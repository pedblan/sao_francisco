from __future__ import annotations

import re
from collections.abc import Iterable
from contextlib import suppress
from decimal import Decimal, InvalidOperation
from typing import Any

from sao_francisco.core.cancellation import CancellationToken
from sao_francisco.core.costs import UsageMetrics
from sao_francisco.core.models import Segment, Transcript, WordTiming
from sao_francisco.providers.base import ProviderError, ProviderRequest

OPENAI_UPLOAD_LIMIT = 25_000_000
_SENTENCE_BOUNDARY_RE = re.compile(r"(?<=[.!?…])\s+|\n+")


class OpenAIProvider:
    provider_id = "openai"

    def __init__(self, api_key: str) -> None:
        if not api_key.strip():
            raise ProviderError(
                code="missing_key",
                message="Configure uma chave da OpenAI antes de transcrever.",
                retryable=False,
            )
        self._api_key = api_key.strip()

    def _client(self) -> Any:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ProviderError(
                code="missing_dependency",
                message="O componente da OpenAI não foi instalado corretamente.",
                retryable=False,
            ) from exc
        return OpenAI(api_key=self._api_key, timeout=1800.0, max_retries=0)

    def validate_credential(self) -> None:
        client = self._client()
        try:
            client.models.list()
        except Exception as exc:
            raise _classify_openai_error(exc) from exc
        finally:
            with suppress(Exception):
                client.close()

    def transcribe(
        self,
        request: ProviderRequest,
        cancellation: CancellationToken,
    ) -> Transcript:
        cancellation.raise_if_cancelled()
        try:
            size = request.audio_path.stat().st_size
        except OSError as exc:
            raise ProviderError(
                code="missing_audio",
                message="A parte de áudio preparada não pôde ser aberta.",
                retryable=False,
            ) from exc
        if size >= OPENAI_UPLOAD_LIMIT:
            raise ProviderError(
                code="upload_too_large",
                message=(
                    "Uma parte excedeu o limite de upload da OpenAI. "
                    "O trabalho pode ser retomado após subdividi-la."
                ),
                retryable=False,
            )

        parameters: dict[str, Any] = {
            "model": request.model_id,
        }
        if request.language:
            parameters["language"] = request.language
        if request.model_id == "whisper-1":
            parameters.update(
                response_format="verbose_json",
                timestamp_granularities=["segment", "word"],
            )
            if request.context_prompt:
                parameters["prompt"] = request.context_prompt[-1800:]
        elif request.model_id == "gpt-4o-transcribe-diarize":
            parameters.update(
                response_format="diarized_json",
                chunking_strategy="auto",
            )
        else:
            parameters["response_format"] = "json"
            if request.context_prompt:
                parameters["prompt"] = request.context_prompt[-4000:]

        client = self._client()
        unregister = cancellation.add_cancel_callback(client.close)
        try:
            with request.audio_path.open("rb") as audio:
                response = client.audio.transcriptions.create(
                    file=audio,
                    **parameters,
                )
        except Exception as exc:
            cancellation.raise_if_cancelled()
            raise _classify_openai_error(exc) from exc
        finally:
            unregister()
            with suppress(Exception):
                client.close()
        cancellation.raise_if_cancelled()
        return _parse_response(response, request.duration, request.model_id)


def _parse_response(response: Any, duration: float, model_id: str) -> Transcript:
    data = _as_mapping(response)
    raw_segments = data.get("segments") or []
    if raw_segments:
        segments = _segments_from_response(raw_segments, data.get("words") or ())
        timestamp_kind = "provider"
    else:
        text = str(data.get("text") or getattr(response, "text", "")).strip()
        segments = _estimated_text_segments(text, duration) if text else ()
        timestamp_kind = "estimated"
    usage = _usage_metrics(_as_mapping(data.get("usage")))
    return Transcript(
        segments=segments,
        language=_optional_text(data.get("language")),
        duration=max(duration, max((segment.end for segment in segments), default=0.0)),
        metadata={
            "provider": "openai",
            "model": model_id,
            "timestamps": timestamp_kind,
            "usage": usage.to_dict(),
        },
    )


