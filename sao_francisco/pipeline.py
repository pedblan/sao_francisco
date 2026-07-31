"""Application-level orchestration for resumable media transcription.

The core package deliberately has no opinion about GUI state or providers.  This
module joins those pieces while remaining synchronous and Qt-free: callers run a
pipeline behind a worker boundary, receive progress snapshots, and can cancel
through the shared :class:`~sao_francisco.core.CancellationToken`.
"""

from __future__ import annotations

import os
import re
import tempfile
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

from .catalog import editorial_route_for, model_by_id
from .core import (
    EDITORIAL_CONTRACT_VERSION,
    CancellationToken,
    ChunkSpec,
    CostRecord,
    EditorialBlock,
    EditorialValidationError,
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
    assemble_editorial_results,
    build_cost_record,
    export_improved_docx,
    export_improved_txt,
    export_transcript,
    format_cost_label,
    format_timestamp,
    format_usage_label,
    plan_chunks,
    plan_editorial_blocks,
    summarize_costs,
    transcript_to_editorial_text,
    validate_editorial_result,
    zero_cost_record,
)
from .credentials import CredentialError, read_secret
from .providers import (
    EditorialProvider,
    EditorialRequest,
    ProviderError,
    ProviderRequest,
    TranscriptionProvider,
    editorial_provider_for,
    provider_for,
)

SUPPORTED_FORMATS = frozenset({"docx", "md", "srt", "txt", "vtt"})
_LANGUAGE_RE = re.compile(r"^[A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8})*$")
_UNSAFE_FILENAME_RE = re.compile(r"[\x00-\x1f<>:\"/\\|?*]+")

ProgressCallback = Callable[["PipelineProgress"], None]
ProviderFactory = Callable[[str, str], TranscriptionProvider]
EditorialProviderFactory = Callable[[str, str], EditorialProvider]
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
    prefer_existing_captions: bool = False
    include_timestamps: bool = False
    improve_with_ai: bool = False

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
        object.__setattr__(self, "include_timestamps", bool(self.include_timestamps))
        improve = bool(self.improve_with_ai)
        if improve and not {"docx", "txt"} & set(formats):
            raise PipelineValidationError(
                "Para melhorar o texto, escolha DOCX ou TXT."
            )
        object.__setattr__(self, "improve_with_ai", improve)

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
                    value.get("prefer_existing_captions", False),
                )
            ),
            include_timestamps=_as_bool(
                value.get(
                    "includeTimestamps",
                    value.get("include_timestamps", False),
                )
            ),
            improve_with_ai=_as_bool(
                value.get(
                    "improveWithAi",
                    value.get("improve_with_ai", False),
                )
            ),
        )

    def to_manifest_settings(self) -> dict[str, Any]:
        """Return JSON-safe settings; credentials are intentionally absent."""

        return {
            "formats": list(self.formats),
            "output_folder": str(self.output_folder) if self.output_folder else "",
            "prefer_existing_captions": self.prefer_existing_captions,
            "include_timestamps": self.include_timestamps,
            "improve_with_ai": self.improve_with_ai,
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
    stage: str = ""
    cost_label: str = ""
    usage_label: str = ""

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
            "stage": self.stage,
            "costLabel": self.cost_label,
            "usageLabel": self.usage_label,
        }


@dataclass(frozen=True, slots=True)
class PipelineResult:
    manifest: JobManifest
    transcript: Transcript
    outputs: tuple[Path, ...]
    provenance: str
    improved_text: str | None = None
    output_groups: Mapping[str, tuple[Path, ...]] = field(default_factory=dict)

    @property
    def primary_output(self) -> Path | None:
        preferred = ("docx", "md", "txt", "srt", "vtt")
        improved = tuple(self.output_groups.get("improved", ()))
        if improved:
            preferred_improved = next(
                (path for suffix in preferred for path in improved if path.suffix == f".{suffix}"),
                None,
            )
            if preferred_improved is not None:
                return preferred_improved
        by_suffix = {path.suffix.casefold().lstrip("."): path for path in self.outputs}
        return next((by_suffix[item] for item in preferred if item in by_suffix), None)


