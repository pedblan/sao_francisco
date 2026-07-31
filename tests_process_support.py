"""Top-level multiprocessing targets used by spawn-based unit tests."""

from __future__ import annotations

import time
from collections.abc import Mapping
from typing import Any


def disposable_executor_probe(
    raw_task: Mapping[str, Any],
    _raw_config: Mapping[str, Any],
    message_queue: Any,
    _cancel_event: Any,
) -> None:
    """Ignore cancellation for one source and finish immediately for the next."""

    if str(raw_task.get("source") or "") == "stuck":
        time.sleep(30)
        return
    message_queue.put(
        {
            "kind": "succeeded",
            "key": str(raw_task.get("key") or ""),
            "job_id": "probe-result",
        }
    )


__all__ = ["disposable_executor_probe"]
