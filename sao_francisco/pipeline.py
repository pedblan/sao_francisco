"""Application-level orchestration for resumable media transcription.

The core package deliberately has no opinion about GUI state or providers.  This
module joins those pieces while remaining synchronous and Qt-free: callers run a
pipeline in a worker thread, receive progress snapshots, and can cancel through
the shared :class:`~sao_francisco.core.CancellationToken`.
"""

from __future__ import annotations

import os
import re
import tempfile
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

from .catalog import model_by_id
from .core import (
    CancellationToken,
    ChunkSpec,
    ExportError,
    JobManifest,
    JobStatus,
    JobStore,
    JobStoreError,
    MediaDependencyError,
    MediaError,
    MediaProcessor,
    OperationCancelled,
    SubtitleAsset,
    SubtitleError,
    SubtitleOrigin,
    Transcript,
    assemble_chunks,
    export_transcript,
    format_timestamp,
    plan_chunks,
)
from .credentials import CredentialError, read_secret
from .providers import (
    ProviderError,
    ProviderRequest,
    TranscriptionProvider,
    provider_for,
)

SUPPORTED_FORMATS = frozenset({"docx", "md", "srt", "txt", "vtt"})
_LANGUAGE_RE = re.compile(r"^[A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8})*$")
_UNSAFE_FILENAME_RE = re.compile(r"[\x00-\x1f<>:\"/\\|?*]+")

ProgressCallback = Callable[["PipelineProgress"], None]
ProviderFactory = Callable[[str, str], TranscriptionProvider]
SecretReader = Callable[[str], str | None]


class PipelineError(RuntimeError):
    """A user-facing failure in application orchestration."""


class PipelineValidationError(PipelineError, ValueError):
    """Input cannot safely be submitted to the pipeline."""


@dataclass(frozen=True, slots=True)
class PipelineOptions:
    """Stable options persisted with each resumable job."""

    provider: str
    model: str
    formats: tuple[str, ...]
    language: str | None = None
    output_folder: Path | None = None
    prefer_existing_captions: bool = True

    def __post_init__(self) -> None:
        provider = self.provider.strip().casefold()
        if provider not in {"openai", "gemini"}:
            raise PipelineValidationError("Escolha OpenAI ou Gemini.")

        model = self.model.strip()
        try:
            catalog_model = model_by_id(model)
        except KeyError as exc:
            raise PipelineValidationError(
                "O modelo de transcrição não existe no catálogo."
            ) from exc
        if catalog_model.provider != provider:
            raise PipelineValidationError("O modelo escolhido não pertence ao provedor.")

        formats = tuple(dict.fromkeys(item.strip().casefold() for item in self.formats))
        if not formats:
            raise PipelineValidationError("Escolha ao menos um formato de saída.")
        unsupported = sorted(set(formats) - SUPPORTED_FORMATS)
        if unsupported:
            raise PipelineValidationError(
                f"Formato de saída não suportado: {', '.join(unsupported)}."
            )

        language = self.language.strip() if self.language else None
        if language and language.casefold() == "auto":
            language = None
        if language and not _LANGUAGE_RE.fullmatch(language):
            raise PipelineValidationError("O código de idioma não é válido.")

        folder = Path(self.output_folder).expanduser() if self.output_folder else None
        object.__setattr__(self, "provider", provider)
        object.__setattr__(self, "model", model)
        object.__setattr__(self, "formats", formats)
        object.__setattr__(self, "language", language)
        object.__setattr__(self, "output_folder", folder)
        object.__setattr__(self, "prefer_existing_captions", bool(self.prefer_existing_captions))

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> PipelineOptions:
        raw_formats = value.get("formats", ())
        if isinstance(raw_formats, str) or not isinstance(raw_formats, Sequence):
            raise PipelineValidationError("A lista de formatos é inválida.")
        raw_folder = value.get("outputFolder", value.get("output_folder"))
        return cls(
            provider=str(value.get("provider", "")),
            model=str(value.get("model", "")),
            language=_optional_text(value.get("language")),
            formats=tuple(str(item) for item in raw_formats),
            output_folder=Path(str(raw_folder)) if _optional_text(raw_folder) else None,
            prefer_existing_captions=_as_bool(
                value.get(
                    "preferExistingCaptions",
                    value.get("prefer_existing_captions", True),
                )
            ),
        )

    def to_manifest_settings(self) -> dict[str, Any]:
        """Return JSON-safe settings; credentials are intentionally absent."""

        return {
            "formats": list(self.formats),
            "output_folder": str(self.output_folder) if self.output_folder else "",
            "prefer_existing_captions": self.prefer_existing_captions,
        }


