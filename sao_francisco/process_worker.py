"""Disposable process entry point for long-running pipeline work.

Only JSON-safe task settings and local storage paths cross the process
boundary. Credentials are read inside the child from the platform credential
store and are never placed in process arguments or messages.
"""

from __future__ import annotations

import threading
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .core import CancellationToken, JobStore, MediaProcessor, OperationCancelled
from .pipeline import (
    PipelineOptions,
    PipelineProgress,
    PipelineValidationError,
    TranscriptionPipeline,
    _public_error,
)


@dataclass(frozen=True, slots=True)
class PipelineProcessConfig:
    """Filesystem configuration required to reconstruct a pipeline in a child."""

    job_root: Path
    media_work_root: Path
    default_output_root: Path

    def to_mapping(self) -> dict[str, str]:
        return {
            "job_root": str(self.job_root),
            "media_work_root": str(self.media_work_root),
            "default_output_root": str(self.default_output_root),
        }

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> PipelineProcessConfig:
        return cls(
            job_root=Path(str(value["job_root"])),
            media_work_root=Path(str(value["media_work_root"])),
            default_output_root=Path(str(value["default_output_root"])),
        )


def run_pipeline_process(
    raw_task: Mapping[str, Any],
    raw_config: Mapping[str, Any],
    message_queue: Any,
    cancel_event: Any,
) -> None:
    """Run one task and publish durable identifiers instead of large results."""

    key = str(raw_task.get("key") or "")
    last_job_id = str(raw_task.get("resume_job_id") or "")
    cancellation = CancellationToken()

    def forward_cancellation() -> None:
        cancel_event.wait()
        cancellation.cancel()

    threading.Thread(
        target=forward_cancellation,
        name="pipeline-cancellation-bridge",
        daemon=True,
    ).start()

    try:
        config = PipelineProcessConfig.from_mapping(raw_config)
        pipeline = TranscriptionPipeline(
            JobStore(config.job_root),
            media=MediaProcessor(work_root=config.media_work_root),
            default_output_root=config.default_output_root,
        )

        def report(value: PipelineProgress) -> None:
            nonlocal last_job_id
            if value.job_id:
                last_job_id = value.job_id
            message_queue.put(
                {
                    "kind": "progress",
                    "key": key,
                    "job_id": last_job_id,
                    "payload": value.to_ui_dict(),
                }
            )

        resume_job_id = str(raw_task.get("resume_job_id") or "")
        if resume_job_id:
            result = pipeline.resume(
                resume_job_id,
                cancellation=cancellation,
                progress=report,
            )
        else:
            raw_options = raw_task.get("options")
            if not isinstance(raw_options, Mapping):
                raise PipelineValidationError("As opções do trabalho estão ausentes.")
            result = pipeline.run(
                str(raw_task.get("source") or ""),
                PipelineOptions.from_mapping(raw_options),
                cancellation=cancellation,
                progress=report,
            )
        message_queue.put(
            {
                "kind": "succeeded",
                "key": key,
                "job_id": result.manifest.job_id,
            }
        )
    except OperationCancelled:
        message_queue.put(
            {
                "kind": "cancelled",
                "key": key,
                "job_id": last_job_id,
            }
        )
    except BaseException as exc:
        message_queue.put(
            {
                "kind": "failed",
                "key": key,
                "job_id": last_job_id,
                "message": _public_error(exc),
                "error_code": type(exc).__name__.casefold(),
            }
        )


__all__ = ["PipelineProcessConfig", "run_pipeline_process"]
