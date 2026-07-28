"""Crash-resistant job manifests and per-chunk result persistence."""

from __future__ import annotations

import json
import os
import re
import tempfile
import threading
import uuid
from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from types import MappingProxyType
from typing import Any

from .models import ChunkSpec, Transcript

MANIFEST_SCHEMA_VERSION = 1
_SAFE_JOB_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


class JobStoreError(RuntimeError):
    """Base class for persisted-job errors."""


class JobNotFoundError(JobStoreError):
    """The requested job does not exist."""


class CorruptJobError(JobStoreError):
    """A manifest or saved chunk result cannot be decoded."""


class JobStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="milliseconds")


@dataclass(frozen=True, slots=True)
class JobManifest:
    """Small, atomic state record for a resumable transcription job."""

    job_id: str
    source: str
    chunks: tuple[ChunkSpec, ...]
    provider: str
    model: str
    language: str | None = None
    status: JobStatus = JobStatus.PENDING
    completed_chunks: frozenset[int] = frozenset()
    chunk_errors: Mapping[int, str] = field(default_factory=dict, compare=False)
    settings: Mapping[str, Any] = field(default_factory=dict, compare=False)
    metadata: Mapping[str, Any] = field(default_factory=dict, compare=False)
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)
    schema_version: int = MANIFEST_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not _SAFE_JOB_ID.fullmatch(self.job_id):
            raise ValueError("job_id contains unsafe characters")
        chunks = tuple(sorted(self.chunks, key=lambda chunk: chunk.index))
        if [chunk.index for chunk in chunks] != list(range(len(chunks))):
            raise ValueError("chunk indices must be contiguous and start at zero")
        completed = frozenset(int(index) for index in self.completed_chunks)
        valid_indices = {chunk.index for chunk in chunks}
        if not completed <= valid_indices:
            raise ValueError("completed_chunks contains an unknown chunk")
        errors = {int(index): str(message) for index, message in self.chunk_errors.items()}
        if not set(errors) <= valid_indices:
            raise ValueError("chunk_errors contains an unknown chunk")
        object.__setattr__(self, "chunks", chunks)
        object.__setattr__(self, "provider", self.provider.strip())
        object.__setattr__(self, "model", self.model.strip())
        object.__setattr__(self, "language", self.language.strip() if self.language else None)
        object.__setattr__(self, "status", JobStatus(self.status))
        object.__setattr__(self, "completed_chunks", completed)
        object.__setattr__(self, "chunk_errors", MappingProxyType(errors))
        object.__setattr__(self, "settings", MappingProxyType(dict(self.settings)))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))
        if self.schema_version != MANIFEST_SCHEMA_VERSION:
            raise ValueError(f"unsupported manifest schema {self.schema_version}")

    @property
    def progress(self) -> float:
        if not self.chunks:
            return 1.0
        return len(self.completed_chunks) / len(self.chunks)

    @property
    def pending_chunks(self) -> tuple[ChunkSpec, ...]:
        return tuple(
            chunk for chunk in self.chunks if chunk.index not in self.completed_chunks
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "job_id": self.job_id,
            "source": self.source,
            "chunks": [chunk.to_dict() for chunk in self.chunks],
            "provider": self.provider,
            "model": self.model,
            "language": self.language,
            "status": self.status.value,
            "completed_chunks": sorted(self.completed_chunks),
            "chunk_errors": {str(key): value for key, value in self.chunk_errors.items()},
            "settings": dict(self.settings),
            "metadata": dict(self.metadata),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> JobManifest:
        try:
            return cls(
                schema_version=int(value.get("schema_version", 0)),
                job_id=str(value["job_id"]),
                source=str(value["source"]),
                chunks=tuple(ChunkSpec.from_dict(item) for item in value["chunks"]),
                provider=str(value["provider"]),
                model=str(value["model"]),
                language=value.get("language"),
                status=JobStatus(value.get("status", JobStatus.PENDING.value)),
                completed_chunks=frozenset(
                    int(index) for index in value.get("completed_chunks", ())
                ),
                chunk_errors={
                    int(index): str(message)
                    for index, message in value.get("chunk_errors", {}).items()
                },
                settings=value.get("settings", {}),
                metadata=value.get("metadata", {}),
                created_at=str(value["created_at"]),
                updated_at=str(value["updated_at"]),
            )
        except (KeyError, TypeError, ValueError) as error:
            raise CorruptJobError(f"invalid job manifest: {error}") from error


class JobStore:
    """Store each job in an exclusive directory beneath ``root``.

    Chunk results are written before their completion bit is committed to the
    manifest.  On load, orphaned result files are reconciled automatically,
    allowing a job to resume even if the process stopped between those writes.
    """

    def __init__(self, root: str | os.PathLike[str]) -> None:
        self.root = Path(root).expanduser().resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()

    @staticmethod
    def new_job_id() -> str:
        return uuid.uuid4().hex

    def job_directory(self, job_id: str) -> Path:
        self._validate_job_id(job_id)
        return self.root / job_id

    def manifest_path(self, job_id: str) -> Path:
        return self.job_directory(job_id) / "manifest.json"

    def chunk_result_path(self, job_id: str, chunk_index: int) -> Path:
        if chunk_index < 0:
            raise ValueError("chunk_index must not be negative")
        return self.job_directory(job_id) / "results" / f"chunk-{chunk_index:06d}.json"

    def original_result_path(self, job_id: str) -> Path:
        return self.job_directory(job_id) / "assembled" / "original.json"

    def editorial_plan_path(self, job_id: str) -> Path:
        return self.job_directory(job_id) / "editorial" / "plan.json"

    def editorial_result_path(self, job_id: str, block_id: str) -> Path:
        self._validate_unit_id(block_id)
        return self.job_directory(job_id) / "editorial" / "results" / f"{block_id}.json"

    def improved_result_path(self, job_id: str) -> Path:
        return self.job_directory(job_id) / "assembled" / "improved.json"

    def create_job(
        self,
        *,
        source: str,
        chunks: tuple[ChunkSpec, ...] | list[ChunkSpec],
        provider: str,
        model: str,
        language: str | None = None,
        settings: Mapping[str, Any] | None = None,
        metadata: Mapping[str, Any] | None = None,
        job_id: str | None = None,
    ) -> JobManifest:
        identifier = job_id or self.new_job_id()
        directory = self.job_directory(identifier)
        with self._lock:
            directory.mkdir(parents=True, exist_ok=False)
            (directory / "results").mkdir()
            manifest = JobManifest(
                job_id=identifier,
                source=source,
                chunks=tuple(chunks),
                provider=provider,
                model=model,
                language=language,
                settings=settings or {},
                metadata=metadata or {},
            )
            self._write_manifest(manifest)
        return manifest

    def load_job(self, job_id: str, *, reconcile: bool = True) -> JobManifest:
        path = self.manifest_path(job_id)
        if not path.is_file():
            raise JobNotFoundError(f"job {job_id!r} does not exist")
        with self._lock:
            try:
                value = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError) as error:
                raise CorruptJobError(f"cannot read {path}: {error}") from error
            manifest = JobManifest.from_dict(value)
            if manifest.job_id != job_id:
                raise CorruptJobError("manifest job_id does not match its directory")
            if reconcile:
                manifest = self._reconcile(manifest)
            return manifest

    resume_job = load_job

    def save_job(self, manifest: JobManifest) -> JobManifest:
        if not self.job_directory(manifest.job_id).is_dir():
            raise JobNotFoundError(f"job {manifest.job_id!r} does not exist")
        updated = replace(manifest, updated_at=_now())
        with self._lock:
            self._write_manifest(updated)
        return updated

    def set_status(
        self,
        job_id: str,
        status: JobStatus,
        *,
        message: str | None = None,
    ) -> JobManifest:
        with self._lock:
            manifest = self.load_job(job_id)
            metadata = dict(manifest.metadata)
            if message:
                metadata["status_message"] = message
            updated = replace(
                manifest,
                status=JobStatus(status),
                metadata=metadata,
                updated_at=_now(),
            )
            self._write_manifest(updated)
            return updated

    def save_chunk_result(
        self,
        job_id: str,
        chunk_index: int,
        transcript: Transcript,
    ) -> JobManifest:
        """Atomically persist one result and mark its chunk complete."""

        with self._lock:
            manifest = self.load_job(job_id)
            valid_indices = {chunk.index for chunk in manifest.chunks}
            if chunk_index not in valid_indices:
                raise IndexError(f"unknown chunk {chunk_index}")
            result_path = self.chunk_result_path(job_id, chunk_index)
            self._atomic_json_write(result_path, transcript.to_dict())
            completed = manifest.completed_chunks | {chunk_index}
            errors = dict(manifest.chunk_errors)
            errors.pop(chunk_index, None)
            updated = replace(
                manifest,
                completed_chunks=frozenset(completed),
                chunk_errors=errors,
                # Completion belongs to the final export, not to the last
                # provider response.  This keeps crash recovery sequential.
                status=JobStatus.RUNNING,
                updated_at=_now(),
            )
            self._write_manifest(updated)
            return updated

    mark_chunk_complete = save_chunk_result

    def mark_chunk_failed(
        self, job_id: str, chunk_index: int, message: str
    ) -> JobManifest:
        with self._lock:
            manifest = self.load_job(job_id)
            if chunk_index not in {chunk.index for chunk in manifest.chunks}:
                raise IndexError(f"unknown chunk {chunk_index}")
            errors = dict(manifest.chunk_errors)
            errors[chunk_index] = message
            updated = replace(
                manifest,
                chunk_errors=errors,
                status=JobStatus.FAILED,
                updated_at=_now(),
            )
            self._write_manifest(updated)
            return updated

    def load_chunk_result(self, job_id: str, chunk_index: int) -> Transcript:
        path = self.chunk_result_path(job_id, chunk_index)
        if not path.is_file():
            raise JobNotFoundError(
                f"job {job_id!r} has no saved result for chunk {chunk_index}"
            )
        try:
            return Transcript.from_dict(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, UnicodeError, json.JSONDecodeError, TypeError, ValueError) as error:
            raise CorruptJobError(f"cannot read {path}: {error}") from error

    def load_completed_results(self, job_id: str) -> dict[int, Transcript]:
        manifest = self.load_job(job_id)
        return {
            index: self.load_chunk_result(job_id, index)
            for index in sorted(manifest.completed_chunks)
        }

    def pending_chunks(self, job_id: str) -> tuple[ChunkSpec, ...]:
        return self.load_job(job_id).pending_chunks

    def save_original_result(self, job_id: str, transcript: Transcript) -> None:
        with self._lock:
            self.load_job(job_id)
            self._atomic_json_write(self.original_result_path(job_id), transcript.to_dict())

    def load_original_result(self, job_id: str) -> Transcript:
        return self._load_transcript_file(
            self.original_result_path(job_id),
            f"job {job_id!r} has no assembled original",
        )

    def has_original_result(self, job_id: str) -> bool:
        return self.original_result_path(job_id).is_file()

    def save_editorial_plan(
        self, job_id: str, value: Mapping[str, Any]
    ) -> None:
        with self._lock:
            self.load_job(job_id)
            self._atomic_json_write(self.editorial_plan_path(job_id), value)

    def load_editorial_plan(self, job_id: str) -> dict[str, Any]:
        return self._load_json_object(
            self.editorial_plan_path(job_id),
            f"job {job_id!r} has no editorial plan",
        )

    def has_editorial_plan(self, job_id: str) -> bool:
        return self.editorial_plan_path(job_id).is_file()

    def save_editorial_result(
        self,
        job_id: str,
        block_id: str,
        value: Mapping[str, Any],
    ) -> None:
        with self._lock:
            self.load_job(job_id)
            self._atomic_json_write(
                self.editorial_result_path(job_id, block_id),
                value,
            )

    def load_editorial_results(self, job_id: str) -> dict[str, dict[str, Any]]:
        root = self.job_directory(job_id) / "editorial" / "results"
        if not root.is_dir():
            return {}
        results: dict[str, dict[str, Any]] = {}
        for path in sorted(root.glob("*.json")):
            self._validate_unit_id(path.stem)
            results[path.stem] = self._load_json_object(
                path, f"editorial result {path.stem!r} is missing"
            )
        return results

    def save_improved_result(self, job_id: str, text: str) -> None:
        with self._lock:
            self.load_job(job_id)
            self._atomic_json_write(
                self.improved_result_path(job_id),
                {"text": text},
            )

    def load_improved_result(self, job_id: str) -> str:
        value = self._load_json_object(
            self.improved_result_path(job_id),
            f"job {job_id!r} has no assembled improved text",
        )
        return str(value.get("text") or "").strip()

    def has_improved_result(self, job_id: str) -> bool:
        return self.improved_result_path(job_id).is_file()

    def _reconcile(self, manifest: JobManifest) -> JobManifest:
        discovered = {
            chunk.index
            for chunk in manifest.chunks
            if self.chunk_result_path(manifest.job_id, chunk.index).is_file()
        }
        if discovered == manifest.completed_chunks:
            return manifest

        # Decode before trusting an orphaned result as complete.
        for index in discovered - manifest.completed_chunks:
            self.load_chunk_result(manifest.job_id, index)
        status = (
            JobStatus.RUNNING
            if len(discovered) == len(manifest.chunks)
            else manifest.status
        )
        updated = replace(
            manifest,
            completed_chunks=frozenset(discovered),
            status=status,
            updated_at=_now(),
        )
        self._write_manifest(updated)
        return updated

    def _load_transcript_file(self, path: Path, missing_message: str) -> Transcript:
        if not path.is_file():
            raise JobNotFoundError(missing_message)
        try:
            return Transcript.from_dict(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, UnicodeError, json.JSONDecodeError, TypeError, ValueError) as error:
            raise CorruptJobError(f"cannot read {path}: {error}") from error

    @staticmethod
    def _load_json_object(path: Path, missing_message: str) -> dict[str, Any]:
        if not path.is_file():
            raise JobNotFoundError(missing_message)
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            raise CorruptJobError(f"cannot read {path}: {error}") from error
        if not isinstance(value, dict):
            raise CorruptJobError(f"{path} does not contain an object")
        return value

    def _write_manifest(self, manifest: JobManifest) -> None:
        self._atomic_json_write(self.manifest_path(manifest.job_id), manifest.to_dict())

    @staticmethod
    def _atomic_json_write(path: Path, value: Mapping[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
        )
        temporary = Path(temporary_name)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
                json.dump(value, stream, ensure_ascii=False, indent=2, sort_keys=True)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, path)
            JobStore._sync_directory(path.parent)
        except BaseException:
            temporary.unlink(missing_ok=True)
            raise

    @staticmethod
    def _sync_directory(directory: Path) -> None:
        flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
        try:
            descriptor = os.open(directory, flags)
        except OSError:
            return
        try:
            os.fsync(descriptor)
        except OSError:
            pass
        finally:
            os.close(descriptor)

    @staticmethod
    def _validate_job_id(job_id: str) -> None:
        if not _SAFE_JOB_ID.fullmatch(job_id):
            raise ValueError("job_id contains unsafe characters")

    @staticmethod
    def _validate_unit_id(unit_id: str) -> None:
        if not _SAFE_JOB_ID.fullmatch(unit_id):
            raise ValueError("unit_id contains unsafe characters")