@dataclass(frozen=True, slots=True)
class PipelineProgress:
    """One immutable progress snapshot suitable for a Qt ``QVariantMap``."""

    job_id: str
    source_name: str
    state: str
    detail: str
    progress: float
    completed_parts: int
    total_parts: int
    provenance: str = ""

    def to_ui_dict(self) -> dict[str, Any]:
        return {
            "id": self.job_id,
            "title": self.source_name,
            "sourceName": self.source_name,
            "state": self.state,
            "detail": self.detail,
            "progress": min(1.0, max(0.0, float(self.progress))),
            "completedParts": self.completed_parts,
            "totalParts": self.total_parts,
            "provenance": self.provenance,
        }


@dataclass(frozen=True, slots=True)
class PipelineResult:
    manifest: JobManifest
    transcript: Transcript
    outputs: tuple[Path, ...]
    provenance: str

    @property
    def primary_output(self) -> Path | None:
        preferred = ("docx", "md", "txt", "srt", "vtt")
        by_suffix = {path.suffix.casefold().lstrip("."): path for path in self.outputs}
        return next((by_suffix[item] for item in preferred if item in by_suffix), None)


class TranscriptionPipeline:
    """Run and resume one source at a time.

    The class is thread-compatible, not internally concurrent.  A backend may
    queue calls onto one worker thread while the :class:`JobStore` keeps each
    completed provider response crash-safe.
    """

    def __init__(
        self,
        job_store: JobStore,
        *,
        media: MediaProcessor | None = None,
        provider_factory: ProviderFactory = provider_for,
        secret_reader: SecretReader = read_secret,
        default_output_root: str | os.PathLike[str] | None = None,
        target_chunk_duration: float = 600.0,
        chunk_search_window: float = 30.0,
        chunk_overlap: float = 2.0,
        minimum_chunk_duration: float = 15.0,
    ) -> None:
        self.job_store = job_store
        self.media = media or MediaProcessor()
        self.provider_factory = provider_factory
        self.secret_reader = secret_reader
        self.default_output_root = (
            Path(default_output_root).expanduser()
            if default_output_root is not None
            else self.job_store.root.parent / "exports"
        )
        self.target_chunk_duration = target_chunk_duration
        self.chunk_search_window = chunk_search_window
        self.chunk_overlap = chunk_overlap
        self.minimum_chunk_duration = minimum_chunk_duration

    def run(
        self,
        source: str | os.PathLike[str],
        options: PipelineOptions | Mapping[str, Any],
        *,
        cancellation: CancellationToken | None = None,
        progress: ProgressCallback | None = None,
    ) -> PipelineResult:
        """Create and execute a resumable job for one local file or URL."""

        selected = (
            options
            if isinstance(options, PipelineOptions)
            else PipelineOptions.from_mapping(options)
        )
        token = cancellation or CancellationToken()
        source_text = self._validated_source(source)
        source_name = _source_name(source_text)
        manifest: JobManifest | None = None

        self._report(
            progress,
            PipelineProgress(
                job_id="",
                source_name=source_name,
                state="preparing",
                detail=(
                    "Verificando a fonte e as legendas disponíveis…"
                    if selected.prefer_existing_captions
                    else "Verificando a fonte…"
                ),
                progress=0.0,
                completed_parts=0,
                total_parts=0,
            ),
        )

        try:
            token.raise_if_cancelled()
            with self.media.create_workspace(source_name) as workspace:
                subtitle: SubtitleAsset | None = None
                if selected.prefer_existing_captions:
                    try:
                        subtitle = self.media.resolve_subtitles(
                            source_text,
                            prefer_existing_subtitles=True,
                            language=selected.language,
                            workspace=workspace,
                            fallback_to_audio=True,
                            allow_automatic=True,
                            cancel_token=token,
                        )
                    except OperationCancelled:
                        raise
                    except (MediaError, OSError, SubtitleError, UnicodeError, ValueError):
                        # Existing captions are an optimization, never a hard
                        # requirement.  Audio is the documented fallback.
                        subtitle = None

                if subtitle is not None:
                    source_name = _workspace_source_name(workspace, source_name)
                    provenance = _subtitle_provenance(subtitle.origin)
                    duration = max(float(subtitle.transcript.duration or 0.0), 0.001)
                    manifest = self._create_manifest(
                        source_text,
                        selected,
                        chunks=(ChunkSpec(0, 0.0, duration),),
                        source_name=source_name,
                        provenance=provenance,
                        extra_metadata={"subtitle_origin": subtitle.origin.value},
                    )
                    manifest = self.job_store.save_chunk_result(
                        manifest.job_id, 0, subtitle.transcript
                    )
                    self._report_manifest(
                        progress,
                        manifest,
                        source_name,
                        "running",
                        "Legenda existente encontrada; preparando os arquivos…",
                        provenance,
                    )
                    return self._finalize(
                        manifest,
                        selected,
                        subtitle.transcript,
                        provenance,
                        token,
                        progress,
                    )

                if selected.prefer_existing_captions:
                    fallback_detail = (
                        "Nenhuma legenda compatível; obtendo a mídia para transcrever o áudio…"
                        if _is_http_url(source_text)
                        else "Nenhuma legenda compatível; analisando o áudio da mídia…"
                    )
                else:
                    fallback_detail = (
                        "Obtendo a mídia para transcrever o áudio…"
                        if _is_http_url(source_text)
                        else "Analisando o áudio da mídia…"
                    )
                self._report(
                    progress,
                    PipelineProgress(
                        job_id="",
                        source_name=source_name,
                        state="preparing",
                        detail=fallback_detail,
                        progress=0.0,
                        completed_parts=0,
                        total_parts=0,
                    ),
                )
                local_source = self._prepare_local_source(
                    source_text, workspace=workspace, cancellation=token
                )
                source_name = _workspace_source_name(workspace, source_name)
                self._report(
                    progress,
                    PipelineProgress(
                        job_id="",
                        source_name=source_name,
                        state="preparing",
                        detail="Medindo a duração e procurando pausas naturais…",
                        progress=0.0,
                        completed_parts=0,
                        total_parts=0,
                    ),
                )
                info = self.media.probe(local_source, cancel_token=token)
                silences = self.media.detect_silences(
                    local_source,
                    media_duration=info.duration,
                    cancel_token=token,
                )
                chunks = plan_chunks(
                    info.duration,
                    silences,
                    target_duration=self.target_chunk_duration,
                    search_window=self.chunk_search_window,
                    overlap=self.chunk_overlap,
                    min_duration=self.minimum_chunk_duration,
                )
                manifest = self._create_manifest(
                    source_text,
                    selected,
                    chunks=chunks,
                    source_name=source_name,
                    provenance="audio_transcription",
                    extra_metadata={
                        "media_duration": info.duration,
                        "media_format": info.format_name or "",
                    },
                )
                return self._transcribe_and_finalize(
                    manifest,
                    selected,
                    local_source,
                    workspace,
                    token,
                    progress,
                )
        except OperationCancelled:
            if manifest is not None:
                manifest = self.job_store.set_status(
                    manifest.job_id,
                    JobStatus.CANCELLED,
                    message="Cancelada; as partes concluídas foram preservadas.",
                )
                self._report_manifest(
                    progress,
                    manifest,
                    source_name,
                    "cancelled",
                    "Cancelada; você pode retomar pelo Histórico.",
                    str(manifest.metadata.get("provenance", "")),
                )
            raise
        except BaseException as exc:
            if manifest is not None:
                manifest = self._mark_failed(manifest, exc)
                self._report_manifest(
                    progress,
                    manifest,
                    source_name,
                    "failed",
                    _public_error(exc),
                    str(manifest.metadata.get("provenance", "")),
                )
            raise

    def resume(
        self,
        job_id: str,
        *,
        cancellation: CancellationToken | None = None,
        progress: ProgressCallback | None = None,
    ) -> PipelineResult:
        """Resume only missing parts, then regenerate the requested outputs."""

        token = cancellation or CancellationToken()
        manifest = self.job_store.load_job(job_id)
        options = self._options_from_manifest(manifest)
        source_name = str(manifest.metadata.get("source_name") or _source_name(manifest.source))
        provenance = str(manifest.metadata.get("provenance") or "audio_transcription")

        try:
            token.raise_if_cancelled()
            if not manifest.pending_chunks:
                transcript = assemble_chunks(
                    manifest.chunks,
                    self.job_store.load_completed_results(job_id),
                )
                return self._finalize(
                    manifest,
                    options,
                    transcript,
                    provenance,
                    token,
                    progress,
                )

            with self.media.create_workspace(source_name) as workspace:
                self._validate_resume_source(manifest)
                if provenance != "audio_transcription":
                    subtitle = self.media.resolve_subtitles(
                        manifest.source,
                        prefer_existing_subtitles=True,
                        language=manifest.language,
                        workspace=workspace,
                        fallback_to_audio=False,
                        allow_automatic=True,
                        cancel_token=token,
                    )
                    if subtitle is None:
                        raise PipelineError(
                            "A legenda original não está mais disponível para retomada."
                        )
                    manifest = self.job_store.save_chunk_result(
                        job_id, manifest.pending_chunks[0].index, subtitle.transcript
                    )
                    return self._finalize(
                        manifest,
                        options,
                        subtitle.transcript,
                        provenance,
                        token,
                        progress,
                    )

                local_source = self._prepare_local_source(
                    manifest.source, workspace=workspace, cancellation=token
                )
                return self._transcribe_and_finalize(
                    manifest,
                    options,
                    local_source,
                    workspace,
                    token,
                    progress,
                )
        except OperationCancelled:
            manifest = self.job_store.set_status(
                job_id,
                JobStatus.CANCELLED,
                message="Cancelada; as partes concluídas foram preservadas.",
            )
            self._report_manifest(
                progress,
                manifest,
                source_name,
                "cancelled",
                "Cancelada; você pode retomar pelo Histórico.",
                provenance,
            )
            raise
        except BaseException as exc:
            manifest = self._mark_failed(manifest, exc)
            self._report_manifest(
                progress,
                manifest,
                source_name,
                "failed",
                _public_error(exc),
                provenance,
            )
            raise

    def list_jobs(self) -> tuple[JobManifest, ...]:
        """Return readable manifests newest-first, ignoring unrelated files."""

        jobs: list[JobManifest] = []
        for directory in self.job_store.root.iterdir():
            if not directory.is_dir():
                continue
            try:
                jobs.append(self.job_store.load_job(directory.name))
            except (JobStoreError, OSError, ValueError):
                continue
        return tuple(
            sorted(jobs, key=lambda item: (item.updated_at, item.created_at), reverse=True)
        )

    def _create_manifest(
        self,
        source: str,
        options: PipelineOptions,
        *,
        chunks: Sequence[ChunkSpec],
        source_name: str,
        provenance: str,
        extra_metadata: Mapping[str, Any] | None = None,
    ) -> JobManifest:
        metadata = {
            "source_name": source_name,
            "source_type": "url" if _is_http_url(source) else "file",
            "provenance": provenance,
            **_source_identity(source),
            **dict(extra_metadata or {}),
        }
        return self.job_store.create_job(
            source=source,
            chunks=tuple(chunks),
            provider=options.provider,
            model=options.model,
            language=options.language,
            settings=options.to_manifest_settings(),
            metadata=metadata,
        )

    def _transcribe_and_finalize(
        self,
        manifest: JobManifest,
        options: PipelineOptions,
        local_source: Path,
        workspace: Any,
        token: CancellationToken,
        progress: ProgressCallback | None,
    ) -> PipelineResult:
        source_name = str(manifest.metadata.get("source_name") or _source_name(manifest.source))
        secret = self.secret_reader(options.provider)
        if not secret:
            raise PipelineValidationError(
                f"Configure uma chave do provedor {options.provider.title()} antes de transcrever."
            )
        provider = self.provider_factory(options.provider, secret)
        manifest = self.job_store.set_status(manifest.job_id, JobStatus.RUNNING)
        results = self.job_store.load_completed_results(manifest.job_id)

        for chunk in manifest.pending_chunks:
            token.raise_if_cancelled()
            completed = len(results)
            self._report(
                progress,
                PipelineProgress(
                    job_id=manifest.job_id,
                    source_name=source_name,
                    state="preparing",
                    detail=f"Preparando parte {chunk.index + 1} de {len(manifest.chunks)}…",
                    progress=manifest.progress,
                    completed_parts=completed,
                    total_parts=len(manifest.chunks),
                    provenance="audio_transcription",
                ),
            )
            try:
                prepared = self.media.split_audio(
                    local_source,
                    (chunk,),
                    workspace=workspace,
                    cancel_token=token,
                )
                audio = prepared.chunks[0]
                self._report(
                    progress,
                    PipelineProgress(
                        job_id=manifest.job_id,
                        source_name=source_name,
                        state="running",
                        detail=(
                            f"Transcrevendo parte {chunk.index + 1} de {len(manifest.chunks)}…"
                        ),
                        progress=manifest.progress,
                        completed_parts=completed,
                        total_parts=len(manifest.chunks),
                        provenance="audio_transcription",
                    ),
                )
                transcript = provider.transcribe(
                    ProviderRequest(
                        audio_path=audio.path,
                        model_id=options.model,
                        duration=chunk.duration,
                        language=options.language,
                        context_prompt=self._context_before(chunk.index, results),
                    ),
                    token,
                )
                token.raise_if_cancelled()
                manifest = self.job_store.save_chunk_result(
                    manifest.job_id, chunk.index, transcript
                )
                results[chunk.index] = transcript
            except OperationCancelled:
                raise
            except BaseException as exc:
                self.job_store.mark_chunk_failed(manifest.job_id, chunk.index, _public_error(exc))
                raise

            self._report_manifest(
                progress,
                manifest,
                source_name,
                "running",
                f"Parte {chunk.index + 1} de {len(manifest.chunks)} concluída.",
                "audio_transcription",
            )

        transcript = assemble_chunks(manifest.chunks, results)
        return self._finalize(
            manifest,
            options,
            transcript,
            "audio_transcription",
            token,
            progress,
        )

    def _finalize(
        self,
        manifest: JobManifest,
        options: PipelineOptions,
        transcript: Transcript,
        provenance: str,
        token: CancellationToken,
        progress: ProgressCallback | None,
    ) -> PipelineResult:
        token.raise_if_cancelled()
        source_name = str(manifest.metadata.get("source_name") or _source_name(manifest.source))
        self._report_manifest(
            progress,
            manifest,
            source_name,
            "running",
            "Montando e exportando os resultados…",
            provenance,
        )
        outputs = self._export_all(transcript, manifest, options, token)
        primary = _primary_output(outputs)
        metadata = {
            **dict(manifest.metadata),
            "provenance": provenance,
            "output_paths": [str(path) for path in outputs],
            "primary_output": str(primary) if primary else "",
        }
        manifest = self.job_store.save_job(
            replace(manifest, status=JobStatus.COMPLETED, metadata=metadata)
        )
        self._report_manifest(
            progress,
            manifest,
            source_name,
            "completed",
            "Concluída; os arquivos estão prontos.",
            provenance,
        )
        return PipelineResult(manifest, transcript, outputs, provenance)

    def _export_all(
        self,
        transcript: Transcript,
        manifest: JobManifest,
        options: PipelineOptions,
        token: CancellationToken,
    ) -> tuple[Path, ...]:
        folder = self._output_folder(manifest.source, options)
        folder.mkdir(parents=True, exist_ok=True)
        if not folder.is_dir():
            raise PipelineError("A pasta de saída não pôde ser criada.")
        stem = _available_stem(
            folder,
            str(manifest.metadata.get("source_name") or _source_name(manifest.source)),
            options.formats,
        )

        outputs: list[Path] = []
        for output_format in options.formats:
            token.raise_if_cancelled()
            destination = folder / f"{stem}.{output_format}"
            if output_format == "md":
                output = export_markdown(
                    transcript,
                    destination,
                    title=str(manifest.metadata.get("source_name") or stem),
                    source=_safe_source_label(manifest.source),
                )
            elif output_format == "docx":
                output = export_transcript(
                    transcript,
                    destination,
                    format=output_format,
                    include_timestamps=True,
                    title=str(manifest.metadata.get("source_name") or stem),
                )
            else:
                output = export_transcript(
                    transcript,
                    destination,
                    format=output_format,
                )
            outputs.append(output)
        return tuple(outputs)

    def _output_folder(self, source: str, options: PipelineOptions) -> Path:
        if options.output_folder is not None:
            return options.output_folder.expanduser().resolve()
        if not _is_http_url(source):
            return Path(source).expanduser().resolve().parent
        return self.default_output_root.expanduser().resolve()

    def _prepare_local_source(
        self,
        source: str,
        *,
        workspace: Any,
        cancellation: CancellationToken,
    ) -> Path:
        if _is_http_url(source):
            path, _ = self.media.download_url(
                source,
                workspace=workspace,
                cancel_token=cancellation,
            )
            return path
        return Path(source)

    def _validated_source(self, source: str | os.PathLike[str]) -> str:
        text = os.fspath(source).strip()
        if not text:
            raise PipelineValidationError("Adicione um arquivo ou endereço para transcrever.")
        if _is_http_url(text):
            return text
        parsed = urlparse(text)
        if parsed.scheme and parsed.scheme != "file":
            raise PipelineValidationError(
                "Somente arquivos locais e endereços HTTP(S) são aceitos."
            )
        if parsed.scheme == "file":
            text = unquote(parsed.path)
        path = Path(text).expanduser().resolve()
        if not path.is_file():
            raise PipelineValidationError(f"O arquivo selecionado não existe: {path.name}.")
        return str(path)

    def _options_from_manifest(self, manifest: JobManifest) -> PipelineOptions:
        return PipelineOptions(
            provider=manifest.provider,
            model=manifest.model,
            language=manifest.language,
            formats=tuple(str(item) for item in manifest.settings.get("formats", ("txt",))),
            output_folder=(
                Path(str(manifest.settings["output_folder"]))
                if _optional_text(manifest.settings.get("output_folder"))
                else None
            ),
            prefer_existing_captions=_as_bool(
                manifest.settings.get("prefer_existing_captions", True)
            ),
        )

    @staticmethod
    def _validate_resume_source(manifest: JobManifest) -> None:
        if _is_http_url(manifest.source):
            return
        path = Path(manifest.source)
        try:
            stat = path.stat()
        except OSError as exc:
            raise PipelineValidationError(
                "A fonte original não está mais disponível para retomada."
            ) from exc
        expected_size = manifest.metadata.get("source_size")
        expected_mtime = manifest.metadata.get("source_mtime_ns")
        if (
            expected_size is not None
            and expected_mtime is not None
            and (int(expected_size) != stat.st_size or int(expected_mtime) != stat.st_mtime_ns)
        ):
            raise PipelineValidationError(
                "A fonte original foi alterada; inicie um novo trabalho."
            )

    @staticmethod
    def _context_before(index: int, results: Mapping[int, Transcript]) -> str | None:
        previous = [results[key].text for key in sorted(results) if key < index]
        context = " ".join(text for text in previous if text).strip()
        return context[-3000:] or None

    def _mark_failed(self, manifest: JobManifest, exc: BaseException) -> JobManifest:
        current = self.job_store.load_job(manifest.job_id)
        if current.status == JobStatus.FAILED:
            return current
        return self.job_store.set_status(
            manifest.job_id,
            JobStatus.FAILED,
            message=_public_error(exc),
        )

    def _report_manifest(
        self,
        callback: ProgressCallback | None,
        manifest: JobManifest,
        source_name: str,
        state: str,
        detail: str,
        provenance: str,
    ) -> None:
        self._report(
            callback,
            PipelineProgress(
                job_id=manifest.job_id,
                source_name=source_name,
                state=state,
                detail=detail,
                progress=manifest.progress,
                completed_parts=len(manifest.completed_chunks),
                total_parts=len(manifest.chunks),
                provenance=provenance,
            ),
        )

    @staticmethod
    def _report(
        callback: ProgressCallback | None,
        value: PipelineProgress,
    ) -> None:
        if callback is not None:
            callback(value)


