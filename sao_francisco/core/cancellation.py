"""Cooperative cancellation shared by media and provider adapters."""

from __future__ import annotations

import threading
from collections.abc import Callable
from contextlib import suppress


class OperationCancelled(RuntimeError):
    """Raised when a cooperative operation has been cancelled."""


class CancellationToken:
    """A thread-safe cancellation signal.

    Cancellation is intentionally cooperative: callers may poll ``cancelled``
    and long-running subprocess calls use :meth:`raise_if_cancelled`.
    """

    def __init__(self) -> None:
        self._event = threading.Event()
        self._lock = threading.Lock()
        self._callbacks: dict[int, Callable[[], None]] = {}
        self._next_callback_id = 0

    @property
    def cancelled(self) -> bool:
        return self._event.is_set()

    def cancel(self) -> None:
        with self._lock:
            if self._event.is_set():
                return
            self._event.set()
            callbacks = tuple(self._callbacks.values())
            self._callbacks.clear()
        for callback in callbacks:
            with suppress(Exception):
                callback()

    def add_cancel_callback(self, callback: Callable[[], None]) -> Callable[[], None]:
        """Run a short callback on cancellation and return an unregister function."""

        with self._lock:
            if self._event.is_set():
                run_now = True
                callback_id = -1
            else:
                run_now = False
                callback_id = self._next_callback_id
                self._next_callback_id += 1
                self._callbacks[callback_id] = callback
        if run_now:
            with suppress(Exception):
                callback()

        def unregister() -> None:
            with self._lock:
                self._callbacks.pop(callback_id, None)

        return unregister

    def raise_if_cancelled(self) -> None:
        if self.cancelled:
            raise OperationCancelled("operation cancelled")


NEVER_CANCELLED = CancellationToken()
