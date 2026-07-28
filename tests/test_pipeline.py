from __future__ import annotations

import os
from importlib.util import find_spec
from pathlib import Path
from typing import Any

import pytest

from sao_francisco.core import (
    CancellationToken,
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
)
from sao_francisco.pipeline import (
    PipelineOptions,
    PipelineValidationError,
    TranscriptionPipeline,
)
from sao_francisco.providers import ProviderRequest


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


def options(output: Path, *formats: str) -> PipelineOptions:
    return PipelineOptions(
        provider="openai",
        model="gpt-4o-mini-transcribe",
        formats=tuple(formats or ("txt",)),
        language="pt-BR",
        output_folder=output,
        prefer_existing_captions=True,
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