Pipeline = TranscriptionPipeline


def transcript_to_markdown(
    transcript: Transcript,
    *,
    title: str,
    source: str | None = None,
) -> str:
    """Render a readable Markdown transcript with stable media timestamps."""

    lines = [f"# {title.strip() or 'Transcrição'}"]
    if source:
        lines.extend(("", f"Fonte: `{source}`"))
    lines.extend(("", "## Transcrição", ""))
    for segment in transcript.segments:
        timestamp = format_timestamp(segment.start, include_milliseconds=False)
        speaker = f" **{segment.speaker}:**" if segment.speaker else ""
        lines.append(f"- `{timestamp}`{speaker} {segment.text}".rstrip())
    return "\n".join(lines).rstrip() + "\n"


def export_markdown(
    transcript: Transcript,
    path: str | os.PathLike[str],
    *,
    title: str,
    source: str | None = None,
) -> Path:
    """Atomically write the integration layer's additional ``.md`` format."""

    destination = Path(path).expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(transcript_to_markdown(transcript, title=title, source=source))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise
    return destination


def _available_stem(folder: Path, source_name: str, formats: Sequence[str]) -> str:
    base = _safe_stem(Path(source_name).stem or source_name)
    candidate = base
    suffix = 2
    while any((folder / f"{candidate}.{item}").exists() for item in formats):
        candidate = f"{base} ({suffix})"
        suffix += 1
    return candidate


