"""Qt-facing application adapter.

Production media and provider work runs in a disposable child process. This
object owns GUI state, validation, queueing, safe credential hand-off, and
conversion between Python models and QML maps. Injected test pipelines retain
the legacy thread executor so small unit fakes remain straightforward.
"""

from __future__ import annotations

import uuid
from collections import deque
from collections.abc import Mapping
from contextlib import suppress
from dataclasses import dataclass
from datetime import datetime
from multiprocessing import get_context
from pathlib import Path
from queue import Empty
from time import monotonic
from typing import Any
from urllib.parse import urlparse

from PySide6.QtCore import (
    Property,
    QObject,
    QSettings,
    QStandardPaths,
    Qt,
    QThread,
    QTimer,
    QUrl,
    Signal,
    Slot,
)
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QFileDialog

from . import __version__
from .catalog import model_by_id, models_for_provider
from .core import (
    CancellationToken,
    JobManifest,
    JobNotFoundError,
    JobStatus,
    JobStore,
    JobStoreError,
    MediaDependencyError,
    MediaProcessor,
    OperationCancelled,
    format_cost_label,
    format_usage_label,
)
from .credentials import (
    CredentialError,
    credential_status,
    read_secret,
    save_secret,
)
from .help_system import HelpContentError, HelpDocument
from .pipeline import (
    PipelineError,
    PipelineOptions,
    PipelineProgress,
    PipelineResult,
    PipelineValidationError,
    TranscriptionPipeline,
    overall_progress,
)
from .process_worker import PipelineProcessConfig, run_pipeline_process
from .providers import ProviderError, provider_for

ROUTES = frozenset({"transcribe", "history", "settings", "help", "about"})
HELP_ANCHORS = frozenset(
    {
        "primeiros-passos",
        "adicionar-arquivo-video-ou-url",
        "escolher-um-modelo",
        "chaves-da-openai-e-do-gemini",
        "como-midias-longas-sao-processadas",
        "acompanhar-cancelar-e-retomar",
        "formatos-de-saida",
        "custos-dados-e-armazenamento",
        "problemas-comuns",
        "atalhos-e-navegacao",
        "licencas-e-sobre",
    }
)
_SHUTDOWN_GRACE_MS = 5_000
_CANCEL_GRACE_MS = 5_000
_PROCESS_KILL_GRACE_MS = 1_000
_PROCESS_POLL_MS = 25


@dataclass(frozen=True, slots=True)
class _QueuedTask:
    key: str
    source: str
    title: str
    options: PipelineOptions | None = None
    resume_job_id: str | None = None
    cancellation: CancellationToken | None = None


@dataclass(frozen=True, slots=True)
class _CredentialTest:
    provider: str
    candidate: str


class _PipelineWorker(QObject):
    progress = Signal(str, object)
    succeeded = Signal(str, object)
    failed = Signal(str, str)
    cancelled = Signal(str)
    credentialFinished = Signal(str, bool, str)

    def __init__(self, pipeline: TranscriptionPipeline) -> None:
        super().__init__()
        self._pipeline = pipeline

    @Slot(object)
    def run_task(self, task: _QueuedTask) -> None:
        token = task.cancellation or CancellationToken()

        def report(value: PipelineProgress) -> None:
            self.progress.emit(task.key, value.to_ui_dict())

        try:
            if task.resume_job_id:
                result = self._pipeline.resume(
                    task.resume_job_id,
                    cancellation=token,
                    progress=report,
                )
            else:
                if task.options is None:
                    raise PipelineValidationError("As opções do trabalho estão ausentes.")
                result = self._pipeline.run(
                    task.source,
                    task.options,
                    cancellation=token,
                    progress=report,
                )
        except OperationCancelled:
            self.cancelled.emit(task.key)
        except BaseException as exc:
            self.failed.emit(task.key, _error_message(exc))
        else:
            self.succeeded.emit(task.key, result)

    @Slot(object)
    def test_credential(self, request: _CredentialTest) -> None:
        try:
            provider_for(request.provider, request.candidate).validate_credential()
        except BaseException as exc:
            self.credentialFinished.emit(
                request.provider,
                False,
                _error_message(exc),
            )
        else:
            self.credentialFinished.emit(
                request.provider,
                True,
                "Chave válida.",
            )


