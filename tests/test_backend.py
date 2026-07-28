# ruff: noqa: E402

from __future__ import annotations

import os
import threading
import time
from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")

from PySide6.QtCore import QSettings, QThread
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

import sao_francisco.backend as backend_module
from sao_francisco.backend import HELP_ANCHORS, AppBackend
from sao_francisco.core import (
    CancellationToken,
    ChunkSpec,
    JobStatus,
    JobStore,
    Segment,
    Transcript,
)
from sao_francisco.help_system import HelpDocument
from sao_francisco.pipeline import (
    PipelineOptions,
    PipelineProgress,
    PipelineResult,
)


class FakePipeline:
    def __init__(self, root: Path) -> None:
        self.job_store = JobStore(root / "jobs")
        self.output_root = root / "outputs"
        self.started = threading.Event()
        self.release = threading.Event()
        self.block = False
        self.sources: list[str] = []
        self.ran_outside_gui_thread = False

    def list_jobs(self) -> tuple[Any, ...]:
        manifests = []
        for directory in self.job_store.root.iterdir():
            if directory.is_dir():
                manifests.append(self.job_store.load_job(directory.name))
        return tuple(sorted(manifests, key=lambda item: item.updated_at, reverse=True))

    def run(
        self,
        source: str,
        options: PipelineOptions,
        *,
        cancellation: CancellationToken,
        progress: Any,
    ) -> PipelineResult:
        application = QApplication.instance()
        self.ran_outside_gui_thread = (
            application is not None and QThread.currentThread() is not application.thread()
        )
        self.sources.append(source)
        self.started.set()
        while self.block and not self.release.wait(0.01):
            cancellation.raise_if_cancelled()
        cancellation.raise_if_cancelled()

        title = Path(source).name
        manifest = self.job_store.create_job(
            source=source,
            chunks=(ChunkSpec(0, 0, 2),),
            provider=options.provider,
            model=options.model,
            language=options.language,
            settings=options.to_manifest_settings(),
            metadata={
                "source_name": title,
                "provenance": "audio_transcription",
            },
        )
        progress(
            PipelineProgress(
                job_id=manifest.job_id,
                source_name=title,
                state="running",
                detail="Transcrevendo parte 1 de 1…",
                progress=0,
                completed_parts=0,
                total_parts=1,
                provenance="audio_transcription",
            )
        )
        transcript = Transcript(
            segments=(Segment(0, 2, f"texto de {title}"),),
            duration=2,
        )
        manifest = self.job_store.save_chunk_result(
            manifest.job_id,
            0,
            transcript,
        )
        self.output_root.mkdir(parents=True, exist_ok=True)
        output = self.output_root / f"{manifest.job_id}.txt"
        output.write_text(transcript.text, encoding="utf-8")
        manifest = self.job_store.save_job(
            replace(
                manifest,
                status=JobStatus.COMPLETED,
                metadata={
                    **dict(manifest.metadata),
                    "output_paths": [str(output)],
                    "primary_output": str(output),
                },
            )
        )
        return PipelineResult(
            manifest,
            transcript,
            (output,),
            "audio_transcription",
        )

    def resume(
        self,
        job_id: str,
        *,
        cancellation: CancellationToken,
        progress: Any,
    ) -> PipelineResult:
        cancellation.raise_if_cancelled()
        manifest = self.job_store.load_job(job_id)
        return self.run(
            manifest.source,
            PipelineOptions(
                provider=manifest.provider,
                model=manifest.model,
                language=manifest.language,
                formats=("txt",),
                output_folder=self.output_root,
            ),
            cancellation=cancellation,
            progress=progress,
        )


class UncooperativePipeline(FakePipeline):
    """Model an SDK call that does not return after cooperative cancellation."""

    def run(
        self,
        source: str,
        options: PipelineOptions,
        *,
        cancellation: CancellationToken,
        progress: Any,
    ) -> PipelineResult:
        self.sources.append(source)
        self.started.set()
        QThread.msleep(30_000)
        raise AssertionError("o encerramento forçado não interrompeu o worker")


@pytest.fixture(scope="module")
def application() -> QApplication:
    return QApplication.instance() or QApplication([])


@pytest.fixture
def backend(
    tmp_path: Path,
    application: QApplication,
) -> tuple[AppBackend, FakePipeline]:
    pipeline = FakePipeline(tmp_path)
    settings = QSettings(
        str(tmp_path / "settings.ini"),
        QSettings.Format.IniFormat,
    )
    instance = AppBackend(
        pipeline=pipeline,
        qsettings=settings,
        parent=None,
    )
    yield instance, pipeline
    pipeline.release.set()
    assert instance.shutdown()
    application.processEvents()


def wait_until(
    application: QApplication,
    predicate: Any,
    timeout_ms: int = 3_000,
) -> None:
    deadline = time.monotonic() + timeout_ms / 1_000
    while not predicate() and time.monotonic() < deadline:
        application.processEvents()
        QTest.qWait(5)
    assert predicate()


def submission(*sources: Path) -> dict[str, Any]:
    return {
        "sourceType": "files",
        "sources": [str(source) for source in sources],
        "provider": "openai",
        "model": "gpt-4o-mini-transcribe",
        "language": "auto",
        "formats": ["txt"],
        "outputFolder": "",
        "preferExistingCaptions": True,
    }


