"""Offline smoke test for the multiprocessing boundary used by frozen apps."""

from __future__ import annotations

import os
import sys
import time
from multiprocessing import get_context
from queue import Empty
from typing import Any


def _probe_target(mode: str, message_queue: Any, _cancel_event: Any) -> None:
    """Provide an importable spawn target without touching credentials or the network."""

    if mode == "stuck":
        time.sleep(30)
        return
    message_queue.put({"kind": "succeeded", "pid": os.getpid()})


def _successful_probe(timeout_seconds: float) -> None:
    context = get_context("spawn")
    message_queue = context.Queue()
    cancel_event = context.Event()
    process = context.Process(
        target=_probe_target,
        args=("success", message_queue, cancel_event),
        name="sao-francisco-process-smoke-success",
        daemon=True,
    )
    try:
        process.start()
        try:
            message = message_queue.get(timeout=timeout_seconds)
        except Empty as exc:
            raise RuntimeError("o subprocesso não devolveu o resultado esperado") from exc
        process.join(timeout=timeout_seconds)
        if process.is_alive():
            process.terminate()
            process.join(timeout=timeout_seconds)
            raise RuntimeError("o subprocesso concluído permaneceu vivo")
        if not isinstance(message, dict) or message.get("kind") != "succeeded":
            raise RuntimeError("o subprocesso devolveu uma mensagem inválida")
        if process.exitcode != 0:
            raise RuntimeError(
                f"o subprocesso terminou com código inesperado: {process.exitcode}"
            )
    finally:
        if process.is_alive():
            process.terminate()
            process.join(timeout=timeout_seconds)
        if process.is_alive() and hasattr(process, "kill"):
            process.kill()
            process.join(timeout=timeout_seconds)
        message_queue.close()
        message_queue.join_thread()
        process.close()


def _forced_cancellation_probe(
    *,
    start_timeout_seconds: float,
    kill_timeout_seconds: float,
) -> None:
    context = get_context("spawn")
    message_queue = context.Queue()
    cancel_event = context.Event()
    process = context.Process(
        target=_probe_target,
        args=("stuck", message_queue, cancel_event),
        name="sao-francisco-process-smoke-stuck",
        daemon=True,
    )
    try:
        process.start()
        deadline = time.monotonic() + start_timeout_seconds
        while process.pid is None and time.monotonic() < deadline:
            time.sleep(0.01)
        if process.pid is None or not process.is_alive():
            raise RuntimeError("o subprocesso incooperativo não chegou a iniciar")

        cancel_event.set()
        process.terminate()
        process.join(timeout=kill_timeout_seconds)
        if process.is_alive() and hasattr(process, "kill"):
            process.kill()
            process.join(timeout=kill_timeout_seconds)
        if process.is_alive():
            raise RuntimeError("o subprocesso incooperativo não pôde ser encerrado")
    finally:
        if process.is_alive():
            process.terminate()
            process.join(timeout=kill_timeout_seconds)
        if process.is_alive() and hasattr(process, "kill"):
            process.kill()
            process.join(timeout=kill_timeout_seconds)
        message_queue.close()
        message_queue.join_thread()
        process.close()


def run_process_smoke_test() -> int:
    """Exercise spawn, forced termination and reuse with no external effects."""

    try:
        _successful_probe(10)
        _forced_cancellation_probe(
            start_timeout_seconds=10,
            kill_timeout_seconds=5,
        )
        _successful_probe(10)
    except BaseException as exc:
        print(f"Falha no smoke do subprocesso: {exc}", file=sys.stderr)
        return 1
    print("Smoke do subprocesso concluído.")
    return 0


__all__ = ["run_process_smoke_test"]
