from __future__ import annotations

import os
import zipfile
from dataclasses import replace
from importlib.util import find_spec
from pathlib import Path
from typing import Any

import pytest

from sao_francisco.core import (
    CancellationToken,
    ChunkSpec,
    EditorialValidationError,
    JobStatus,
    JobStore,
    MediaInfo,
    MediaProcessor,
    OperationCancelled,
    PreparedChunk,
    PreparedMedia,
    Segment,
    SubtitleAsset,
    SubtitleOrigin,
    Transcript,
    UsageMetrics,
)
from sao_francisco.pipeline import (
    PipelineOptions,
    PipelineValidationError,
    TranscriptionPipeline,
)
from sao_francisco.providers import (
    EditorialRequest,
    EditorialResponse,
    ProviderError,
    ProviderRequest,
)


class FakeMediaProcessor(MediaProcessor):
    def __init__(
        self,
        work_root: Path,
        *,
        subtitle: SubtitleAsset | None = None,
        duration: float = 25.0,
        remote_title: str | None = None,
    ) -> None:
        super().__init__(work_root=work_root)
        self.subtitle = subtitle
        self.duration = duration
        self.remote_title = remote_title
        self.subtitle_attempts = 0
        self.probe_calls = 0
        self.split_indices: list[int] = []

    def resolve_subtitles(self, *_args: object, **_kwargs: object) -> SubtitleAsset | None:
        self.subtitle_attempts += 1
        return self.subtitle

    def probe(self, source: str | Path, **_kwargs: object) -> MediaInfo:
        self.probe_calls += 1
        return MediaInfo(Path(source), self.duration, "fake", 1, 0)

    def detect_silences(self, *_args: object, **_kwargs: object) -> tuple[()]:
        return ()

    def split_audio(
        self,
        source: str | Path,
        chunks: Any,
        *,
        workspace: Any,
        **_kwargs: object,
    ) -> PreparedMedia:
        directory = workspace.path / "chunks"
        directory.mkdir(parents=True, exist_ok=True)
        prepared: list[PreparedChunk] = []
        for chunk in chunks:
            self.split_indices.append(chunk.index)
            path = directory / f"chunk-{chunk.index:06d}.mp3"
            path.write_bytes(b"fake audio")
            prepared.append(PreparedChunk(chunk, path))
        return PreparedMedia(Path(source), workspace, tuple(prepared))

    def download_url(
        self,
        _url: str,
        *,
        workspace: Any,
        **_kwargs: object,
    ) -> tuple[Path, Any]:
        if self.remote_title:
            workspace.metadata["title"] = self.remote_title
        path = workspace.path / "source.mp3"
        path.write_bytes(b"fake remote audio")
        return path, workspace


class FakeProvider:
    provider_id = "openai"

    def __init__(self) -> None:
        self.requests: list[ProviderRequest] = []

    def validate_credential(self) -> None:
        raise AssertionError("credential validation is not part of a transcription run")

    def transcribe(
        self,
        request: ProviderRequest,
        cancellation: CancellationToken,
    ) -> Transcript:
        cancellation.raise_if_cancelled()
        self.requests.append(request)
        index = int(request.audio_path.stem.rsplit("-", 1)[-1])
        return Transcript(
            segments=(
                Segment(
                    0,
                    request.duration,
                    f"conteúdo da parte {index + 1}",
                ),
            ),
            language=request.language or "pt",
            duration=request.duration,
        )


class LeakyProvider(FakeProvider):
    def transcribe(
        self,
        request: ProviderRequest,
        cancellation: CancellationToken,
    ) -> Transcript:
        raise RuntimeError(
            f"sk-proj-secret https://example.test/video?token=secret {request.audio_path}"
        )


class FakeEditorialProvider:
    provider_id = "openai"

    def __init__(self, *, fail_after: int | None = None) -> None:
        self.requests: list[EditorialRequest] = []
        self.fail_after = fail_after

    def improve(
        self,
        request: EditorialRequest,
        cancellation: CancellationToken,
    ) -> EditorialResponse:
        cancellation.raise_if_cancelled()
        self.requests.append(request)
        if self.fail_after is not None and len(self.requests) > self.fail_after:
            raise ProviderError(
                code="test_editorial_failure",
                message="Não foi possível melhorar o texto. O original está preservado.",
                retryable=True,
            )
        return EditorialResponse(
            text=request.text,
            model_id=request.model_id,
            usage=UsageMetrics(
                input_tokens=100,
                output_tokens=80,
                total_tokens=180,
            ),
        )