class TranscriptionPipeline:
    """Run and resume one source at a time.

    The class is safe to invoke in a worker thread or disposable process, but is
    not internally concurrent.  The :class:`JobStore` keeps every completed
    provider response crash-safe.
    """

    def __init__(
        self,
        job_store: JobStore,
        *,
        media: MediaProcessor | None = None,
        provider_factory: ProviderFactory = provider_for,
        editorial_provider_factory: EditorialProviderFactory = editorial_provider_for,
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
        self.editorial_provider_factory = editorial_provider_factory
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
                    subtitle_transcript = _with_cost_record(
                        subtitle.transcript,
                        zero_cost_record(
                            stage="transcription",
                            unit_id="caption-0",
                            provider=selected.provider,
                            model=selected.model,
                        ),
                    )
                    manifest = self.job_store.save_chunk_result(
                        manifest.job_id, 0, subtitle_transcript
                    )
                    manifest = self._update_cost_metadata(manifest)
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
                        subtitle_transcript,
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
                manifest = self._mark_cancelled(
                    manifest,
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
                    pending_index = manifest.pending_chunks[0].index
                    subtitle_transcript = _with_cost_record(
                        subtitle.transcript,
                        zero_cost_record(
                            stage="transcription",
                            unit_id=f"caption-{pending_index}",
                            provider=options.provider,
                            model=options.model,
                        ),
                    )
                    manifest = self.job_store.save_chunk_result(
                        job_id, pending_index, subtitle_transcript
                    )
                    manifest = self._update_cost_metadata(manifest)
                    return self._finalize(
                        manifest,
                        options,
                        subtitle_transcript,
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
            manifest = self._mark_cancelled(
                manifest,
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

    def load_result(self, job_id: str) -> PipelineResult:
        """Rebuild a completed result from durable job artifacts."""

        manifest = self.job_store.load_job(job_id)
        transcript = self.job_store.load_original_result(job_id)
        groups = _saved_output_groups(manifest)
        outputs = _flatten_output_groups(groups)
        if not outputs:
            outputs = tuple(
                Path(str(path))
                for path in manifest.metadata.get("output_paths", ())
            )
            groups = {
                "improved": (),
                "original": outputs,
                "captions": (),
            }
        improved_text = (
            self.job_store.load_improved_result(job_id)
            if self.job_store.has_improved_result(job_id)
            else None
        )
        return PipelineResult(
            manifest=manifest,
            transcript=transcript,
            outputs=outputs,
            provenance=str(
                manifest.metadata.get("provenance") or "audio_transcription"
            ),
            improved_text=improved_text,
            output_groups=groups,
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
        planned_records = [
            build_cost_record(
                stage="transcription",
                unit_id=f"planned-{chunk.index}",
                provider=options.provider,
                model=options.model,
                duration_seconds=chunk.duration,
            )
            for chunk in chunks
        ]
        forecast = summarize_costs(planned_records)
        metadata = {
            "source_name": source_name,
            "source_type": "url" if _is_http_url(source) else "file",
            "provenance": provenance,
            "pipeline_stage": "preparing",
            "cost_forecast": forecast,
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
                    progress=overall_progress(manifest),
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
                        progress=overall_progress(manifest),
                        completed_parts=completed,
                        total_parts=len(manifest.chunks),
                        provenance="audio_transcription",
                    ),
                )
                manifest, attempt_id = self._start_remote_attempt(
                    manifest,
                    stage="transcription",
                    unit_id=f"chunk-{chunk.index}",
                    provider=options.provider,
                    model=options.model,
                )
                try:
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
                except OperationCancelled:
                    self._finish_remote_attempt(
                        manifest.job_id,
                        attempt_id,
                        status="remote_ambiguous",
                        remote_result_ambiguous=True,
                        error_code="cancelled_in_flight",
                    )
                    raise
                except BaseException as exc:
                    self._finish_remote_attempt(
                        manifest.job_id,
                        attempt_id,
                        status="failed",
                        error_code=_error_code(exc),
                    )
                    raise
                record = build_cost_record(
                    stage="transcription",
                    unit_id=f"chunk-{chunk.index}",
                    provider=options.provider,
                    model=options.model,
                    usage=transcript.metadata.get("usage"),
                    duration_seconds=chunk.duration,
                )
                transcript = _with_cost_record(transcript, record)
                manifest = self.job_store.save_chunk_result(
                    manifest.job_id, chunk.index, transcript
                )
                manifest = self._finish_remote_attempt(
                    manifest.job_id,
                    attempt_id,
                    status="accepted",
                    cost_record=record,
                )
                results[chunk.index] = transcript
                manifest = self._update_cost_metadata(manifest)
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
        source_name = str(
            manifest.metadata.get("source_name") or _source_name(manifest.source)
        )
        if self.job_store.has_original_result(manifest.job_id):
            transcript = self.job_store.load_original_result(manifest.job_id)
        else:
            self.job_store.save_original_result(manifest.job_id, transcript)
        manifest = self._save_stage(
            manifest,
            "transcription_complete",
            status=JobStatus.RUNNING,
        )
        manifest = self._update_cost_metadata(manifest)
        try:
            manifest, output_groups = self._ensure_original_exports(
                manifest,
                options,
                transcript,
                token,
                progress,
                provenance,
            )
        except BaseException:
            self._save_stage(
                manifest,
                "original_export_failed",
                status=JobStatus.FAILED,
            )
            raise

        improved_text: str | None = None
        if options.improve_with_ai:
            if self.job_store.has_improved_result(manifest.job_id):
                improved_text = self.job_store.load_improved_result(manifest.job_id)
            else:
                improved_text, manifest = self._improve_text(
                    manifest,
                    options,
                    transcript,
                    token,
                    progress,
                )

        if improved_text is not None:
            manifest = self._save_stage(
                manifest,
                "exporting_improved",
                status=JobStatus.RUNNING,
            )
            self._report_manifest(
                progress,
                manifest,
                source_name,
                "running",
                "Criando os arquivos do texto melhorado…",
                provenance,
            )
            try:
                improved_outputs = self._export_improved(
                    transcript,
                    improved_text,
                    manifest,
                    options,
                    token,
                )
            except BaseException:
                self._save_stage(
                    manifest,
                    "improved_export_failed",
                    status=JobStatus.FAILED,
                )
                raise
            output_groups = {
                **output_groups,
                "improved": improved_outputs,
            }
            manifest = self._save_output_groups(
                manifest,
                output_groups,
                stage="improvement_exported",
            )

        token.raise_if_cancelled()
        outputs = _flatten_output_groups(output_groups)
        primary = _primary_output(output_groups.get("improved", ()) or outputs)
        metadata = {
            **dict(manifest.metadata),
            "provenance": provenance,
            "pipeline_stage": "completed",
            "output_paths": [str(path) for path in outputs],
            "output_groups": {
                key: [str(path) for path in values]
                for key, values in output_groups.items()
            },
            "primary_output": str(primary) if primary else "",
        }
        metadata.pop("status_message", None)
        manifest = self.job_store.save_job(
            replace(manifest, status=JobStatus.COMPLETED, metadata=metadata)
        )
        manifest = self._update_cost_metadata(manifest)
        self._report_manifest(
            progress,
            manifest,
            source_name,
            "completed",
            "Concluída; os arquivos estão prontos.",
            provenance,
        )
        return PipelineResult(
            manifest,
            transcript,
            outputs,
            provenance,
            improved_text,
            output_groups,
        )

    def _ensure_original_exports(
        self,
        manifest: JobManifest,
        options: PipelineOptions,
        transcript: Transcript,
        token: CancellationToken,
        progress: ProgressCallback | None,
        provenance: str,
    ) -> tuple[JobManifest, dict[str, tuple[Path, ...]]]:
        saved = _saved_output_groups(manifest)
        expected = len(options.formats)
        existing = (*saved["original"], *saved["captions"])
        if (
            bool(manifest.metadata.get("original_ready"))
            and len(existing) == expected
            and all(path.is_file() for path in existing)
        ):
            return manifest, saved

        source_name = str(
            manifest.metadata.get("source_name") or _source_name(manifest.source)
        )
        manifest = self._save_stage(
            manifest,
            "exporting_original",
            status=JobStatus.RUNNING,
        )
        self._report_manifest(
            progress,
            manifest,
            source_name,
            "running",
            "Transcrição pronta; criando os arquivos originais…",
            provenance,
        )
        groups = self._export_original(
            transcript,
            manifest,
            options,
            token,
        )
        manifest = self._save_output_groups(
            manifest,
            groups,
            stage="original_exported",
            extra_metadata={"original_ready": True},
        )
        self._report_manifest(
            progress,
            manifest,
            source_name,
            "running",
            (
                "Transcrição original pronta; iniciando a melhoria…"
                if options.improve_with_ai
                else "Transcrição original pronta."
            ),
            provenance,
        )
        return manifest, groups

    def _export_original(
        self,
        transcript: Transcript,
        manifest: JobManifest,
        options: PipelineOptions,
        token: CancellationToken,
    ) -> dict[str, tuple[Path, ...]]:
        folder, stem = self._result_destination(manifest, options)

        original_outputs: list[Path] = []
        caption_outputs: list[Path] = []
        for output_format in options.formats:
            token.raise_if_cancelled()
            original_suffix = (
                " — transcrição"
                if options.improve_with_ai and output_format in {"docx", "txt"}
                else ""
            )
            destination = folder / f"{stem}{original_suffix}.{output_format}"
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
                    include_timestamps=options.include_timestamps,
                    title=str(manifest.metadata.get("source_name") or stem),
                )
            elif output_format == "txt":
                output = export_transcript(
                    transcript,
                    destination,
                    format=output_format,
                    include_timestamps=options.include_timestamps,
                )
            else:
                output = export_transcript(
                    transcript,
                    destination,
                    format=output_format,
                )
            if output_format in {"srt", "vtt"}:
                caption_outputs.append(output)
            else:
                original_outputs.append(output)

        return {
            "improved": (),
            "original": tuple(original_outputs),
            "captions": tuple(caption_outputs),
        }

    def _export_improved(
        self,
        transcript: Transcript,
        improved_text: str,
        manifest: JobManifest,
        options: PipelineOptions,
        token: CancellationToken,
    ) -> tuple[Path, ...]:
        folder, stem = self._result_destination(manifest, options)
        title = str(manifest.metadata.get("source_name") or stem)
        outputs: list[Path] = []
        for output_format in options.formats:
            if output_format not in {"docx", "txt"}:
                continue
            token.raise_if_cancelled()
            destination = folder / f"{stem} — texto melhorado.{output_format}"
            if output_format == "docx":
                output = export_improved_docx(
                    improved_text,
                    destination,
                    title=title,
                    language=transcript.language,
                )
            else:
                output = export_improved_txt(improved_text, destination)
            outputs.append(output)
        return tuple(outputs)

    def _result_destination(
        self,
        manifest: JobManifest,
        options: PipelineOptions,
    ) -> tuple[Path, str]:
        folder = self._output_folder(manifest.source, options)
        folder.mkdir(parents=True, exist_ok=True)
        if not folder.is_dir():
            raise PipelineError("A pasta de saída não pôde ser criada.")
        current = self.job_store.load_job(manifest.job_id)
        stem = str(current.metadata.get("result_stem") or "").strip()
        if not stem:
            stem = _available_result_stem(
                folder,
                str(current.metadata.get("source_name") or _source_name(current.source)),
                options.formats,
                options.improve_with_ai,
            )
            metadata = {**dict(current.metadata), "result_stem": stem}
            self.job_store.save_job(replace(current, metadata=metadata))
        return folder, stem

    def _save_output_groups(
        self,
        manifest: JobManifest,
        groups: Mapping[str, Sequence[Path]],
        *,
        stage: str,
        extra_metadata: Mapping[str, Any] | None = None,
    ) -> JobManifest:
        current = self.job_store.load_job(manifest.job_id)
        normalized = {
            key: tuple(Path(path) for path in groups.get(key, ()))
            for key in ("improved", "original", "captions")
        }
        outputs = _flatten_output_groups(normalized)
        primary = _primary_output(normalized["improved"] or outputs)
        metadata = {
            **dict(current.metadata),
            "pipeline_stage": stage,
            "output_paths": [str(path) for path in outputs],
            "output_groups": {
                key: [str(path) for path in paths]
                for key, paths in normalized.items()
            },
            "primary_output": str(primary) if primary else "",
            **dict(extra_metadata or {}),
        }
        return self.job_store.save_job(
            replace(current, status=JobStatus.RUNNING, metadata=metadata)
        )

    def _improve_text(
        self,
        manifest: JobManifest,
        options: PipelineOptions,
        transcript: Transcript,
        token: CancellationToken,
        progress: ProgressCallback | None,
    ) -> tuple[str, JobManifest]:
        token.raise_if_cancelled()
        source_name = str(
            manifest.metadata.get("source_name") or _source_name(manifest.source)
        )
        original_text = transcript_to_editorial_text(transcript)
        if self.job_store.has_editorial_plan(manifest.job_id):
            raw_plan = self.job_store.load_editorial_plan(manifest.job_id)
            if str(raw_plan.get("contract_version")) != EDITORIAL_CONTRACT_VERSION:
                raise PipelineError(
                    "A melhoria salva usa uma versão incompatível. Inicie um novo trabalho."
                )
            blocks = tuple(
                EditorialBlock.from_dict(item)
                for item in raw_plan.get("blocks", ())
            )
        else:
            blocks = plan_editorial_blocks(original_text)
            self.job_store.save_editorial_plan(
                manifest.job_id,
                {
                    "contract_version": EDITORIAL_CONTRACT_VERSION,
                    "blocks": [item.to_dict() for item in blocks],
                },
            )

        if not blocks:
            self.job_store.save_improved_result(manifest.job_id, original_text)
            return original_text, self._save_stage(
                manifest,
                "improvement_complete",
                status=JobStatus.RUNNING,
            )

        saved = self.job_store.load_editorial_results(manifest.job_id)
        route = editorial_route_for(options.provider, options.model)
        pending = [block for block in blocks if block.block_id not in saved]
        provider: EditorialProvider | None = None
        if pending:
            secret = self.secret_reader(options.provider)
            if not secret:
                raise PipelineValidationError(
                    "Configure a chave do serviço escolhido antes de melhorar o texto."
                )
            provider = self.editorial_provider_factory(options.provider, secret)

        manifest = self._save_stage(
            manifest,
            "improving",
            status=JobStatus.RUNNING,
            extra_metadata={
                "editorial_total": len(blocks),
                "editorial_completed": len(saved),
            },
        )
        for block in pending:
            token.raise_if_cancelled()
            completed = len(saved)
            self._report(
                progress,
                PipelineProgress(
                    job_id=manifest.job_id,
                    source_name=source_name,
                    state="running",
                    detail=(
                        f"Melhorando o texto — parte {completed + 1} de {len(blocks)}…"
                    ),
                    progress=overall_progress(manifest, "improving"),
                    completed_parts=completed,
                    total_parts=len(blocks),
                    provenance=str(manifest.metadata.get("provenance") or ""),
                    stage="improving",
                    **self._cost_labels(manifest, in_progress=True),
                ),
            )
            if provider is None:
                raise PipelineError("A melhoria não pôde ser iniciada.")
            manifest, attempt_id = self._start_remote_attempt(
                manifest,
                stage="improvement",
                unit_id=block.block_id,
                provider=options.provider,
                model=route.model_id,
            )
            try:
                response = provider.improve(
                    EditorialRequest(
                        block_id=block.block_id,
                        text=block.text,
                        model_id=route.model_id,
                        reasoning_effort=route.reasoning_effort,
                        previous_context=_editorial_context(block.index, blocks),
                    ),
                    token,
                )
            except OperationCancelled:
                self._finish_remote_attempt(
                    manifest.job_id,
                    attempt_id,
                    status="remote_ambiguous",
                    remote_result_ambiguous=True,
                    error_code="cancelled_in_flight",
                )
                raise
            except BaseException as exc:
                self._finish_remote_attempt(
                    manifest.job_id,
                    attempt_id,
                    status="failed",
                    error_code=_error_code(exc),
                )
                raise
            cost_record = build_cost_record(
                stage="improvement",
                unit_id=block.block_id,
                provider=options.provider,
                model=route.model_id,
                usage=response.usage,
            )
            try:
                improved = validate_editorial_result(block.text, response.text)
                value = {
                    "block_id": block.block_id,
                    "index": block.index,
                    "text": improved,
                    "model": response.model_id,
                    "contract_version": EDITORIAL_CONTRACT_VERSION,
                    "usage": response.usage.to_dict(),
                    "cost_record": cost_record.to_dict(),
                }
                self.job_store.save_editorial_result(
                    manifest.job_id,
                    block.block_id,
                    value,
                )
            except BaseException as exc:
                self._finish_remote_attempt(
                    manifest.job_id,
                    attempt_id,
                    status="failed",
                    error_code=_error_code(exc),
                    cost_record=cost_record,
                )
                self._update_cost_metadata(manifest)
                raise
            manifest = self._finish_remote_attempt(
                manifest.job_id,
                attempt_id,
                status="accepted",
                cost_record=cost_record,
            )
            saved[block.block_id] = value
            manifest = self._update_cost_metadata(manifest)
            manifest = self._save_stage(
                manifest,
                "improving",
                status=JobStatus.RUNNING,
                extra_metadata={
                    "editorial_total": len(blocks),
                    "editorial_completed": len(saved),
                },
            )

        token.raise_if_cancelled()
        assembled = assemble_editorial_results(
            blocks,
            {
                block_id: str(value.get("text") or "")
                for block_id, value in saved.items()
            },
        )
        self.job_store.save_improved_result(manifest.job_id, assembled)
        manifest = self._save_stage(
            manifest,
            "improvement_complete",
            status=JobStatus.RUNNING,
        )
        self._report_manifest(
            progress,
            manifest,
            source_name,
            "running",
            "Texto melhorado pronto; criando os arquivos…",
            str(manifest.metadata.get("provenance") or ""),
        )
        return assembled, manifest

    def _save_stage(
        self,
        manifest: JobManifest,
        stage: str,
        *,
        status: JobStatus,
        extra_metadata: Mapping[str, Any] | None = None,
    ) -> JobManifest:
        current = self.job_store.load_job(manifest.job_id)
        metadata = {
            **dict(current.metadata),
            "pipeline_stage": stage,
            **dict(extra_metadata or {}),
        }
        return self.job_store.save_job(
            replace(current, status=status, metadata=metadata)
        )

    def _update_cost_metadata(self, manifest: JobManifest) -> JobManifest:
        current = self.job_store.load_job(manifest.job_id)
        records: list[CostRecord] = []
        for transcript in self.job_store.load_completed_results(manifest.job_id).values():
            raw = transcript.metadata.get("cost_record")
            if isinstance(raw, Mapping):
                records.append(CostRecord.from_dict(raw))
        for value in self.job_store.load_editorial_results(manifest.job_id).values():
            raw = value.get("cost_record")
            if isinstance(raw, Mapping):
                records.append(CostRecord.from_dict(raw))
        raw_adjustments = current.metadata.get("cost_adjustments", ())
        if isinstance(raw_adjustments, Sequence) and not isinstance(
            raw_adjustments, (str, bytes)
        ):
            for raw in raw_adjustments:
                if isinstance(raw, Mapping):
                    records.append(CostRecord.from_dict(raw))
        raw_attempts = current.metadata.get("attempts", ())
        if isinstance(raw_attempts, Sequence) and not isinstance(
            raw_attempts, (str, bytes)
        ):
            for attempt in raw_attempts:
                if not isinstance(attempt, Mapping) or attempt.get("status") == "accepted":
                    continue
                raw = attempt.get("cost_record")
                if isinstance(raw, Mapping):
                    records.append(CostRecord.from_dict(raw))
        zero_proven = (
            str(current.metadata.get("provenance") or "") != "audio_transcription"
            and not bool(current.settings.get("improve_with_ai", False))
        )
        summary = summarize_costs(records, zero_proven=zero_proven)
        metadata = {**dict(current.metadata), "cost_summary": summary}
        return self.job_store.save_job(replace(current, metadata=metadata))

    def _start_remote_attempt(
        self,
        manifest: JobManifest,
        *,
        stage: str,
        unit_id: str,
        provider: str,
        model: str,
    ) -> tuple[JobManifest, str]:
        current = self.job_store.load_job(manifest.job_id)
        raw_attempts = current.metadata.get("attempts", ())
        attempts = (
            [dict(item) for item in raw_attempts if isinstance(item, Mapping)]
            if isinstance(raw_attempts, Sequence)
            and not isinstance(raw_attempts, (str, bytes))
            else []
        )
        number = 1 + sum(
            item.get("stage") == stage and item.get("unit_id") == unit_id
            for item in attempts
        )
        attempt_id = f"{stage}:{unit_id}:{number}"
        attempts.append(
            {
                "attempt_id": attempt_id,
                "stage": stage,
                "unit_id": unit_id,
                "provider": provider,
                "model": model,
                "status": "running",
                "started_at": _now(),
                "finished_at": None,
                "error_code": None,
                "remote_result_ambiguous": False,
            }
        )
        metadata = {
            **dict(current.metadata),
            "attempts": attempts,
            "active_attempt_id": attempt_id,
        }
        return (
            self.job_store.save_job(replace(current, metadata=metadata)),
            attempt_id,
        )

    def _finish_remote_attempt(
        self,
        job_id: str,
        attempt_id: str,
        *,
        status: str,
        error_code: str | None = None,
        remote_result_ambiguous: bool = False,
        cost_record: CostRecord | None = None,
    ) -> JobManifest:
        current = self.job_store.load_job(job_id)
        raw_attempts = current.metadata.get("attempts", ())
        attempts = (
            [dict(item) for item in raw_attempts if isinstance(item, Mapping)]
            if isinstance(raw_attempts, Sequence)
            and not isinstance(raw_attempts, (str, bytes))
            else []
        )
        found = False
        for item in attempts:
            if item.get("attempt_id") != attempt_id:
                continue
            item.update(
                status=status,
                finished_at=_now(),
                error_code=error_code,
                remote_result_ambiguous=remote_result_ambiguous,
            )
            if cost_record is not None:
                item["cost_record"] = cost_record.to_dict()
            found = True
            break
        if not found:
            raise PipelineError("A tentativa remota ativa não pôde ser reconciliada.")
        metadata = {**dict(current.metadata), "attempts": attempts}
        if metadata.get("active_attempt_id") == attempt_id:
            metadata.pop("active_attempt_id", None)
        if remote_result_ambiguous:
            metadata["remote_result_ambiguous"] = True
        return self.job_store.save_job(replace(current, metadata=metadata))

    def mark_stalled_cancelled(self, job_id: str) -> JobManifest:
        """Persist a forced cancellation after the worker process is gone."""

        current = self.job_store.load_job(job_id)
        raw_attempts = current.metadata.get("attempts", ())
        attempts = (
            [dict(item) for item in raw_attempts if isinstance(item, Mapping)]
            if isinstance(raw_attempts, Sequence)
            and not isinstance(raw_attempts, (str, bytes))
            else []
        )
        ambiguous = self._reconcile_unfinished_attempts(
            current,
            attempts,
            unresolved_error_code="cancelled_in_flight",
        )
        metadata = {
            **dict(current.metadata),
            "attempts": attempts,
            "pipeline_stage": "cancelled",
            "cancelled_from_stage": str(
                current.metadata.get("pipeline_stage") or ""
            ),
            "cancellation_state": "cancelled",
            "status_message": (
                "Cancelada; a transcrição original foi preservada. "
                "Uma chamada em andamento pode ter sido processada pelo serviço."
                if ambiguous
                else "Cancelada; as partes concluídas foram preservadas."
            ),
        }
        metadata.pop("active_attempt_id", None)
        if ambiguous:
            metadata["remote_result_ambiguous"] = True
        return self.job_store.save_job(
            replace(current, status=JobStatus.CANCELLED, metadata=metadata)
        )

    def request_cancel(self, job_id: str) -> JobManifest:
        """Persist the user's intent before signalling the worker process."""

        current = self.job_store.load_job(job_id)
        raw_attempts = current.metadata.get("attempts", ())
        attempts = (
            [dict(item) for item in raw_attempts if isinstance(item, Mapping)]
            if isinstance(raw_attempts, Sequence)
            and not isinstance(raw_attempts, (str, bytes))
            else []
        )
        for item in attempts:
            if item.get("status") == "running":
                item["status"] = "cancel_requested"
                item["cancel_requested_at"] = _now()
        metadata = {
            **dict(current.metadata),
            "attempts": attempts,
            "cancel_requested_at": _now(),
            "cancellation_state": "cancel_requested",
            "status_message": (
                "Cancelamento solicitado; preservando as partes concluídas."
            ),
        }
        return self.job_store.save_job(replace(current, metadata=metadata))

    def mark_interrupted(self, job_id: str) -> JobManifest:
        """Pause a job left running by an earlier process or app session."""

        current = self.job_store.load_job(job_id)
        raw_attempts = current.metadata.get("attempts", ())
        attempts = (
            [dict(item) for item in raw_attempts if isinstance(item, Mapping)]
            if isinstance(raw_attempts, Sequence)
            and not isinstance(raw_attempts, (str, bytes))
            else []
        )
        ambiguous = self._reconcile_unfinished_attempts(
            current,
            attempts,
            unresolved_error_code="process_interrupted",
        )
        stage = str(current.metadata.get("pipeline_stage") or "")
        legacy_editorial = stage == "improving" and not attempts
        metadata = {
            **dict(current.metadata),
            "attempts": attempts,
            "status_message": (
                "Interrompida durante uma chamada remota; retome explicitamente "
                "porque o serviço pode ter processado a tentativa."
                if ambiguous or legacy_editorial
                else "Interrompida quando o aplicativo foi fechado."
            ),
        }
        metadata.pop("active_attempt_id", None)
        if ambiguous or legacy_editorial:
            metadata["remote_result_ambiguous"] = True
        return self.job_store.save_job(
            replace(current, status=JobStatus.PAUSED, metadata=metadata)
        )

    def _reconcile_unfinished_attempts(
        self,
        manifest: JobManifest,
        attempts: list[dict[str, Any]],
        *,
        unresolved_error_code: str,
    ) -> bool:
        """Prefer a durable artifact over an unfinished manifest update."""

        saved_costs: dict[tuple[str, str], Mapping[str, Any] | None] = {}
        for index, transcript in self.job_store.load_completed_results(
            manifest.job_id
        ).items():
            raw_cost = transcript.metadata.get("cost_record")
            saved_costs[("transcription", f"chunk-{index}")] = (
                raw_cost if isinstance(raw_cost, Mapping) else None
            )
        for block_id, value in self.job_store.load_editorial_results(
            manifest.job_id
        ).items():
            raw_cost = value.get("cost_record")
            saved_costs[("improvement", block_id)] = (
                raw_cost if isinstance(raw_cost, Mapping) else None
            )

        ambiguous = False
        for item in attempts:
            if item.get("status") not in {"running", "cancel_requested"}:
                continue
            key = (str(item.get("stage") or ""), str(item.get("unit_id") or ""))
            if key in saved_costs:
                item.update(
                    status="accepted",
                    finished_at=_now(),
                    error_code=None,
                    remote_result_ambiguous=False,
                )
                if saved_costs[key] is not None:
                    item["cost_record"] = dict(saved_costs[key] or {})
                continue
            item.update(
                status="remote_ambiguous",
                finished_at=_now(),
                error_code=unresolved_error_code,
                remote_result_ambiguous=True,
            )
            ambiguous = True
        return ambiguous

    @staticmethod
    def _cost_labels(
        manifest: JobManifest,
        *,
        in_progress: bool,
    ) -> dict[str, str]:
        summary = manifest.metadata.get("cost_summary")
        if not isinstance(summary, Mapping) or (
            summary.get("usd") is None and not summary.get("proven_zero")
        ):
            forecast = manifest.metadata.get("cost_forecast")
            if isinstance(forecast, Mapping):
                summary = forecast
        normalized = summary if isinstance(summary, Mapping) else {}
        return {
            "cost_label": format_cost_label(normalized, in_progress=in_progress),
            "usage_label": format_usage_label(normalized),
        }

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
                manifest.settings.get("prefer_existing_captions", False)
            ),
            include_timestamps=_as_bool(
                manifest.settings.get("include_timestamps", False)
            ),
            improve_with_ai=_as_bool(
                manifest.settings.get("improve_with_ai", False)
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

    def _mark_cancelled(
        self,
        manifest: JobManifest,
        *,
        message: str,
    ) -> JobManifest:
        current = self.job_store.load_job(manifest.job_id)
        previous_stage = str(current.metadata.get("pipeline_stage") or "")
        raw_attempts = current.metadata.get("attempts", ())
        attempts = (
            [dict(item) for item in raw_attempts if isinstance(item, Mapping)]
            if isinstance(raw_attempts, Sequence)
            and not isinstance(raw_attempts, (str, bytes))
            else []
        )
        ambiguous = self._reconcile_unfinished_attempts(
            current,
            attempts,
            unresolved_error_code="cancelled_in_flight",
        )
        metadata = {
            **dict(current.metadata),
            "attempts": attempts,
            "pipeline_stage": "cancelled",
            "cancelled_from_stage": previous_stage,
            "cancellation_state": "cancelled",
            "status_message": message,
        }
        metadata.pop("active_attempt_id", None)
        if ambiguous:
            metadata["remote_result_ambiguous"] = True
        return self.job_store.save_job(
            replace(current, status=JobStatus.CANCELLED, metadata=metadata)
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
        current = self.job_store.load_job(manifest.job_id)
        stage = str(current.metadata.get("pipeline_stage") or "")
        if stage == "improving":
            total_parts = max(1, int(current.metadata.get("editorial_total") or 1))
            completed_parts = min(
                total_parts,
                max(0, int(current.metadata.get("editorial_completed") or 0)),
            )
        else:
            completed_parts = len(current.completed_chunks)
            total_parts = len(current.chunks)
        self._report(
            callback,
            PipelineProgress(
                job_id=current.job_id,
                source_name=source_name,
                state=state,
                detail=detail,
                progress=overall_progress(current, stage),
                completed_parts=completed_parts,
                total_parts=total_parts,
                provenance=provenance,
                stage=stage,
                **self._cost_labels(current, in_progress=state != "completed"),
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


def _available_result_stem(
    folder: Path,
    source_name: str,
    formats: Sequence[str],
    has_improved: bool,
) -> str:
    base = _safe_stem(Path(source_name).stem or source_name)
    candidate = base
    suffix = 2

    def destinations(stem: str) -> tuple[Path, ...]:
        values: list[Path] = []
        for output_format in formats:
            original_suffix = (
                " — transcrição"
                if has_improved and output_format in {"docx", "txt"}
                else ""
            )
            values.append(folder / f"{stem}{original_suffix}.{output_format}")
            if has_improved and output_format in {"docx", "txt"}:
                values.append(folder / f"{stem} — texto melhorado.{output_format}")
        return tuple(values)

    while any(path.exists() for path in destinations(candidate)):
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


def _with_cost_record(transcript: Transcript, record: CostRecord) -> Transcript:
    metadata = {**dict(transcript.metadata), "cost_record": record.to_dict()}
    return replace(transcript, metadata=metadata)


def _editorial_context(
    index: int,
    blocks: Sequence[EditorialBlock],
) -> str | None:
    if index <= 0:
        return None
    previous = blocks[index - 1].text.strip()
    return previous[-800:] or None


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


def overall_progress(manifest: JobManifest, stage: str | None = None) -> float:
    """Return monotonic progress for every stage requested by the job."""

    current_stage = stage or str(manifest.metadata.get("pipeline_stage") or "")
    improve = bool(manifest.settings.get("improve_with_ai", False))
    if manifest.status == JobStatus.COMPLETED:
        return 1.0
    if current_stage in {"improvement_exported", "completed"}:
        return 0.99
    if current_stage == "cancelled" and bool(manifest.metadata.get("original_ready")):
        return 0.65 if improve else 0.95
    if current_stage in {"exporting_improved", "improved_export_failed"}:
        return 0.97
    if current_stage == "improvement_complete":
        return 0.95
    if current_stage == "improving":
        total = max(1, int(manifest.metadata.get("editorial_total") or 1))
        completed = min(
            total,
            max(0, int(manifest.metadata.get("editorial_completed") or 0)),
        )
        return 0.65 + 0.30 * completed / total
    if current_stage == "original_exported":
        return 0.65 if improve else 0.95
    if current_stage in {"exporting_original", "original_export_failed"}:
        return 0.62 if improve else 0.93
    if current_stage == "transcription_complete":
        return 0.60 if improve else 0.90
    scale = 0.60 if improve else 0.90
    return min(scale, max(0.0, manifest.progress * scale))


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="milliseconds")


def _error_code(exc: BaseException) -> str:
    if isinstance(exc, ProviderError):
        return exc.code
    if isinstance(exc, OperationCancelled):
        return "cancelled"
    return type(exc).__name__.casefold()


def _saved_output_groups(
    manifest: JobManifest,
) -> dict[str, tuple[Path, ...]]:
    raw = manifest.metadata.get("output_groups")
    source = raw if isinstance(raw, Mapping) else {}
    return {
        key: tuple(
            Path(str(path))
            for path in source.get(key, ())
        )
        for key in ("improved", "original", "captions")
    }


def _flatten_output_groups(
    groups: Mapping[str, Sequence[Path]],
) -> tuple[Path, ...]:
    return tuple(
        Path(path)
        for key in ("original", "captions", "improved")
        for path in groups.get(key, ())
    )


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
    if isinstance(exc, EditorialValidationError):
        return (
            "A melhoria não devolveu um texto utilizável. "
            "A transcrição original está preservada."
        )
    if isinstance(exc, PipelineError):
        return str(exc)
    if isinstance(exc, MediaDependencyError):
        return (
            "Não foi possível preparar esta mídia. Atualize o São Francisco "
            "e tente novamente."
        )
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
    "overall_progress",
    "transcript_to_markdown",
]
