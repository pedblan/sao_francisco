from .base import (
    ProviderError,
    ProviderRequest,
    TranscriptionProvider,
)
from .editorial import (
    EditorialProvider,
    EditorialRequest,
    EditorialResponse,
    GeminiEditorialProvider,
    OpenAIEditorialProvider,
    editorial_provider_for,
)
from .gemini_provider import GeminiProvider
from .openai_provider import OpenAIProvider

__all__ = [
    "GeminiProvider",
    "GeminiEditorialProvider",
    "EditorialProvider",
    "EditorialRequest",
    "EditorialResponse",
    "OpenAIProvider",
    "OpenAIEditorialProvider",
    "ProviderError",
    "ProviderRequest",
    "TranscriptionProvider",
    "provider_for",
    "editorial_provider_for",
]


def provider_for(provider_id: str, api_key: str) -> TranscriptionProvider:
    if provider_id == "openai":
        return OpenAIProvider(api_key)
    if provider_id == "gemini":
        return GeminiProvider(api_key)
    raise ProviderError(
        code="unknown_provider",
        message="O provedor de transcrição não é reconhecido.",
        retryable=False,
    )