def _safe_stem(value: str) -> str:
    cleaned = _UNSAFE_FILENAME_RE.sub("-", value).strip(" .-")
    return (cleaned or "transcricao")[:120].rstrip(" .")


def _source_name(source: str) -> str:
    if not _is_http_url(source):
        return Path(source).name
    parsed = urlparse(source)
    final = unquote(Path(parsed.path).name).strip()
    return final or parsed.netloc


def _workspace_source_name(workspace: Any, fallback: str) -> str:
    metadata = getattr(workspace, "metadata", {})
    if not isinstance(metadata, Mapping):
        return fallback
    title = str(metadata.get("title") or "").strip()
    return title or fallback


def _safe_source_label(source: str) -> str:
    """Remove URL credentials, query strings and fragments from exported text."""

    if not _is_http_url(source):
        return source
    parsed = urlparse(source)
    hostname = parsed.hostname or ""
    try:
        port = parsed.port
    except ValueError:
        port = None
    if port:
        hostname = f"{hostname}:{port}"
    return parsed._replace(netloc=hostname, query="", fragment="").geturl()


def _source_identity(source: str) -> dict[str, int]:
    if _is_http_url(source):
        return {}
    try:
        stat = Path(source).stat()
    except OSError:
        return {}
    return {
        "source_size": stat.st_size,
        "source_mtime_ns": stat.st_mtime_ns,
    }


