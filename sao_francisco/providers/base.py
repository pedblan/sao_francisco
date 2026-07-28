from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from sao_francisco.core.cancellation import CancellationToken
from sao_francisco.core.models import Transcript


class ProviderError(RuntimeError):
    def __init__(self, *, code: str, message: str, retryable: bool) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.retryable = retryable


@dataclass(frozen=True, slots=True)
class ProviderRequest:
    audio_path: Path
    model_id: str
    duration: float
    language: str | None = None
    context_prompt: str | None = None


class TranscriptionProvider(Protocol):
    provider_id: str

    def validate_credential(self) -> None: ...

    def transcribe(
        self,
        request: ProviderRequest,
        cancellation: CancellationToken,
    ) -> Transcript: ...