def options(output: Path, *formats: str) -> PipelineOptions:
    return PipelineOptions(
        provider="openai",
        model="gpt-4o-mini-transcribe",
        formats=tuple(formats or ("txt",)),
        language="pt-BR",
        output_folder=output,
        prefer_existing_captions=True,
    )


def improved_options(output: Path, *formats: str) -> PipelineOptions:
    return PipelineOptions(
        provider="openai",
        model="gpt-4o-mini-transcribe",
        formats=tuple(formats or ("txt",)),
        language="pt-BR",
        output_folder=output,
        improve_with_ai=True,
    )


def test_existing_captions_bypass_credentials_and_export_every_format(tmp_path) -> None:
    media_file = tmp_path / "aula.mp4"
    media_file.write_bytes(b"fake media")
    sidecar = tmp_path / "aula.pt-BR.vtt"
    sidecar.write_text("WEBVTT", encoding="utf-8")
    transcript = Transcript(
        segments=(Segment(1, 3, "Legenda pronta", speaker="Ana"),),
        language="pt-BR",
        duration=4,
    )
    media = FakeMediaProcessor(
        tmp_path / "work",
        subtitle=SubtitleAsset(
            transcript=transcript,
            origin=SubtitleOrigin.SIDECAR,
            path=sidecar,
        ),
    )

    pipeline = TranscriptionPipeline(
        JobStore(tmp_path / "jobs"),
        media=media,
        secret_reader=lambda _provider: pytest.fail("a key must not be read"),
        provider_factory=lambda _provider, _secret: pytest.fail("a provider must not be created"),
    )
    formats = ["txt", "md", "srt", "vtt"]
    if find_spec("docx") is not None:
        formats.append("docx")
    result = pipeline.run(media_file, options(tmp_path / "out", *formats))

    assert result.provenance == "existing_captions"
    assert result.manifest.status == JobStatus.COMPLETED
    assert {path.suffix for path in result.outputs} == {
        f".{output_format}" for output_format in formats
    }
    assert media.probe_calls == 0
    assert media.split_indices == []
    markdown = next(path for path in result.outputs if path.suffix == ".md")
    assert "**Ana:** Legenda pronta" in markdown.read_text(encoding="utf-8")


def test_caption_miss_falls_back_to_chunked_audio_without_paid_validation(tmp_path) -> None:
    media_file = tmp_path / "entrevista.wav"
    media_file.write_bytes(b"fake media")
    media = FakeMediaProcessor(tmp_path / "work", duration=25)
    provider = FakeProvider()
    progress = []
    pipeline = TranscriptionPipeline(
        JobStore(tmp_path / "jobs"),
        media=media,
        secret_reader=lambda provider_id: f"test-key-for-{provider_id}",
        provider_factory=lambda _provider, _secret: provider,
        target_chunk_duration=10,
        chunk_search_window=0,
        chunk_overlap=1,
        minimum_chunk_duration=2,
    )

    result = pipeline.run(
        media_file,
        options(tmp_path / "out", "txt", "md"),
        progress=progress.append,
    )

    assert result.provenance == "audio_transcription"
    assert len(provider.requests) == len(result.manifest.chunks) == 3
    assert media.subtitle_attempts == 1
    assert media.split_indices == [0, 1, 2]
    assert progress[-1].state == "completed"
    assert progress[-1].progress == 1
    assert result.transcript.text.startswith("conteúdo da parte 1")


