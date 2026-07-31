from __future__ import annotations

import json
import time
from contextlib import suppress
from typing import Any

from sao_francisco.core.cancellation import CancellationToken, OperationCancelled
from sao_francisco.core.costs import UsageMetrics
from sao_francisco.core.models import Segment, Transcript
from sao_francisco.providers.base import ProviderError, ProviderRequest

TRANSCRIPT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "language": {"type": "string"},
        "segments": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "start": {"type": "number"},
                    "end": {"type": "number"},
                    "speaker": {"type": "string"},
                    "text": {"type": "string"},
                },
                "required": ["start", "end", "speaker", "text"],
            },
        },
    },
    "required": ["language", "segments"],
}


class GeminiProvider:
    provider_id = "gemini"

    def __init__(self, api_key: str) -> None:
        if not api_key.strip():
            raise ProviderError(
                code="missing_key",
                message="Configure uma chave do Gemini antes de transcrever.",
                retryable=False,
            )
        self._api_key = api_key.strip()

    def _client(self) -> Any:
        try:
            from google import genai
            from google.genai import types
        except ImportError as exc:
            raise ProviderError(
                code="missing_dependency",
                message="O componente do Gemini não foi instalado corretamente.",
                retryable=False,
            ) from exc
        return genai.Client(
            api_key=self._api_key,
            http_options=types.HttpOptions(
                retry_options=types.HttpRetryOptions(attempts=1),
            ),
        )

    def validate_credential(self) -> None:
        client = self._client()
        try:
            next(iter(client.models.list()))
        except Exception as exc:
            raise _classify_gemini_error(exc) from exc
        finally:
            _close_client(client)

    def transcribe(
        self,
        request: ProviderRequest,
        cancellation: CancellationToken,
    ) -> Transcript:
        cancellation.raise_if_cancelled()
        client = self._client()
        unregister = cancellation.add_cancel_callback(lambda: _close_client(client))
        uploaded: Any | None = None
        try:
            uploaded = client.files.upload(file=str(request.audio_path))
            uploaded = _wait_until_ready(client, uploaded, cancellation)
            prompt = _prompt(request)
            interaction = client.interactions.create(
                model=request.model_id,
                input=[
                    {"type": "text", "text": prompt},
                    {
                        "type": "audio",
                        "uri": uploaded.uri,
                        "mime_type": uploaded.mime_type,
                    },
                ],
                response_format=[
                    {
                        "type": "text",
                        "mime_type": "application/json",
                        "schema": TRANSCRIPT_SCHEMA,
                    }
                ],
            )
            cancellation.raise_if_cancelled()
            return _parse_interaction(
                interaction,
                duration=request.duration,
                model_id=request.model_id,
            )
        except OperationCancelled:
            raise
        except ProviderError:
            cancellation.raise_if_cancelled()
            raise
        except Exception as exc:
            cancellation.raise_if_cancelled()
            raise _classify_gemini_error(exc) from exc
        finally:
            if uploaded is not None:
                name = getattr(uploaded, "name", None)
                if name:
                    with suppress(Exception):
                        client.files.delete(name=name)
            unregister()
            _close_client(client)


def _close_client(client: Any) -> None:
    close = getattr(client, "close", None)
    if callable(close):
        with suppress(Exception):
            close()


def _wait_until_ready(
    client: Any,
    uploaded: Any,
    cancellation: CancellationToken,
) -> Any:
    deadline = time.monotonic() + 120
    current = uploaded
    while time.monotonic() < deadline:
        cancellation.raise_if_cancelled()
        state = getattr(getattr(current, "state", None), "name", None)
        if state in {None, "ACTIVE", "SUCCEEDED"}:
            return current
        if state in {"FAILED", "ERROR"}:
            raise ProviderError(
                code="upload_failed",
                message="O Gemini não conseguiu preparar a parte enviada.",
                retryable=True,
            )
        time.sleep(0.5)
        current = client.files.get(name=current.name)
    raise ProviderError(
        code="upload_timeout",
        message="O Gemini demorou demais para preparar a parte enviada.",
        retryable=True,
    )


def _prompt(request: ProviderRequest) -> str:
    language = request.language or "o idioma falado"
    context = (
        f"\nContexto final da parte anterior, apenas para continuidade:\n"
        f"{request.context_prompt[-3000:]}"
        if request.context_prompt
        else ""
    )
    return (
        "Transcreva fielmente todo o áudio, sem resumir, traduzir ou explicar. "
        f"Use {language}. Retorne segmentos cronológicos com start e end em segundos "
        "a partir do início deste arquivo. Identifique falantes como Falante 1, "
        "Falante 2 etc. quando houver evidência; use Falante quando não for possível "
        "distingui-los. Preserve números, nomes, hesitações e pontuação audível. "
        "Não invente trechos para silêncio ou áudio incompreensível."
        f"{context}"
    )