def test_help_anchor_contract_matches_the_versioned_manual() -> None:
    document = HelpDocument.from_path(
        Path(__file__).resolve().parents[1] / "sao_francisco" / "AJUDA.md"
    )

    assert {section.anchor for section in document.sections} == HELP_ANCHORS
    assert document.first_anchor == "primeiros-passos"


def test_qml_contract_exposes_properties_navigation_and_help(backend) -> None:
    instance, _pipeline = backend

    assert instance.currentRoute == "transcribe"
    assert instance.toggleSidebar() is True
    instance.navigate("settings")
    assert instance.currentRoute == "settings"
    instance.navigate("not-a-route")
    assert instance.currentRoute == "transcribe"
    instance.navigateHelp("formatos-de-saida")
    assert instance.currentRoute == "help"
    assert instance.helpAnchor == "formatos-de-saida"
    assert instance.helpSection("formatos-de-saida")["markdown"].startswith("## Formatos de saída")
    assert instance.modelsForProvider("openai")
    assert instance.modelsForProvider("unknown") == []


def test_transcription_runs_off_gui_thread_and_keeps_navigation_responsive(
    backend,
    application: QApplication,
    tmp_path: Path,
) -> None:
    instance, pipeline = backend
    source = tmp_path / "aula.wav"
    source.write_bytes(b"media")
    pipeline.block = True

    instance.startTranscription(submission(source))
    wait_until(application, pipeline.started.is_set)

    assert instance.busy
    assert pipeline.ran_outside_gui_thread
    instance.navigate("settings")
    assert instance.currentRoute == "settings"

    pipeline.release.set()
    wait_until(application, lambda: not instance.busy)

    assert instance.activeJobState == "completed"
    assert instance.canOpenOutput
    assert instance.history()[0]["state"] == "completed"


def test_multiple_sources_are_processed_by_the_worker_queue(
    backend,
    application: QApplication,
    tmp_path: Path,
) -> None:
    instance, pipeline = backend
    first = tmp_path / "primeira.wav"
    second = tmp_path / "segunda.wav"
    first.write_bytes(b"media")
    second.write_bytes(b"media")

    instance.startTranscription(submission(first, second))
    wait_until(
        application,
        lambda: len(pipeline.sources) == 2 and not instance.busy,
    )

    assert pipeline.sources == [str(first), str(second)]
    assert instance.activeJob["title"] == second.name
    assert len(instance.history()) == 2


def test_cancellation_is_cooperative_and_leaves_the_ui_resumable(
    backend,
    application: QApplication,
    tmp_path: Path,
) -> None:
    instance, pipeline = backend
    source = tmp_path / "longa.wav"
    source.write_bytes(b"media")
    pipeline.block = True

    instance.startTranscription(submission(source))
    wait_until(application, pipeline.started.is_set)
    instance.cancelTranscription()
    wait_until(application, lambda: not instance.busy)

    assert instance.activeJobState == "cancelled"
    assert "retomar" in instance.activeJob["detail"].casefold()


def test_shutdown_never_leaves_an_uncooperative_qthread_running(
    application: QApplication,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    source = tmp_path / "bloqueada.wav"
    source.write_bytes(b"media")
    pipeline = UncooperativePipeline(tmp_path)
    settings = QSettings(
        str(tmp_path / "shutdown-settings.ini"),
        QSettings.Format.IniFormat,
    )
    monkeypatch.setattr(backend_module, "_SHUTDOWN_GRACE_MS", 50)
    instance = AppBackend(pipeline=pipeline, qsettings=settings)

    instance.startTranscription(submission(source))
    wait_until(application, pipeline.started.is_set)
    started_at = time.monotonic()

    assert instance.shutdown()
    assert not instance._worker_thread.isRunning()  # noqa: SLF001
    assert time.monotonic() - started_at < 2


def test_settings_send_secrets_only_to_the_secure_store(
    backend,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    instance, _pipeline = backend
    saved: list[tuple[str, str]] = []
    monkeypatch.setattr(
        backend_module,
        "save_secret",
        lambda provider, secret: saved.append((provider, secret)),
    )
    monkeypatch.setattr(
        backend_module,
        "credential_status",
        lambda provider: {
            "configured": True,
            "source": "cofre de teste",
            "provider": provider,
        },
    )

    assert instance.saveSettings(
        {
            "openAiApiKey": "sk-test-secret",
            "geminiApiKey": "gemini-test-secret",
            "outputFolder": str(tmp_path),
            "rememberWindowGeometry": True,
            "notifyOnCompletion": False,
            "resumeInterruptedJobs": True,
        }
    )

    assert saved == [
        ("openai", "sk-test-secret"),
        ("gemini", "gemini-test-secret"),
    ]
    persisted = {
        key: instance._settings_store.value(key)  # noqa: SLF001
        for key in instance._settings_store.allKeys()  # noqa: SLF001
    }
    assert "sk-test-secret" not in repr(persisted)
    assert "gemini-test-secret" not in repr(persisted)
    assert "sk-test-secret" not in repr(instance.settings)
    assert instance.settings["openAiKeyMasked"].startswith("••••")


def test_unknown_errors_are_redacted_before_reaching_qml() -> None:
    message = backend_module._error_message(  # noqa: SLF001
        RuntimeError("sk-proj-secret https://example.test/?token=secret")
    )
    assert message == "Não foi possível concluir a transcrição."