def _estimated_text_segments(text: str, duration: float) -> tuple[Segment, ...]:
    """Distribute text-only responses into readable, explicitly estimated cues."""

    units: list[str] = []
    for sentence in _SENTENCE_BOUNDARY_RE.split(text.strip()):
        words = sentence.split()
        units.extend(
            " ".join(words[index : index + 28])
            for index in range(0, len(words), 28)
        )
    if not units:
        return ()

    bounded_duration = max(float(duration), 0.001)
    weights = [max(1, len(unit.split())) for unit in units]
    total_weight = sum(weights)
    elapsed_weight = 0
    segments: list[Segment] = []
    for index, (unit, weight) in enumerate(zip(units, weights, strict=True)):
        start = bounded_duration * elapsed_weight / total_weight
        elapsed_weight += weight
        end = (
            bounded_duration
            if index == len(units) - 1
            else bounded_duration * elapsed_weight / total_weight
        )
        segments.append(
            Segment(
                start=start,
                end=end,
                text=unit,
                metadata={"timestamps": "estimated"},
            )
        )
    return tuple(segments)


def _segments_from_response(
    raw_segments: Iterable[Any],
    raw_words: Iterable[Any],
) -> tuple[Segment, ...]:
    words = tuple(
        WordTiming(
            start=float(_value(word, "start", 0.0)),
            end=float(_value(word, "end", _value(word, "start", 0.0))),
            text=str(_value(word, "word", _value(word, "text", ""))).strip(),
        )
        for word in raw_words
        if str(_value(word, "word", _value(word, "text", ""))).strip()
    )
    segments: list[Segment] = []
    for raw in raw_segments:
        text = str(_value(raw, "text", "")).strip()
        if not text:
            continue
        start = max(0.0, float(_value(raw, "start", 0.0)))
        end = max(start, float(_value(raw, "end", start)))
        contained_words = tuple(
            word
            for word in words
            if word.start >= start - 1e-4 and word.end <= end + 1e-4
        )
        segments.append(
            Segment(
                start=start,
                end=end,
                text=text,
                speaker=_optional_text(_value(raw, "speaker", None)),
                words=contained_words,
            )
        )
    return tuple(segments)


def _as_mapping(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    dump = getattr(value, "model_dump", None)
    if callable(dump):
        dumped = dump()
        if isinstance(dumped, dict):
            return dumped
    result: dict[str, Any] = {}
    for field in ("text", "segments", "words", "language", "duration", "usage", "model"):
        if hasattr(value, field):
            result[field] = getattr(value, field)
    return result


def _usage_metrics(value: dict[str, Any]) -> UsageMetrics:
    if str(value.get("type") or "").casefold() == "duration":
        return UsageMetrics(duration_seconds=_optional_number(value.get("seconds")))
    return UsageMetrics(
        input_tokens=_optional_int(value.get("input_tokens")),
        output_tokens=_optional_int(value.get("output_tokens")),
        total_tokens=_optional_int(value.get("total_tokens")),
    )


def _optional_int(value: Any) -> int | None:
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    return number if number >= 0 else None


def _optional_number(value: Any) -> Decimal | None:
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None
    return number if number >= 0 else None


def _value(value: Any, field: str, default: Any) -> Any:
    if isinstance(value, dict):
        return value.get(field, default)
    return getattr(value, field, default)


def _optional_text(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None


def _classify_openai_error(exc: Exception) -> ProviderError:
    name = type(exc).__name__
    status = getattr(exc, "status_code", None)
    if name == "AuthenticationError" or status == 401:
        return ProviderError(
            code="authentication",
            message="A OpenAI não aceitou a chave configurada.",
            retryable=False,
        )
    if name == "PermissionDeniedError" or status == 403:
        return ProviderError(
            code="permission",
            message="A chave não tem acesso ao modelo de transcrição escolhido.",
            retryable=False,
        )
    if name == "RateLimitError" or status == 429:
        return ProviderError(
            code="rate_limit",
            message=(
                "A OpenAI informou limite de uso ou cota indisponível. "
                "Confira faturamento e tente retomar depois."
            ),
            retryable=True,
        )
    if name in {"APITimeoutError", "APIConnectionError"}:
        return ProviderError(
            code="connection",
            message="A conexão com a OpenAI foi interrompida.",
            retryable=True,
        )
    if isinstance(status, int) and status >= 500:
        return ProviderError(
            code="provider_unavailable",
            message="A OpenAI está temporariamente indisponível.",
            retryable=True,
        )
    return ProviderError(
        code="provider_error",
        message="A OpenAI não conseguiu transcrever esta parte.",
        retryable=False,
    )