def test_cancel_then_resume_reuses_saved_chunks(tmp_path) -> None:
    media_file = tmp_path / "reuniao.wav"
    media_file.write_bytes(b"fake media")
    store = JobStore(tmp_path / "jobs")
    first_media = FakeMediaProcessor(tmp_path / "work-first", duration=25)
    first_provider = FakeProvider()
    token = CancellationToken()
    pipeline = TranscriptionPipeline(
        store,
        media=first_media,
        secret_reader=lambda _provider: "test-key",
        provider_factory=lambda _provider, _secret: first_provider,
        target_chunk_duration=10,
        chunk_search_window=0,
        chunk_overlap=1,
        minimum_chunk_duration=2,
    )

    def cancel_after_first(value: Any) -> None:
        if value.completed_parts == 1:
            token.cancel()

    with pytest.raises(OperationCancelled):
        pipeline.run(
            media_file,
            options(tmp_path / "out", "txt"),
            cancellation=token,
            progress=cancel_after_first,
        )

    cancelled = pipeline.list_jobs()[0]
    assert cancelled.status == JobStatus.CANCELLED
    assert cancelled.completed_chunks == frozenset({0})

    resumed_media = FakeMediaProcessor(tmp_path / "work-resumed", duration=25)
    resumed_provider = FakeProvider()
    resumed_pipeline = TranscriptionPipeline(
        store,
        media=resumed_media,
        secret_reader=lambda _provider: "test-key",
        provider_factory=lambda _provider, _secret: resumed_provider,
        target_chunk_duration=10,
        chunk_search_window=0,
        chunk_overlap=1,
        minimum_chunk_duration=2,
    )

    original_stat = media_file.stat()
    media_file.write_bytes(b"changed source")
    with pytest.raises(PipelineValidationError, match="alterada"):
        resumed_pipeline.resume(cancelled.job_id)
    media_file.write_bytes(b"fake media")
    os.utime(
        media_file,
        ns=(original_stat.st_atime_ns, original_stat.st_mtime_ns),
    )
    result = resumed_pipeline.resume(cancelled.job_id)

    assert result.manifest.status == JobStatus.COMPLETED
    assert resumed_media.split_indices == [1, 2]
    assert len(resumed_provider.requests) == 2
    assert result.transcript.text.count("conteúdo da parte 1") == 1


def test_markdown_redacts_remote_query_credentials_and_avoids_overwrite(tmp_path) -> None:
    media = FakeMediaProcessor(tmp_path / "work", duration=4)
    provider = FakeProvider()
    pipeline = TranscriptionPipeline(
        JobStore(tmp_path / "jobs"),
        media=media,
        secret_reader=lambda _provider: "test-key",
        provider_factory=lambda _provider, _secret: provider,
        target_chunk_duration=10,
        minimum_chunk_duration=2,
    )
    remote = "https://user:password@example.com/video?id=123&token=secret#part"

    first = pipeline.run(remote, options(tmp_path / "out", "md"))
    second = pipeline.run(remote, options(tmp_path / "out", "md"))

    assert first.outputs[0] != second.outputs[0]
    exported = first.outputs[0].read_text(encoding="utf-8")
    assert "token=" not in exported
    assert "password" not in exported
    assert "https://example.com/video" in exported


def test_remote_metadata_title_names_the_job_and_output(tmp_path) -> None:
    media = FakeMediaProcessor(
        tmp_path / "work",
        duration=4,
        remote_title="Sessão pública — julho",
    )
    provider = FakeProvider()
    pipeline = TranscriptionPipeline(
        JobStore(tmp_path / "jobs"),
        media=media,
        secret_reader=lambda _provider: "test-key",
        provider_factory=lambda _provider, _secret: provider,
        target_chunk_duration=10,
        minimum_chunk_duration=2,
    )

    result = pipeline.run(
        "https://example.com/watch?v=123",
        options(tmp_path / "out", "txt"),
    )

    assert result.manifest.metadata["source_name"] == "Sessão pública — julho"
    assert result.outputs[0].name == "Sessão pública — julho.txt"


def test_options_reject_unknown_or_cross_provider_models(tmp_path) -> None:
    with pytest.raises(PipelineValidationError, match="não pertence"):
        PipelineOptions(
            provider="gemini",
            model="gpt-4o-mini-transcribe",
            formats=("txt",),
            output_folder=tmp_path,
        )
    with pytest.raises(PipelineValidationError, match="Formato"):
        PipelineOptions(
            provider="openai",
            model="gpt-4o-mini-transcribe",
            formats=("pdf",),
            output_folder=tmp_path,
        )


def test_automatic_language_is_omitted_from_provider_hint(tmp_path) -> None:
    selected = PipelineOptions.from_mapping(
        {
            "provider": "openai",
            "model": "gpt-4o-mini-transcribe",
            "language": "auto",
            "formats": ["txt"],
            "outputFolder": str(tmp_path),
        }
    )

    assert selected.language is None
    assert selected.prefer_existing_captions is False
    assert selected.include_timestamps is False