def _parse_interaction(
    interaction: Any,
    *,
    duration: float,
    model_id: str,
) -> Transcript:
    output = getattr(interaction, "output_text", None)
    if output is None:
        output = getattr(interaction, "outputText", None)
    if isinstance(output, str):
        try:
            data = json.loads(output)
        except json.JSONDecodeError as exc:
            raise ProviderError(
                code="invalid_response",
                message="O Gemini devolveu uma transcrição em formato inválido.",
                retryable=True,
            ) from exc
    elif isinstance(output, dict):
        data = output
    else:
        raise ProviderError(
            code="invalid_response",
            message="O Gemini não devolveu uma transcrição utilizável.",
            retryable=True,
        )

    segments: list[Segment] = []
    last_start = 0.0
    for raw in data.get("segments", ()):
        text = str(raw.get("text", "")).strip()
        if not text:
            continue
        start = max(last_start, float(raw.get("start", last_start)))
        end = max(start, min(float(raw.get("end", duration)), duration))
        segments.append(
            Segment(
                start=start,
                end=end,
                text=text,
                speaker=str(raw.get("speaker", "")).strip() or None,
                metadata={"timestamps": "model_generated"},
            )
        )
        last_start = start
    if not segments:
        raise ProviderError(
            code="empty_response",
            message="O Gemini não reconheceu fala nesta parte.",
            retryable=False,
        )
    interaction_data = _as_mapping(interaction)
    usage = _usage_metrics(
        _as_mapping(
            interaction_data.get("usage")
            or interaction_data.get("usage_metadata")
            or interaction_data.get("usageMetadata")
        )
    )
    return Transcript(
        segments=tuple(segments),
        language=str(data.get("language", "")).strip() or None,
        duration=max(duration, max(segment.end for segment in segments)),
        metadata={
            "provider": "gemini",
            "model": model_id,
            "timestamps": "model_generated",
            "usage": usage.to_dict(),
        },
    )


def _as_mapping(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return dict(value)
    dump = getattr(value, "model_dump", None)
    if callable(dump):
        dumped = dump()
        if isinstance(dumped, dict):
            return dumped
    result: dict[str, Any] = {}
    for field in ("usage", "usage_metadata", "usageMetadata", "model"):
        if hasattr(value, field):
            result[field] = getattr(value, field)
    return result


def _usage_metrics(value: dict[str, Any]) -> UsageMetrics:
    return UsageMetrics(
        input_tokens=_first_int(
            value,
            "input_tokens",
            "inputTokenCount",
            "prompt_token_count",
            "promptTokenCount",
        ),
        cached_input_tokens=_first_int(
            value, "cached_input_tokens", "cachedContentTokenCount"
        ),
        output_tokens=_first_int(
            value,
            "output_tokens",
            "outputTokenCount",
            "candidates_token_count",
            "candidatesTokenCount",
        ),
        reasoning_tokens=_first_int(
            value, "reasoning_tokens", "thoughtsTokenCount", "thought_token_count"
        ),
        total_tokens=_first_int(
            value, "total_tokens", "totalTokenCount", "total_token_count"
        ),
        reasoning_in_output=False,
    )


def _first_int(value: dict[str, Any], *names: str) -> int | None:
    for name in names:
        raw = value.get(name)
        if raw is None:
            continue
        try:
            number = int(raw)
        except (TypeError, ValueError):
            continue
        if number >= 0:
            return number
    return None


def _classify_gemini_error(exc: Exception) -> ProviderError:
    status = getattr(exc, "status_code", None)
    code = getattr(exc, "code", status)
    text_code = str(code or "").upper()
    if status == 401 or "UNAUTHENTICATED" in text_code:
        return ProviderError(
            code="authentication",
            message="O Gemini não aceitou a chave configurada.",
            retryable=False,
        )
    if status == 403 or "PERMISSION_DENIED" in text_code:
        return ProviderError(
            code="permission",
            message="A chave não tem acesso ao modelo Gemini escolhido.",
            retryable=False,
        )
    if status == 429 or "RESOURCE_EXHAUSTED" in text_code:
        return ProviderError(
            code="rate_limit",
            message=(
                "O Gemini informou limite de uso ou cota indisponível. "
                "Confira o projeto e tente retomar depois."
            ),
            retryable=True,
        )
    if isinstance(status, int) and status >= 500:
        return ProviderError(
            code="provider_unavailable",
            message="O Gemini está temporariamente indisponível.",
            retryable=True,
        )
    if type(exc).__name__ in {"TimeoutError", "ConnectError"}:
        return ProviderError(
            code="connection",
            message="A conexão com o Gemini foi interrompida.",
            retryable=True,
        )
    return ProviderError(
        code="provider_error",
        message="O Gemini não conseguiu transcrever esta parte.",
        retryable=False,
    )