class _ProcessExecutor(QObject):
    """Own one disposable child process without blocking the Qt event loop."""

    progress = Signal(str, object)
    succeeded = Signal(str, str)
    failed = Signal(str, str)
    cancelled = Signal(str, str)
    forcedCancelled = Signal(str, str)

    def __init__(
        self,
        config: PipelineProcessConfig,
        *,
        context: Any | None = None,
        target: Any = run_pipeline_process,
        cancel_grace_ms: int = _CANCEL_GRACE_MS,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._config = config
        self._context = context or get_context("spawn")
        self._target = target
        self._cancel_grace_ms = max(0, int(cancel_grace_ms))
        self._process: Any | None = None
        self._message_queue: Any | None = None
        self._cancel_event: Any | None = None
        self._task_key = ""
        self._last_job_id = ""
        self._terminal: dict[str, Any] | None = None
        self._cancel_deadline: float | None = None
        self._kill_deadline: float | None = None
        self._forced = False
        self._timer = QTimer(self)
        self._timer.setInterval(_PROCESS_POLL_MS)
        self._timer.timeout.connect(self._poll)

    @property
    def running(self) -> bool:
        return self._process is not None

    def start(self, task: _QueuedTask) -> None:
        if self.running:
            raise RuntimeError("Já existe um processo de transcrição ativo.")
        raw_options: dict[str, Any] | None = None
        if task.options is not None:
            raw_options = {
                "provider": task.options.provider,
                "model": task.options.model,
                "language": task.options.language or "",
                **task.options.to_manifest_settings(),
            }
        raw_task = {
            "key": task.key,
            "source": task.source,
            "resume_job_id": task.resume_job_id or "",
            "options": raw_options,
        }
        self._message_queue = self._context.Queue()
        self._cancel_event = self._context.Event()
        self._task_key = task.key
        self._last_job_id = task.resume_job_id or ""
        self._terminal = None
        self._cancel_deadline = None
        self._kill_deadline = None
        self._forced = False
        self._process = self._context.Process(
            target=self._target,
            args=(
                raw_task,
                self._config.to_mapping(),
                self._message_queue,
                self._cancel_event,
            ),
            name="sao-francisco-pipeline",
            daemon=True,
        )
        try:
            self._process.start()
        except BaseException:
            self._cleanup()
            raise
        self._timer.start()

    def cancel(self) -> bool:
        if not self.running or self._cancel_event is None:
            return False
        self._cancel_event.set()
        if self._cancel_deadline is None:
            self._cancel_deadline = monotonic() + self._cancel_grace_ms / 1_000
        return True

    def shutdown(self) -> None:
        """Stop the child within a fixed bound while the app is closing."""

        process = self._process
        if process is None:
            return
        if self._cancel_event is not None:
            self._cancel_event.set()
        process.join(timeout=_SHUTDOWN_GRACE_MS / 1_000)
        if process.is_alive():
            process.terminate()
            process.join(timeout=_PROCESS_KILL_GRACE_MS / 1_000)
        if process.is_alive() and hasattr(process, "kill"):
            process.kill()
            process.join(timeout=_PROCESS_KILL_GRACE_MS / 1_000)
        self._cleanup()

    @Slot()
    def _poll(self) -> None:
        process = self._process
        if process is None:
            return
        self._drain_messages()
        now = monotonic()
        if (
            self._cancel_deadline is not None
            and now >= self._cancel_deadline
            and not self._forced
            and process.is_alive()
        ):
            process.terminate()
            self._forced = True
            self._terminal = {
                "kind": "forced_cancelled",
                "key": self._task_key,
                "job_id": self._last_job_id,
            }
            self._kill_deadline = now + _PROCESS_KILL_GRACE_MS / 1_000
        if (
            self._forced
            and self._kill_deadline is not None
            and now >= self._kill_deadline
            and process.is_alive()
            and hasattr(process, "kill")
        ):
            process.kill()
            self._kill_deadline = now + _PROCESS_KILL_GRACE_MS / 1_000

        if process.is_alive():
            return
        process.join(timeout=0)
        self._drain_messages()
        terminal = self._terminal or {
            "kind": (
                "forced_cancelled"
                if self._cancel_deadline is not None
                else "failed"
            ),
            "key": self._task_key,
            "job_id": self._last_job_id,
            "message": "O processo de transcrição terminou inesperadamente.",
        }
        self._emit_terminal(terminal)

    def _drain_messages(self) -> None:
        if self._message_queue is None:
            return
        while True:
            try:
                message = self._message_queue.get_nowait()
            except (Empty, EOFError, OSError):
                return
            if not isinstance(message, Mapping):
                continue
            value = dict(message)
            job_id = str(value.get("job_id") or "")
            if job_id:
                self._last_job_id = job_id
            if value.get("kind") == "progress":
                payload = value.get("payload")
                if isinstance(payload, Mapping):
                    self.progress.emit(self._task_key, dict(payload))
                continue
            self._terminal = value

    def _emit_terminal(self, terminal: Mapping[str, Any]) -> None:
        key = str(terminal.get("key") or self._task_key)
        job_id = str(terminal.get("job_id") or self._last_job_id)
        kind = str(terminal.get("kind") or "failed")
        message = str(
            terminal.get("message")
            or "O processo de transcrição terminou inesperadamente."
        )
        self._cleanup()
        if kind == "succeeded":
            self.succeeded.emit(key, job_id)
        elif kind == "cancelled":
            self.cancelled.emit(key, job_id)
        elif kind == "forced_cancelled":
            self.forcedCancelled.emit(key, job_id)
        else:
            self.failed.emit(key, message)

    def _cleanup(self) -> None:
        self._timer.stop()
        if self._message_queue is not None:
            with suppress(OSError, ValueError):
                self._message_queue.close()
        self._process = None
        self._message_queue = None
        self._cancel_event = None
        self._task_key = ""
        self._last_job_id = ""
        self._terminal = None
        self._cancel_deadline = None
        self._kill_deadline = None
        self._forced = False


class AppBackend(QObject):
    """Implementation of ``qml/BACKEND_CONTRACT.md``."""

    currentRouteChanged = Signal()
    sidebarCollapsedChanged = Signal()
    busyChanged = Signal()
    appVersionChanged = Signal()
    activeJobStateChanged = Signal()
    canOpenOutputChanged = Signal()
    activeJobChanged = Signal()
    pendingSourcesChanged = Signal()
    outputFolderChanged = Signal()
    historyItemsChanged = Signal()
    settingsChanged = Signal()
    helpAnchorChanged = Signal()
    helpContentChanged = Signal()

    historyChanged = Signal()
    toastRequested = Signal(str)
    apiKeyTestFinished = Signal(str, bool, str)

    _runRequested = Signal(object)
    _credentialTestRequested = Signal(object)

    def __init__(
        self,
        *,
        pipeline: TranscriptionPipeline | None = None,
        qsettings: QSettings | None = None,
        help_document: HelpDocument | None = None,
        data_root: str | Path | None = None,
        default_output_root: str | Path | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._current_route = "transcribe"
        self._sidebar_collapsed = False
        self._busy = False
        self._active_job: dict[str, Any] = {}
        self._pending_sources: list[str] = []
        self._history_items: list[dict[str, Any]] = []
        self._queue: deque[_QueuedTask] = deque()
        self._current_task: _QueuedTask | None = None
        self._resume_confirmations: set[str] = set()
        self._shutting_down = False

        self._settings_store = qsettings if qsettings is not None else QSettings()
        self._output_folder = str(
            self._settings_store.value("preferences/outputFolder", "", type=str)
        )

        self._help_error = ""
        self._help: HelpDocument | None
        if help_document is not None:
            self._help = help_document
        else:
            try:
                self._help = HelpDocument.from_path(Path(__file__).with_name("AJUDA.md"))
            except HelpContentError as exc:
                self._help = None
                self._help_error = str(exc)
        self._help_anchor = (
            "primeiros-passos"
            if self._help and self._help.has_anchor("primeiros-passos")
            else (self._help.first_anchor if self._help else "primeiros-passos")
        )

        self._uses_process_executor = pipeline is None
        self._pipeline = pipeline or self._default_pipeline(
            data_root=data_root,
            default_output_root=default_output_root,
        )
        self._process_executor: _ProcessExecutor | None = None
        if self._uses_process_executor:
            media_root = self._pipeline.media.work_root
            if media_root is None:
                media_root = self._pipeline.job_store.root.parent / "cache" / "media"
            self._process_executor = _ProcessExecutor(
                PipelineProcessConfig(
                    job_root=self._pipeline.job_store.root,
                    media_work_root=media_root,
                    default_output_root=self._pipeline.default_output_root,
                ),
                parent=self,
            )
            self._process_executor.progress.connect(self._on_progress)
            self._process_executor.succeeded.connect(self._on_process_success)
            self._process_executor.failed.connect(self._on_failure)
            self._process_executor.cancelled.connect(self._on_process_cancelled)
            self._process_executor.forcedCancelled.connect(
                self._on_forced_process_cancelled
            )

        self._worker_thread = QThread()
        self._worker_thread.setObjectName(
            "credential-worker"
            if self._uses_process_executor
            else "transcription-worker"
        )
        self._worker = _PipelineWorker(self._pipeline)
        self._worker.moveToThread(self._worker_thread)
        if not self._uses_process_executor:
            self._runRequested.connect(
                self._worker.run_task,
                Qt.ConnectionType.QueuedConnection,
            )
        self._credentialTestRequested.connect(
            self._worker.test_credential,
            Qt.ConnectionType.QueuedConnection,
        )
        self._worker.progress.connect(self._on_progress)
        self._worker.succeeded.connect(self._on_success)
        self._worker.failed.connect(self._on_failure)
        self._worker.cancelled.connect(self._on_cancelled)
        self._worker.credentialFinished.connect(self._on_credential_finished)
        self._worker_thread.finished.connect(self._worker.deleteLater)
        self._worker_thread.start()

        interrupted = self._recover_interrupted_jobs()
        self._refresh_history()
        if interrupted and self._preference_bool("resumeInterruptedJobs", True):
            QTimer.singleShot(0, lambda: self._auto_resume(interrupted))

    @Property(str, notify=currentRouteChanged)
    def currentRoute(self) -> str:  # noqa: N802 - public QML contract
        return self._current_route

    @Property(bool, notify=sidebarCollapsedChanged)
    def sidebarCollapsed(self) -> bool:  # noqa: N802
        return self._sidebar_collapsed

    @Property(bool, notify=busyChanged)
    def busy(self) -> bool:
        return self._busy

    @Property(str, constant=True)
    def appVersion(self) -> str:  # noqa: N802
        return __version__

    @Property(str, constant=True)
    def thirdPartyNoticesMarkdown(self) -> str:  # noqa: N802
        package = Path(__file__).resolve().parent
        candidates = (
            package / "THIRD_PARTY_NOTICES.md",
            package.parent / "THIRD_PARTY_NOTICES.md",
        )
        target = next((path for path in candidates if path.is_file()), None)
        if target is None:
            return "# Avisos de terceiros\n\nOs avisos não foram encontrados neste pacote."
        try:
            return target.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            return "# Avisos de terceiros\n\nOs avisos não puderam ser lidos."

    @Property(str, notify=activeJobStateChanged)
    def activeJobState(self) -> str:  # noqa: N802
        return str(self._active_job.get("state", ""))

    @Property(bool, notify=canOpenOutputChanged)
    def canOpenOutput(self) -> bool:  # noqa: N802
        return self._active_output() is not None

    @Property("QVariantMap", notify=activeJobChanged)
    def activeJob(self) -> dict[str, Any]:  # noqa: N802
        return dict(self._active_job)

    @Property("QVariantList", notify=pendingSourcesChanged)
    def pendingSources(self) -> list[str]:  # noqa: N802
        return list(self._pending_sources)

    @Property(str, notify=outputFolderChanged)
    def outputFolder(self) -> str:  # noqa: N802
        return self._output_folder

    @Property("QVariantList", notify=historyItemsChanged)
    def historyItems(self) -> list[dict[str, Any]]:  # noqa: N802
        return [dict(item) for item in self._history_items]

    @Property("QVariantMap", notify=settingsChanged)
    def settings(self) -> dict[str, Any]:
        return self._settings_map()

    @Property(str, notify=helpAnchorChanged)
    def helpAnchor(self) -> str:  # noqa: N802
        return self._help_anchor

    @Slot(str)
    def navigate(self, route: str) -> None:
        selected = route.strip().casefold()
        if selected not in ROUTES:
            selected = "transcribe"
        if selected != self._current_route:
            self._current_route = selected
            self.currentRouteChanged.emit()

    @Slot(result=bool)
    def toggleSidebar(self) -> bool:  # noqa: N802
        self.setSidebarCollapsed(not self._sidebar_collapsed)
        return self._sidebar_collapsed

    @Slot(bool)
    def setSidebarCollapsed(self, collapsed: bool) -> None:  # noqa: N802
        selected = bool(collapsed)
        if selected != self._sidebar_collapsed:
            self._sidebar_collapsed = selected
            self.sidebarCollapsedChanged.emit()

    @Slot(str)
    def navigateHelp(self, anchor: str) -> None:  # noqa: N802
        selected = anchor.strip().casefold()
        if (
            selected not in HELP_ANCHORS
            or self._help is None
            or not self._help.has_anchor(selected)
        ):
            selected = "primeiros-passos"
        if selected != self._help_anchor:
            self._help_anchor = selected
            self.helpAnchorChanged.emit()
        self.navigate("help")

    @Slot(str)
    def openExternalUrl(self, url: str) -> None:  # noqa: N802
        destination = QUrl(url)
        if destination.scheme().casefold() != "https" or not destination.host():
            self.toastRequested.emit("Este endereço não pode ser aberto com segurança.")
            return
        if not QDesktopServices.openUrl(destination):
            self.toastRequested.emit("Não foi possível abrir o endereço.")

    @Slot(str, result="QVariantList")
    def modelsForProvider(self, provider_id: str) -> list[dict[str, Any]]:  # noqa: N802
        selected = provider_id.strip().casefold()
        if selected not in {"openai", "gemini"}:
            return []
        models = (
            models_for_provider("openai")
            if selected == "openai"
            else models_for_provider("gemini")
        )
        return [item.to_ui_dict() for item in models]

    @Slot("QVariantList")
    def setPendingSources(self, urls: list[Any]) -> None:  # noqa: N802
        normalized: list[str] = []
        for raw in urls:
            try:
                source = _local_source(str(raw))
            except PipelineValidationError:
                continue
            if source not in normalized:
                normalized.append(source)
        if normalized != self._pending_sources:
            self._pending_sources = normalized
            self.pendingSourcesChanged.emit()

    @Slot(result=str)
    def chooseOutputFolder(self) -> str:  # noqa: N802
        selected = QFileDialog.getExistingDirectory(
            None,
            "Escolher pasta de saída",
            self._output_folder or _documents_location(),
        )
        if selected and selected != self._output_folder:
            self._output_folder = selected
            self.outputFolderChanged.emit()
        return selected

    @Slot("QVariantMap")
    def startTranscription(self, values: dict[str, Any]) -> None:  # noqa: N802
        try:
            options, sources = self._validated_submission(values)
        except PipelineValidationError as exc:
            self.toastRequested.emit(str(exc))
            return

        for source in sources:
            self._enqueue(
                _QueuedTask(
                    key=uuid.uuid4().hex,
                    source=source,
                    title=_display_source(source),
                    options=options,
                )
            )
        if self._pending_sources:
            self._pending_sources = []
            self.pendingSourcesChanged.emit()

    @Slot()
    def cancelTranscription(self) -> None:  # noqa: N802
        cleared = len(self._queue)
        self._queue.clear()
        if self._current_task:
            if self.activeJobState == "cancelling":
                return
            job_id = _durable_job_id(
                self._active_job,
                self._current_task.resume_job_id,
                self._current_task.key,
            )
            if job_id:
                request_cancel = getattr(self._pipeline, "request_cancel", None)
                if callable(request_cancel):
                    with suppress(JobStoreError, OSError, ValueError):
                        request_cancel(job_id)
            if self._process_executor is not None:
                self._process_executor.cancel()
            elif self._current_task.cancellation:
                self._current_task.cancellation.cancel()
            active = dict(self._active_job)
            active.update(
                state="cancelling",
                detail=(
                    "Cancelando; preservando a transcrição e as partes concluídas…"
                ),
            )
            self._set_active_job(active)
        elif self._active_job.get("state") == "queued":
            active = dict(self._active_job)
            active.update(
                state="cancelled",
                detail="Cancelada antes de iniciar.",
            )
            self._set_active_job(active)
            self._set_busy(False)
        if cleared:
            self.toastRequested.emit("Os itens que ainda estavam na fila foram removidos.")

    @Slot()
    def openActiveOutput(self) -> None:  # noqa: N802
        output = self._active_output()
        if output is None or not _open_local_path(output):
            self.toastRequested.emit("O resultado não está disponível neste computador.")

    @Slot(str)
    def openOutputPath(self, raw_path: str) -> None:  # noqa: N802
        path = Path(raw_path).expanduser()
        if not path.is_file() or not _open_local_path(path):
            self.toastRequested.emit("Este arquivo não está disponível neste computador.")

    @Slot()
    def revealActiveOutput(self) -> None:  # noqa: N802
        output = self._active_output()
        if output is None or not _open_local_path(output.parent):
            self.toastRequested.emit("A pasta do resultado não está disponível.")

    @Slot(result="QVariantList")
    def history(self) -> list[dict[str, Any]]:
        self._refresh_history()
        return [dict(item) for item in self._history_items]

    @Slot(str)
    def openHistoryOutput(self, job_id: str) -> None:  # noqa: N802
        try:
            manifest = self._pipeline.job_store.load_job(job_id)
        except (JobNotFoundError, ValueError):
            self.toastRequested.emit("Este item não existe mais no histórico.")
            return
        output = _manifest_output(manifest)
        if output is None or not _open_local_path(output):
            self.toastRequested.emit("O arquivo de resultado não foi encontrado.")

    @Slot(str)
    def resumeTranscription(self, job_id: str) -> None:  # noqa: N802
        if self._task_is_known(job_id):
            self.toastRequested.emit("Este trabalho já está na fila.")
            return
        try:
            manifest = self._pipeline.job_store.load_job(job_id)
        except (JobNotFoundError, ValueError):
            self.toastRequested.emit("Este item não existe mais no histórico.")
            return
        if manifest.status == JobStatus.COMPLETED and _manifest_output(manifest):
            self.openHistoryOutput(job_id)
            return
        if _requires_paid_retry_confirmation(manifest):
            if job_id not in self._resume_confirmations:
                self._resume_confirmations.add(job_id)
                self.toastRequested.emit(
                    "A tentativa anterior pode ter sido cobrada. "
                    "Clique em Retomar novamente para confirmar uma nova chamada."
                )
                return
            self._resume_confirmations.discard(job_id)
        self._enqueue(
            _QueuedTask(
                key=uuid.uuid4().hex,
                source=manifest.source,
                title=str(
                    manifest.metadata.get("source_name") or _display_source(manifest.source)
                ),
                resume_job_id=manifest.job_id,
            )
        )

    @Slot(str)
    def showHistoryDetails(self, job_id: str) -> None:  # noqa: N802
        try:
            manifest = self._pipeline.job_store.load_job(job_id)
        except (JobNotFoundError, ValueError):
            self.toastRequested.emit("Este item não existe mais no histórico.")
            return
        detail = _manifest_to_ui(manifest)
        total_parts = len(manifest.chunks)
        parts_label = (
            "parte concluída" if total_parts == 1 else "partes concluídas"
        )
        detail["detail"] = str(
            manifest.metadata.get("status_message")
            or (
                f"{len(manifest.completed_chunks)} de {total_parts} "
                f"{parts_label}."
            )
        )
        detail["focusDetails"] = True
        self._set_active_job(detail)
        self.navigate("transcribe")

    @Slot("QVariantMap", result=bool)
    def saveSettings(self, values: dict[str, Any]) -> bool:  # noqa: N802
        try:
            output = str(values.get("outputFolder", "")).strip()
            output_path = Path(output).expanduser() if output else None
            if output_path and output_path.exists() and not output_path.is_dir():
                raise PipelineValidationError("A pasta de saída não é uma pasta.")

            openai_key = str(values.get("openAiApiKey", "")).strip()
            gemini_key = str(values.get("geminiApiKey", "")).strip()
            if openai_key:
                save_secret("openai", openai_key)
            if gemini_key:
                save_secret("gemini", gemini_key)

            self._settings_store.setValue("preferences/outputFolder", output)
            self._settings_store.setValue(
                "preferences/notifyOnCompletion",
                bool(values.get("notifyOnCompletion", True)),
            )
            self._settings_store.setValue(
                "preferences/resumeInterruptedJobs",
                bool(values.get("resumeInterruptedJobs", True)),
            )
            self._settings_store.sync()
            if self._settings_store.status() != QSettings.Status.NoError:
                raise PipelineError("As preferências não puderam ser gravadas.")
        except (CredentialError, OSError, PipelineError) as exc:
            self.toastRequested.emit(_error_message(exc))
            return False

        if output != self._output_folder:
            self._output_folder = output
            self.outputFolderChanged.emit()
        self.settingsChanged.emit()
        return True

    @Slot(str, str, result="QVariant")
    def testApiKey(self, provider: str, candidate: str) -> None | str:  # noqa: N802
        selected = provider.strip().casefold()
        if selected not in {"openai", "gemini"}:
            return "Provedor desconhecido."
        try:
            secret = candidate.strip() or read_secret(selected)
        except CredentialError:
            return "A chave não pôde ser lida no cofre seguro."
        if not secret:
            return "Nenhuma chave foi informada."
        self._credentialTestRequested.emit(_CredentialTest(selected, secret))
        return None

    @Slot(str, result="QVariantList")
    def searchHelp(self, query: str) -> list[dict[str, str]]:  # noqa: N802
        if self._help is None:
            return []
        return [
            result for result in self._help.search(query) if result.get("anchor") in HELP_ANCHORS
        ]

    @Slot(str, result="QVariantMap")
    def helpSection(self, anchor: str) -> dict[str, str]:  # noqa: N802
        if self._help is None:
            return {
                "title": "Ajuda indisponível",
                "anchor": "primeiros-passos",
                "markdown": f"## Ajuda indisponível\n\n{self._help_error}",
            }
        selected = anchor if self._help.has_anchor(anchor) else "primeiros-passos"
        section = self._help.section(selected)
        return {
            "title": section.title,
            "anchor": section.anchor,
            "markdown": section.markdown,
        }

    @Slot(result=bool)
    def shutdown(self) -> bool:
        """Stop every worker without leaving a live Qt thread behind.

        Production pipeline work has its own disposable process. The Qt thread
        only hosts credential validation and the injected executor used by unit
        tests; terminating it remains an application-shutdown fallback.
        """

        if self._shutting_down:
            process_stopped = (
                self._process_executor is None
                or not self._process_executor.running
            )
            return process_stopped and not self._worker_thread.isRunning()
        self._shutting_down = True
        self._queue.clear()
        if self._current_task and self._current_task.cancellation:
            self._current_task.cancellation.cancel()
        if self._process_executor is not None:
            self._process_executor.shutdown()
        self._worker_thread.requestInterruption()
        self._worker_thread.quit()
        if self._worker_thread.wait(_SHUTDOWN_GRACE_MS):
            return True
        self._worker_thread.terminate()
        # ``shutdown`` is called only while the application itself is closing.
        # Once the cooperative grace period expires, wait for forced termination
        # rather than ever letting Qt destroy a live QThread.
        return self._worker_thread.wait()

    def _default_pipeline(
        self,
        *,
        data_root: str | Path | None,
        default_output_root: str | Path | None,
    ) -> TranscriptionPipeline:
        root = Path(data_root) if data_root else Path(_app_data_location())
        cache_value = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.CacheLocation
        )
        cache = Path(cache_value) if cache_value else root / "cache"
        return TranscriptionPipeline(
            JobStore(root / "jobs"),
            media=MediaProcessor(work_root=cache / "media"),
            default_output_root=default_output_root or _documents_location(),
        )

    def _validated_submission(
        self, values: dict[str, Any]
    ) -> tuple[PipelineOptions, tuple[str, ...]]:
        source_type = str(values.get("sourceType", "")).strip().casefold()
        if source_type not in {"files", "url"}:
            raise PipelineValidationError("Escolha arquivos ou um endereço.")
        raw_sources = values.get("sources", ())
        if not isinstance(raw_sources, (list, tuple)) or not raw_sources:
            raise PipelineValidationError("Adicione uma fonte para transcrever.")

        sources: list[str] = []
        for raw in raw_sources:
            text = str(raw).strip()
            source = _remote_source(text) if source_type == "url" else _local_source(text)
            if source not in sources:
                sources.append(source)

        raw_options = dict(values)
        output = str(raw_options.get("outputFolder", "")).strip()
        if not output:
            raw_options["outputFolder"] = self._output_folder
        options = PipelineOptions.from_mapping(raw_options)
        return options, tuple(sources)

    def _enqueue(self, task: _QueuedTask) -> None:
        task = _QueuedTask(
            key=task.key,
            source=task.source,
            title=task.title,
            options=task.options,
            resume_job_id=task.resume_job_id,
            cancellation=CancellationToken(),
        )
        self._queue.append(task)
        self._set_busy(True)
        if self._current_task is None:
            self._set_active_job(
                {
                    "id": task.resume_job_id or task.key,
                    "title": task.title,
                    "sourceName": task.title,
                    "state": "queued",
                    "detail": "Na fila para iniciar.",
                    "progress": 0.0,
                    "completedParts": 0,
                    "totalParts": 0,
                    "provenance": "",
                }
            )
            QTimer.singleShot(0, self._start_next)
        else:
            self.toastRequested.emit(f"Adicionado à fila ({len(self._queue)} aguardando).")

    @Slot()
    def _start_next(self) -> None:
        if self._shutting_down or self._current_task is not None:
            return
        if not self._queue:
            self._set_busy(False)
            return
        self._current_task = self._queue.popleft()
        task = self._current_task
        self._set_active_job(
            {
                "id": task.resume_job_id or task.key,
                "title": task.title,
                "sourceName": task.title,
                "state": "preparing",
                "detail": "Preparando a fonte…",
                "progress": 0.0,
                "completedParts": 0,
                "totalParts": 0,
                "provenance": "",
            }
        )
        if self._process_executor is not None:
            try:
                self._process_executor.start(task)
            except BaseException as exc:
                self._on_failure(task.key, _error_message(exc))
        else:
            self._runRequested.emit(task)

    @Slot(str, object)
    def _on_progress(self, key: str, value: dict[str, Any]) -> None:
        if self._current_task is None or key != self._current_task.key:
            return
        snapshot = dict(value)
        snapshot["id"] = (
            snapshot.get("id") or self._current_task.resume_job_id or self._current_task.key
        )
        job_id = _durable_job_id(
            snapshot,
            self._current_task.resume_job_id,
            self._current_task.key,
        )
        if job_id:
            try:
                item = _manifest_to_ui(self._pipeline.job_store.load_job(job_id))
            except (JobStoreError, OSError, ValueError):
                item = {}
            item.update(snapshot)
            snapshot = item
        if self.activeJobState == "cancelling":
            snapshot.update(
                state="cancelling",
                detail=(
                    "Cancelando; preservando a transcrição e as partes concluídas…"
                ),
            )
        self._set_active_job(snapshot)
        self._refresh_history()

    @Slot(str, object)
    def _on_success(self, key: str, result: PipelineResult) -> None:
        if self._current_task is None or key != self._current_task.key:
            return
        item = _manifest_to_ui(result.manifest)
        item.update(
            state="completed",
            detail="Concluída; os arquivos estão prontos.",
            outputPaths=[str(path) for path in result.outputs],
            outputGroups={
                key: [str(path) for path in paths]
                for key, paths in result.output_groups.items()
            },
            primaryOutput=str(result.primary_output or ""),
        )
        self._set_active_job(item)
        if self._preference_bool("notifyOnCompletion", True):
            self.toastRequested.emit(f"“{item['title']}” foi concluída.")
        self._finish_current()

    @Slot(str, str)
    def _on_process_success(self, key: str, job_id: str) -> None:
        if self._current_task is None or key != self._current_task.key:
            return
        try:
            result = self._pipeline.load_result(job_id)
        except BaseException as exc:
            self._on_failure(key, _error_message(exc))
            return
        self._on_success(key, result)

    @Slot(str, str)
    def _on_failure(self, key: str, message: str) -> None:
        if self._current_task is None or key != self._current_task.key:
            return
        item = self._current_manifest_item()
        original_ready = bool(item.get("originalReady"))
        detail = (
            f"Transcrição pronta; a melhoria não foi concluída. {message}"
            if original_ready
            else message
        )
        item.update(state="failed", detail=detail)
        self._set_active_job(item)
        self.toastRequested.emit(detail)
        self._finish_current()

    @Slot(str)
    def _on_cancelled(self, key: str) -> None:
        if self._current_task is None or key != self._current_task.key:
            return
        item = self._current_manifest_item()
        original_ready = bool(item.get("originalReady"))
        item.update(
            state="cancelled",
            detail=(
                "Cancelada; a transcrição original está pronta. "
                "Você pode retomar a melhoria pelo Histórico."
                if original_ready
                else "Cancelada; você pode retomar pelo Histórico."
            ),
        )
        self._set_active_job(item)
        self._finish_current()

    @Slot(str, str)
    def _on_process_cancelled(self, key: str, _job_id: str) -> None:
        self._on_cancelled(key)

    @Slot(str, str)
    def _on_forced_process_cancelled(self, key: str, job_id: str) -> None:
        if self._current_task is None or key != self._current_task.key:
            return
        if job_id:
            with suppress(JobStoreError, OSError, ValueError):
                self._pipeline.mark_stalled_cancelled(job_id)
        self._on_cancelled(key)

    @Slot(str, bool, str)
    def _on_credential_finished(
        self,
        provider: str,
        ok: bool,
        message: str,
    ) -> None:
        self.apiKeyTestFinished.emit(provider, ok, message)

    def _finish_current(self) -> None:
        self._current_task = None
        self._refresh_history()
        if self._queue:
            QTimer.singleShot(0, self._start_next)
        else:
            self._set_busy(False)

    def _current_manifest_item(self) -> dict[str, Any]:
        item = dict(self._active_job)
        if self._current_task is None:
            return item
        job_id = _durable_job_id(
            item,
            self._current_task.resume_job_id,
            self._current_task.key,
        )
        if not job_id:
            return item
        try:
            persisted = _manifest_to_ui(self._pipeline.job_store.load_job(job_id))
        except (JobStoreError, OSError, ValueError):
            return item
        persisted.update(
            {
                key: value
                for key, value in item.items()
                if key not in {"outputPaths", "outputGroups", "primaryOutput"}
            }
        )
        return persisted

    def _set_active_job(self, value: dict[str, Any]) -> None:
        previous_state = self.activeJobState
        previous_open = self.canOpenOutput
        if value != self._active_job:
            self._active_job = dict(value)
            self.activeJobChanged.emit()
        if self.activeJobState != previous_state:
            self.activeJobStateChanged.emit()
        if self.canOpenOutput != previous_open:
            self.canOpenOutputChanged.emit()

    def _set_busy(self, value: bool) -> None:
        if bool(value) != self._busy:
            self._busy = bool(value)
            self.busyChanged.emit()

    def _active_output(self) -> Path | None:
        raw = str(self._active_job.get("primaryOutput") or "")
        if raw:
            path = Path(raw)
            if path.is_file():
                return path
        for value in self._active_job.get("outputPaths", ()):
            path = Path(str(value))
            if path.is_file():
                return path
        return None

    def _refresh_history(self) -> None:
        items = [_manifest_to_ui(manifest) for manifest in self._pipeline.list_jobs()]
        if items != self._history_items:
            self._history_items = items
            self.historyItemsChanged.emit()
            self.historyChanged.emit()

    def _recover_interrupted_jobs(self) -> tuple[str, ...]:
        safe_to_auto_resume: list[str] = []
        for manifest in self._pipeline.list_jobs():
            if manifest.status not in {JobStatus.PENDING, JobStatus.RUNNING}:
                continue
            if manifest.status == JobStatus.PENDING:
                self._pipeline.job_store.set_status(
                    manifest.job_id,
                    JobStatus.PAUSED,
                    message="Interrompida antes de iniciar.",
                )
                safe_to_auto_resume.append(manifest.job_id)
            else:
                self._pipeline.mark_interrupted(manifest.job_id)
        return tuple(safe_to_auto_resume)

    def _auto_resume(self, job_ids: tuple[str, ...]) -> None:
        for job_id in reversed(job_ids):
            self.resumeTranscription(job_id)

    def _task_is_known(self, job_id: str) -> bool:
        if self._current_task and self._current_task.resume_job_id == job_id:
            return True
        return any(task.resume_job_id == job_id for task in self._queue)

    def _preference_bool(self, key: str, default: bool) -> bool:
        return bool(
            self._settings_store.value(
                f"preferences/{key}",
                default,
                type=bool,
            )
        )

    def _settings_map(self) -> dict[str, Any]:
        return {
            "openAiKeyMasked": _masked_credential("openai"),
            "geminiKeyMasked": _masked_credential("gemini"),
            "outputFolder": self._output_folder,
            "notifyOnCompletion": self._preference_bool("notifyOnCompletion", True),
            "resumeInterruptedJobs": self._preference_bool("resumeInterruptedJobs", True),
        }


def _manifest_to_ui(manifest: JobManifest) -> dict[str, Any]:
    try:
        model_label = model_by_id(manifest.model).name
    except KeyError:
        model_label = manifest.model
    provider_label = "OpenAI" if manifest.provider == "openai" else "Gemini"
    output_paths = [
        str(path)
        for path in manifest.metadata.get("output_paths", ())
        if Path(str(path)).is_file()
    ]
    primary = str(manifest.metadata.get("primary_output") or "")
    raw_groups = manifest.metadata.get("output_groups")
    output_groups: dict[str, list[str]] = {}
    if isinstance(raw_groups, Mapping):
        for key in ("improved", "original", "captions"):
            output_groups[key] = [
                str(path)
                for path in raw_groups.get(key, ())
                if Path(str(path)).is_file()
            ]
    raw_summary = manifest.metadata.get("cost_summary")
    summary = raw_summary if isinstance(raw_summary, Mapping) else {}
    if not summary or (
        summary.get("usd") is None and not summary.get("proven_zero")
    ):
        raw_forecast = manifest.metadata.get("cost_forecast")
        if isinstance(raw_forecast, Mapping):
            summary = raw_forecast
    state = _ui_status(manifest.status)
    stage = str(manifest.metadata.get("pipeline_stage") or "")
    original_ready = bool(manifest.metadata.get("original_ready")) and bool(
        output_groups.get("original") or output_groups.get("captions")
    )
    improved_ready = bool(output_groups.get("improved"))
    if not bool(manifest.settings.get("improve_with_ai", False)):
        improvement_state = "not_requested"
    elif improved_ready:
        improvement_state = "ready"
    elif stage == "improving":
        improvement_state = "in_progress"
    else:
        improvement_state = "not_completed"
    return {
        "id": manifest.job_id,
        "title": str(manifest.metadata.get("source_name") or _display_source(manifest.source)),
        "sourceName": str(
            manifest.metadata.get("source_name") or _display_source(manifest.source)
        ),
        "createdAt": manifest.created_at,
        "createdAtLabel": _date_label(manifest.created_at),
        "provider": manifest.provider,
        "providerLabel": provider_label,
        "model": manifest.model,
        "modelLabel": model_label,
        "state": state,
        "stage": stage,
        "progress": overall_progress(manifest, stage),
        "completedParts": len(manifest.completed_chunks),
        "totalParts": len(manifest.chunks),
        "provenance": str(manifest.metadata.get("provenance") or ""),
        "outputPaths": output_paths,
        "outputGroups": output_groups,
        "primaryOutput": primary if Path(primary).is_file() else "",
        "originalReady": original_ready,
        "improvementState": improvement_state,
        "remoteResultAmbiguous": bool(
            manifest.metadata.get("remote_result_ambiguous")
        ),
        "costLabel": format_cost_label(
            summary,
            in_progress=state not in {"completed", "failed", "cancelled", "paused"},
        ),
        "usageLabel": format_usage_label(summary),
        "improveWithAi": bool(manifest.settings.get("improve_with_ai", False)),
    }


def _ui_status(status: JobStatus) -> str:
    if status == JobStatus.PENDING:
        return "queued"
    return status.value


def _manifest_output(manifest: JobManifest) -> Path | None:
    primary = str(manifest.metadata.get("primary_output") or "")
    if primary and Path(primary).is_file():
        return Path(primary)
    for raw in manifest.metadata.get("output_paths", ()):
        path = Path(str(raw))
        if path.is_file():
            return path
    return None


def _durable_job_id(
    item: Mapping[str, Any],
    resume_job_id: str | None,
    transient_key: str,
) -> str:
    candidate = str(item.get("id") or resume_job_id or "")
    return candidate if candidate and candidate != transient_key else ""


def _requires_paid_retry_confirmation(manifest: JobManifest) -> bool:
    if bool(manifest.metadata.get("remote_result_ambiguous")):
        return True
    raw_attempts = manifest.metadata.get("attempts", ())
    if isinstance(raw_attempts, (list, tuple)) and any(
        isinstance(item, Mapping)
        and item.get("status") in {
            "remote_ambiguous",
            "rejected",
            "cancel_requested",
            "running",
        }
        for item in raw_attempts
    ):
        return True
    raw_adjustments = manifest.metadata.get("cost_adjustments", ())
    return isinstance(raw_adjustments, (list, tuple)) and any(
        isinstance(item, Mapping) for item in raw_adjustments
    )


def _local_source(value: str) -> str:
    url = QUrl(value)
    if url.scheme().casefold() == "file":
        if not url.isLocalFile():
            raise PipelineValidationError("O endereço de arquivo local é inválido.")
        value = url.toLocalFile()
    elif url.scheme():
        raise PipelineValidationError("Escolha um arquivo local.")
    path = Path(value).expanduser().resolve()
    if not path.is_file():
        raise PipelineValidationError(f"O arquivo selecionado não existe: {path.name}.")
    return str(path)


def _remote_source(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise PipelineValidationError("Informe um endereço HTTP(S) válido.")
    return value


def _display_source(source: str) -> str:
    parsed = urlparse(source)
    if parsed.scheme in {"http", "https"}:
        return Path(parsed.path).name or parsed.netloc
    return Path(source).name


def _masked_credential(provider: str) -> str:
    try:
        status = credential_status(provider)
    except CredentialError:
        return ""
    if not status.get("configured"):
        return ""
    source = str(status.get("source") or "")
    return f"•••••••• — {source}" if source else "••••••••"


def _date_label(value: str) -> str:
    try:
        parsed = datetime.fromisoformat(value).astimezone()
    except ValueError:
        return value
    return parsed.strftime("%d/%m/%Y %H:%M")


def _error_message(exc: BaseException) -> str:
    if isinstance(exc, ProviderError):
        return exc.message
    if isinstance(exc, MediaDependencyError):
        return (
            "Não foi possível preparar esta mídia. Atualize o São Francisco "
            "e tente novamente."
        )
    if isinstance(exc, (CredentialError, PipelineError)):
        return str(exc)
    if isinstance(exc, OSError):
        return "O sistema não conseguiu acessar um arquivo necessário."
    return "Não foi possível concluir a transcrição."


def _open_local_path(path: Path) -> bool:
    resolved = path.expanduser().resolve()
    if not resolved.exists():
        return False
    return bool(QDesktopServices.openUrl(QUrl.fromLocalFile(str(resolved))))


def _documents_location() -> str:
    value = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)
    return value or str(Path.home() / "Documents")


def _app_data_location() -> str:
    value = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
    return value or str(Path.home() / ".sao-francisco")


__all__ = ["AppBackend", "HELP_ANCHORS", "ROUTES"]