@pytest.mark.parametrize("include_timestamps", [False, True])
def test_docx_and_txt_timestamps_follow_the_user_option(
    tmp_path,
    include_timestamps: bool,
) -> None:
    media_file = tmp_path / "fala.wav"
    media_file.write_bytes(b"fake media")
    provider = FakeProvider()
    pipeline = TranscriptionPipeline(
        JobStore(tmp_path / "jobs"),
        media=FakeMediaProcessor(tmp_path / "work", duration=4),
        secret_reader=lambda _provider: "test-key",
        provider_factory=lambda _provider, _secret: provider,
        target_chunk_duration=10,
        minimum_chunk_duration=2,
    )
    formats = ("txt", "docx") if find_spec("docx") is not None else ("txt",)
    selected = PipelineOptions(
        provider="openai",
        model="gpt-4o-mini-transcribe",
        formats=formats,
        output_folder=tmp_path / "out",
        include_timestamps=include_timestamps,
    )

    result = pipeline.run(media_file, selected)
    txt = next(path for path in result.outputs if path.suffix == ".txt")
    assert ("[00:00:00]" in txt.read_text(encoding="utf-8")) is include_timestamps

    docx = next((path for path in result.outputs if path.suffix == ".docx"), None)
    if docx is not None:
        with zipfile.ZipFile(docx) as archive:
            document_xml = archive.read("word/document.xml").decode("utf-8")
        assert ("[00:00:00]" in document_xml) is include_timestamps


def test_unknown_provider_errors_are_redacted_in_persisted_state(tmp_path) -> None:
    media_file = tmp_path / "privada.wav"
    media_file.write_bytes(b"fake media")
    store = JobStore(tmp_path / "jobs")
    pipeline = TranscriptionPipeline(
        store,
        media=FakeMediaProcessor(tmp_path / "work", duration=4),
        secret_reader=lambda _provider: "test-key",
        provider_factory=lambda _provider, _secret: LeakyProvider(),
        target_chunk_duration=10,
        minimum_chunk_duration=2,
    )
    progress = []

    with pytest.raises(RuntimeError, match="sk-proj-secret"):
        pipeline.run(
            media_file,
            options(tmp_path / "out", "txt"),
            progress=progress.append,
        )

    manifest = pipeline.list_jobs()[0]
    persisted = str(manifest.metadata.get("status_message"))
    assert "sk-proj-secret" not in persisted
    assert "token=" not in persisted
    assert progress[-1].detail == "A transcrição não pôde ser concluída."


def test_improvement_is_persisted_before_grouped_final_export(tmp_path) -> None:
    media_file = tmp_path / "reuniao.wav"
    media_file.write_bytes(b"fake media")
    transcriber = FakeProvider()
    progress = []
    store = JobStore(tmp_path / "jobs")

    class InspectingEditorialProvider(FakeEditorialProvider):
        original_was_ready = False

        def improve(self, request, cancellation):
            manifest = pipeline.list_jobs()[0]
            original_paths = manifest.metadata["output_groups"]["original"]
            assert manifest.metadata["original_ready"] is True
            assert all(Path(path).is_file() for path in original_paths)
            self.original_was_ready = True
            return super().improve(request, cancellation)

    editor = InspectingEditorialProvider()
    pipeline = TranscriptionPipeline(
        store,
        media=FakeMediaProcessor(tmp_path / "work", duration=4),
        secret_reader=lambda _provider: "test-key",
        provider_factory=lambda _provider, _secret: transcriber,
        editorial_provider_factory=lambda _provider, _secret: editor,
        target_chunk_duration=10,
        minimum_chunk_duration=2,
    )

    result = pipeline.run(
        media_file,
        improved_options(tmp_path / "out", "txt", "srt"),
        progress=progress.append,
    )

    assert len(transcriber.requests) == 1
    assert len(editor.requests) == 1
    assert editor.original_was_ready
    assert result.manifest.metadata["pipeline_stage"] == "completed"
    assert pipeline.job_store.has_original_result(result.manifest.job_id)
    assert pipeline.job_store.has_improved_result(result.manifest.job_id)
    assert [path.name for path in result.output_groups["original"]] == [
        "reuniao — transcrição.txt"
    ]
    assert [path.name for path in result.output_groups["improved"]] == [
        "reuniao — texto melhorado.txt"
    ]
    assert [path.name for path in result.output_groups["captions"]] == ["reuniao.srt"]
    assert result.primary_output == result.output_groups["improved"][0]
    assert not any("texto melhorado" in path.name for path in result.output_groups["captions"])
    details = [item.detail for item in progress]
    assert next(index for index, value in enumerate(details) if "Transcrevendo" in value) < (
        next(index for index, value in enumerate(details) if "Melhorando" in value)
    )
    assert next(index for index, value in enumerate(details) if "Melhorando" in value) < (
        next(index for index, value in enumerate(details) if "Criando" in value)
    )
    summary = result.manifest.metadata["cost_summary"]
    assert int(summary["reported_tokens"]) == 180