def _subtitle_provenance(origin: SubtitleOrigin) -> str:
    if origin == SubtitleOrigin.URL_AUTOMATIC:
        return "automatic_captions"
    if origin == SubtitleOrigin.URL_MANUAL:
        return "author_captions"
    return "existing_captions"


def _primary_output(outputs: Sequence[Path]) -> Path | None:
    by_suffix = {path.suffix.casefold().lstrip("."): path for path in outputs}
    return next(
        (by_suffix[item] for item in ("docx", "md", "txt", "srt", "vtt") if item in by_suffix),
        None,
    )


def _is_http_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _optional_text(value: object) -> str | None:
    text = str(value or "").strip()
    return text or None


def _as_bool(value: object) -> bool:
    if isinstance(value, str):
        return value.strip().casefold() not in {"", "0", "false", "no", "off"}
    return bool(value)


def _public_error(exc: BaseException) -> str:
    if isinstance(exc, ProviderError):
        return exc.message
    if isinstance(exc, PipelineError):
        return str(exc)
    if isinstance(exc, MediaDependencyError):
        return "Instale FFmpeg, ffprobe e yt-dlp para preparar esta mídia."
    if isinstance(exc, MediaError):
        return "A mídia não pôde ser preparada para transcrição."
    if isinstance(exc, ExportError):
        return "Um dos arquivos de saída não pôde ser gerado."
    if isinstance(exc, CredentialError):
        return "A credencial não pôde ser lida no cofre seguro."
    if isinstance(exc, JobStoreError):
        return "O estado salvo do trabalho não pôde ser atualizado."
    if isinstance(exc, (OSError, UnicodeError, ValueError)):
        return "Um arquivo necessário não pôde ser processado."
    return "A transcrição não pôde ser concluída."


__all__ = [
    "Pipeline",
    "PipelineError",
    "PipelineOptions",
    "PipelineProgress",
    "PipelineResult",
    "PipelineValidationError",
    "SUPPORTED_FORMATS",
    "TranscriptionPipeline",
    "export_markdown",
    "transcript_to_markdown",
]
