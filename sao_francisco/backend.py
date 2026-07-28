"""Qt-facing application adapter.

All expensive media and provider work is dispatched to ``_PipelineWorker`` in a
dedicated ``QThread``.  This object owns only GUI state, validation, queueing,
safe credential hand-off, and conversion between Python models and QML maps.
"""

from __future__ import annotations

import uuid
from collections import deque
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
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
    MediaDependencyError,
    MediaProcessor,
    OperationCancelled,
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
)
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

        self._pipeline = pipeline or self._default_pipeline(
            data_root=data_root,
            default_output_root=default_output_root,
        )
        self._worker_thread = QThread()
        self._worker_thread.setObjectName("transcription-worker")
        self._worker = _PipelineWorker(self._pipeline)
        self._worker.moveToThread(self._worker_thread)
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
        if self._current_task and self._current_task.cancellation:
            self._current_task.cancellation.cancel()
            active = dict(self._active_job)
            active["detail"] = "Cancelamento solicitado; preservando as partes concluídas…"
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
                "preferences/rememberWindowGeometry",
                bool(values.get("rememberWindowGeometry", True)),
            )
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

    @Slot()
    def openThirdPartyNotices(self) -> None:  # noqa: N802
        package = Path(__file__).resolve().parent
        candidates = (
            package / "THIRD_PARTY_NOTICES.md",
            package.parent / "THIRD_PARTY_NOTICES.md",
            package / "licenses",
        )
        target = next((path for path in candidates if path.exists()), None)
        if target is None or not _open_local_path(target):
            self.toastRequested.emit("Os avisos de terceiros não foram encontrados.")

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
        """Stop the worker, forcing it only as a bounded process-exit fallback.

        Provider SDKs cannot always interrupt an HTTP request already in flight.
        Cooperative cancellation gets five seconds; ``terminate`` is reserved
        for application shutdown so a live ``QThread`` is never destroyed.
        Atomic core writes keep a forced exit resumable.
        """

        if self._shutting_down:
            return not self._worker_thread.isRunning()
        self._shutting_down = True
        self._queue.clear()
        if self._current_task and self._current_task.cancellation:
            self._current_task.cancellation.cancel()
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
        self._runRequested.emit(task)

    @Slot(str, object)
    def _on_progress(self, key: str, value: dict[str, Any]) -> None:
        if self._current_task is None or key != self._current_task.key:
            return
        snapshot = dict(value)
        snapshot["id"] = (
            snapshot.get("id") or self._current_task.resume_job_id or self._current_task.key
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
            primaryOutput=str(result.primary_output or ""),
        )
        self._set_active_job(item)
        if self._preference_bool("notifyOnCompletion", True):
            self.toastRequested.emit(f"“{item['title']}” foi concluída.")
        self._finish_current()

    @Slot(str, str)
    def _on_failure(self, key: str, message: str) -> None:
        if self._current_task is None or key != self._current_task.key:
            return
        item = dict(self._active_job)
        item.update(state="failed", detail=message)
        self._set_active_job(item)
        self.toastRequested.emit(message)
        self._finish_current()

    @Slot(str)
    def _on_cancelled(self, key: str) -> None:
        if self._current_task is None or key != self._current_task.key:
            return
        item = dict(self._active_job)
        item.update(
            state="cancelled",
            detail="Cancelada; você pode retomar pelo Histórico.",
        )
        self._set_active_job(item)
        self._finish_current()

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
        interrupted: list[str] = []
        for manifest in self._pipeline.list_jobs():
            if manifest.status not in {JobStatus.PENDING, JobStatus.RUNNING}:
                continue
            self._pipeline.job_store.set_status(
                manifest.job_id,
                JobStatus.PAUSED,
                message="Interrompida quando o aplicativo foi fechado.",
            )
            interrupted.append(manifest.job_id)
        return tuple(interrupted)

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
            "rememberWindowGeometry": self._preference_bool("rememberWindowGeometry", True),
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
        "state": _ui_status(manifest.status),
        "progress": manifest.progress,
        "completedParts": len(manifest.completed_chunks),
        "totalParts": len(manifest.chunks),
        "provenance": str(manifest.metadata.get("provenance") or ""),
        "outputPaths": output_paths,
        "primaryOutput": primary if Path(primary).is_file() else "",
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
        return "Instale FFmpeg, ffprobe e yt-dlp para preparar esta mídia."
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