def test_editorial_failure_preserves_and_exports_original(tmp_path) -> None:
    media_file = tmp_path / "longa.wav"
    media_file.write_bytes(b"fake media")

    class LongProvider(FakeProvider):
        def transcribe(self, request, cancellation):
            cancellation.raise_if_cancelled()
            self.requests.append(request)
            return Transcript(
                segments=(Segment(0, request.duration, ("texto 27. " * 2_000).strip()),),
                duration=request.duration,
            )

    transcriber = LongProvider()
    failing_editor = FakeEditorialProvider(fail_after=1)
    store = JobStore(tmp_path / "jobs")
    pipeline = TranscriptionPipeline(
        store,
        media=FakeMediaProcessor(tmp_path / "work", duration=4),
        secret_reader=lambda _provider: "test-key",
        provider_factory=lambda _provider, _secret: transcriber,
        editorial_provider_factory=lambda _provider, _secret: failing_editor,
        target_chunk_duration=10,
        minimum_chunk_duration=2,
    )

    with pytest.raises(ProviderError):
        pipeline.run(media_file, improved_options(tmp_path / "out", "txt"))

    failed = pipeline.list_jobs()[0]
    assert failed.metadata["pipeline_stage"] == "improving"
    assert store.has_original_result(failed.job_id)
    assert not store.has_improved_result(failed.job_id)
    original_outputs = failed.metadata["output_groups"]["original"]
    assert [Path(path).name for path in original_outputs] == [
        "longa — transcrição.txt"
    ]
    assert all(Path(path).is_file() for path in original_outputs)
    assert failed.metadata["original_ready"] is True
    assert len(store.load_editorial_results(failed.job_id)) == 1

    resumed_editor = FakeEditorialProvider()
    resumed = TranscriptionPipeline(
        store,
        media=FakeMediaProcessor(tmp_path / "resume-work", duration=4),
        secret_reader=lambda _provider: "test-key",
        provider_factory=lambda *_args: pytest.fail("audio must not be retranscribed"),
        editorial_provider_factory=lambda _provider, _secret: resumed_editor,
        target_chunk_duration=10,
        minimum_chunk_duration=2,
    ).resume(failed.job_id)

    assert resumed.manifest.status == JobStatus.COMPLETED
    assert len(resumed_editor.requests) == 1
    assert resumed.outputs


def test_empty_editorial_response_is_not_reported_as_a_file_error(tmp_path) -> None:
    media_file = tmp_path / "vazia.wav"
    media_file.write_bytes(b"fake media")

    class EmptyEditorialProvider(FakeEditorialProvider):
        def improve(self, request, cancellation):
            response = super().improve(request, cancellation)
            return replace(response, text=" \n ")

    progress = []
    pipeline = TranscriptionPipeline(
        JobStore(tmp_path / "jobs"),
        media=FakeMediaProcessor(tmp_path / "work", duration=4),
        secret_reader=lambda _provider: "test-key",
        provider_factory=lambda _provider, _secret: FakeProvider(),
        editorial_provider_factory=lambda _provider, _secret: EmptyEditorialProvider(),
        target_chunk_duration=10,
        minimum_chunk_duration=2,
    )

    with pytest.raises(EditorialValidationError):
        pipeline.run(
            media_file,
            improved_options(tmp_path / "out", "txt"),
            progress=progress.append,
        )

    failed = pipeline.list_jobs()[0]
    public_message = str(failed.metadata["status_message"])
    assert "arquivo" not in public_message.casefold()
    assert "original" in public_message.casefold()
    assert "arquivo" not in progress[-1].detail.casefold()
    assert failed.metadata["original_ready"] is True


def test_editorial_cancellation_marks_attempt_ambiguous_and_keeps_original(
    tmp_path,
) -> None:
    media_file = tmp_path / "cancelada.wav"
    media_file.write_bytes(b"fake media")

    class CancellingEditorialProvider(FakeEditorialProvider):
        def improve(self, request, cancellation):
            self.requests.append(request)
            cancellation.cancel()
            cancellation.raise_if_cancelled()
            raise AssertionError("cancelamento não foi observado")

    editor = CancellingEditorialProvider()
    pipeline = TranscriptionPipeline(
        JobStore(tmp_path / "jobs"),
        media=FakeMediaProcessor(tmp_path / "work", duration=4),
        secret_reader=lambda _provider: "test-key",
        provider_factory=lambda _provider, _secret: FakeProvider(),
        editorial_provider_factory=lambda _provider, _secret: editor,
        target_chunk_duration=10,
        minimum_chunk_duration=2,
    )

    with pytest.raises(OperationCancelled):
        pipeline.run(media_file, improved_options(tmp_path / "out", "txt"))

    cancelled = pipeline.list_jobs()[0]
    attempts = cancelled.metadata["attempts"]
    assert [attempt["status"] for attempt in attempts] == [
        "accepted",
        "remote_ambiguous",
    ]
    assert cancelled.metadata["remote_result_ambiguous"] is True
    assert cancelled.metadata["original_ready"] is True
    assert all(
        Path(path).is_file()
        for path in cancelled.metadata["output_groups"]["original"]
    )
    assert len(editor.requests) == 1


def test_semantic_differences_are_accepted_without_runtime_rejection(tmp_path) -> None:
    media_file = tmp_path / "entrevista.wav"
    media_file.write_bytes(b"fake media")

    class UnsafeEditorialProvider(FakeEditorialProvider):
        def improve(self, request, cancellation):
            response = super().improve(request, cancellation)
            return replace(response, text=f"{response.text} 28")

    store = JobStore(tmp_path / "jobs")
    pipeline = TranscriptionPipeline(
        store,
        media=FakeMediaProcessor(tmp_path / "work", duration=4),
        secret_reader=lambda _provider: "test-key",
        provider_factory=lambda _provider, _secret: FakeProvider(),
        editorial_provider_factory=lambda _provider, _secret: UnsafeEditorialProvider(),
        target_chunk_duration=10,
        minimum_chunk_duration=2,
    )

    result = pipeline.run(media_file, improved_options(tmp_path / "out", "txt"))

    assert result.manifest.status == JobStatus.COMPLETED
    assert result.improved_text is not None
    assert result.improved_text.endswith("28")
    assert result.manifest.metadata["cost_summary"]["reported_tokens"] == 180
    assert "cost_adjustments" not in result.manifest.metadata
    attempts = result.manifest.metadata["attempts"]
    assert [attempt["status"] for attempt in attempts] == [
        "accepted",
        "accepted",
    ]


def test_interruption_reconciles_saved_result_before_marking_attempt_ambiguous(
    tmp_path,
) -> None:
    media_file = tmp_path / "conciliada.wav"
    media_file.write_bytes(b"fake media")
    store = JobStore(tmp_path / "jobs")
    pipeline = TranscriptionPipeline(
        store,
        media=FakeMediaProcessor(tmp_path / "work", duration=4),
        secret_reader=lambda _provider: "test-key",
        provider_factory=lambda _provider, _secret: FakeProvider(),
        editorial_provider_factory=lambda _provider, _secret: FakeEditorialProvider(),
        target_chunk_duration=10,
        minimum_chunk_duration=2,
    )
    result = pipeline.run(
        media_file,
        improved_options(tmp_path / "out", "txt"),
    )
    attempts = [dict(item) for item in result.manifest.metadata["attempts"]]
    editorial_attempt = next(
        item for item in attempts if item["stage"] == "improvement"
    )
    editorial_attempt.update(status="running", finished_at=None)
    metadata = {
        **dict(result.manifest.metadata),
        "pipeline_stage": "improving",
        "attempts": attempts,
        "active_attempt_id": editorial_attempt["attempt_id"],
    }
    interrupted = store.save_job(
        replace(result.manifest, status=JobStatus.RUNNING, metadata=metadata)
    )

    paused = pipeline.mark_interrupted(interrupted.job_id)

    reconciled = next(
        item
        for item in paused.metadata["attempts"]
        if item["attempt_id"] == editorial_attempt["attempt_id"]
    )
    assert reconciled["status"] == "accepted"
    assert reconciled["remote_result_ambiguous"] is False
    assert paused.status == JobStatus.PAUSED
    assert paused.metadata.get("remote_result_ambiguous") is not True


def test_forced_cancel_persists_request_before_marking_remote_ambiguous(
    tmp_path,
) -> None:
    store = JobStore(tmp_path / "jobs")
    pipeline = TranscriptionPipeline(store)
    manifest = store.create_job(
        source="https://example.test/video",
        chunks=(ChunkSpec(0, 0, 5),),
        provider="openai",
        model="gpt-4o-mini-transcribe",
        settings={"formats": ["txt"], "improve_with_ai": False},
    )
    manifest = store.set_status(manifest.job_id, JobStatus.RUNNING)
    manifest, _attempt_id = pipeline._start_remote_attempt(  # noqa: SLF001
        manifest,
        stage="transcription",
        unit_id="chunk-0",
        provider="openai",
        model="gpt-4o-mini-transcribe",
    )

    requested = pipeline.request_cancel(manifest.job_id)

    assert requested.metadata["cancellation_state"] == "cancel_requested"
    assert requested.metadata["attempts"][0]["status"] == "cancel_requested"

    cancelled = pipeline.mark_stalled_cancelled(manifest.job_id)

    assert cancelled.status == JobStatus.CANCELLED
    assert cancelled.metadata["cancellation_state"] == "cancelled"
    assert cancelled.metadata["attempts"][0]["status"] == "remote_ambiguous"
    assert cancelled.metadata["remote_result_ambiguous"] is True


def test_export_retry_does_not_repeat_paid_stages(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    media_file = tmp_path / "entrevista.wav"
    media_file.write_bytes(b"fake media")
    transcriber = FakeProvider()
    editor = FakeEditorialProvider()
    pipeline = TranscriptionPipeline(
        JobStore(tmp_path / "jobs"),
        media=FakeMediaProcessor(tmp_path / "work", duration=4),
        secret_reader=lambda _provider: "test-key",
        provider_factory=lambda _provider, _secret: transcriber,
        editorial_provider_factory=lambda _provider, _secret: editor,
        target_chunk_duration=10,
        minimum_chunk_duration=2,
    )
    real_export = pipeline._export_improved  # noqa: SLF001

    def fail_export(*_args, **_kwargs):
        raise OSError("falha simulada")

    monkeypatch.setattr(pipeline, "_export_improved", fail_export)
    with pytest.raises(OSError):
        pipeline.run(media_file, improved_options(tmp_path / "out", "txt"))

    failed = pipeline.list_jobs()[0]
    before = dict(failed.metadata["cost_summary"])
    assert failed.metadata["pipeline_stage"] == "improved_export_failed"
    assert failed.metadata["original_ready"] is True
    assert all(
        Path(path).is_file()
        for path in failed.metadata["output_groups"]["original"]
    )
    assert len(transcriber.requests) == len(editor.requests) == 1

    monkeypatch.setattr(pipeline, "_export_improved", real_export)
    result = pipeline.resume(failed.job_id)

    assert result.manifest.status == JobStatus.COMPLETED
    assert len(transcriber.requests) == len(editor.requests) == 1
    assert dict(result.manifest.metadata["cost_summary"]) == before


def test_existing_captions_without_improvement_are_proven_free(tmp_path) -> None:
    media_file = tmp_path / "aula.mp4"
    media_file.write_bytes(b"fake media")
    transcript = Transcript(
        segments=(Segment(0, 3, "Legenda pronta."),),
        duration=3,
    )
    media = FakeMediaProcessor(
        tmp_path / "work",
        subtitle=SubtitleAsset(
            transcript=transcript,
            origin=SubtitleOrigin.URL_MANUAL,
            path=tmp_path / "aula.pt.vtt",
        ),
    )
    pipeline = TranscriptionPipeline(
        JobStore(tmp_path / "jobs"),
        media=media,
        secret_reader=lambda _provider: pytest.fail("no key is needed"),
    )

    result = pipeline.run(media_file, options(tmp_path / "out", "txt"))

    summary = result.manifest.metadata["cost_summary"]
    assert summary["proven_zero"] is True
    assert summary["usd"] == "0"
