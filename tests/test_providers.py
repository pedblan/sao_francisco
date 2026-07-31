import json
import threading
from types import SimpleNamespace

from sao_francisco.core import CancellationToken, OperationCancelled
from sao_francisco.providers.base import ProviderRequest
from sao_francisco.providers.editorial import (
    EDITORIAL_INSTRUCTIONS,
    EDITORIAL_TIMEOUT_SECONDS,
    EditorialRequest,
    GeminiEditorialProvider,
    OpenAIEditorialProvider,
)
from sao_francisco.providers.gemini_provider import (
    TRANSCRIPT_SCHEMA,
    GeminiProvider,
    _parse_interaction,
)
from sao_francisco.providers.openai_provider import OpenAIProvider, _parse_response


def test_openai_text_response_becomes_one_bounded_segment() -> None:
    transcript = _parse_response(
        SimpleNamespace(text="Texto reconhecido."),
        duration=42.0,
        model_id="gpt-4o-mini-transcribe",
    )

    assert transcript.text == "Texto reconhecido."
    assert transcript.segments[0].start == 0
    assert transcript.segments[0].end == 42
    assert transcript.metadata["timestamps"] == "estimated"


def test_openai_text_response_distributes_sentences_across_duration() -> None:
    transcript = _parse_response(
        SimpleNamespace(text="Primeira frase. Segunda frase mais longa."),
        duration=12.0,
        model_id="gpt-4o-mini-transcribe",
    )

    assert [segment.text for segment in transcript.segments] == [
        "Primeira frase.",
        "Segunda frase mais longa.",
    ]
    assert transcript.segments[0].start == 0
    assert transcript.segments[-1].end == 12
    assert all(
        segment.metadata["timestamps"] == "estimated"
        for segment in transcript.segments
    )


def test_openai_diarized_response_preserves_speakers() -> None:
    response = {
        "text": "Bom dia. Olá.",
        "segments": [
            {"start": 0, "end": 1.2, "text": "Bom dia.", "speaker": "A"},
            {"start": 1.3, "end": 2.1, "text": "Olá.", "speaker": "B"},
        ],
    }

    transcript = _parse_response(
        response,
        duration=3.0,
        model_id="gpt-4o-transcribe-diarize",
    )

    assert [segment.speaker for segment in transcript.segments] == ["A", "B"]


def test_gemini_structured_response_is_canonicalized() -> None:
    interaction = SimpleNamespace(
        output_text=json.dumps(
            {
                "language": "pt",
                "segments": [
                    {
                        "start": 0,
                        "end": 2.5,
                        "speaker": "Falante 1",
                        "text": "Começamos agora.",
                    }
                ],
            }
        )
    )

    transcript = _parse_interaction(
        interaction,
        duration=3.0,
        model_id="gemini-3.6-flash",
    )

    assert transcript.language == "pt"
    assert transcript.segments[0].speaker == "Falante 1"
    assert transcript.metadata["timestamps"] == "model_generated"


def test_gemini_uses_current_polymorphic_response_format(tmp_path) -> None:
    audio = tmp_path / "parte.mp3"
    audio.write_bytes(b"audio")
    captured = {}
    uploaded = SimpleNamespace(
        name="files/parte",
        uri="https://example.invalid/parte",
        mime_type="audio/mpeg",
        state=None,
    )

    class Files:
        def upload(self, *, file):
            assert file == str(audio)
            return uploaded

        def delete(self, *, name):
            assert name == uploaded.name

    class Interactions:
        def create(self, **values):
            captured.update(values)
            return SimpleNamespace(
                output_text=json.dumps(
                    {
                        "language": "pt",
                        "segments": [
                            {
                                "start": 0,
                                "end": 1,
                                "speaker": "Falante",
                                "text": "Teste.",
                            }
                        ],
                    }
                )
            )

    fake_client = SimpleNamespace(files=Files(), interactions=Interactions())

    class Provider(GeminiProvider):
        def _client(self):
            return fake_client

    result = Provider("segredo").transcribe(
        ProviderRequest(audio, "gemini-3.6-flash", 1.0, "pt"),
        CancellationToken(),
    )

    assert result.text == "Teste."
    assert captured["response_format"] == [
        {
            "type": "text",
            "mime_type": "application/json",
            "schema": TRANSCRIPT_SCHEMA,
        }
    ]


def test_openai_cancellation_closes_an_in_flight_client(tmp_path) -> None:
    audio_path = tmp_path / "parte.mp3"
    audio_path.write_bytes(b"audio")
    started = threading.Event()
    closed = threading.Event()
    outcome: list[BaseException] = []

    class Transcriptions:
        def create(self, **_values):
            started.set()
            closed.wait(2)
            raise RuntimeError("conexão fechada")

    class Client:
        audio = SimpleNamespace(transcriptions=Transcriptions())

        def close(self):
            closed.set()

    client = Client()

    class Provider(OpenAIProvider):
        def _client(self):
            return client

    token = CancellationToken()

    def transcribe() -> None:
        try:
            Provider("segredo").transcribe(
                ProviderRequest(
                    audio_path,
                    "gpt-4o-mini-transcribe",
                    1.0,
                ),
                token,
            )
        except BaseException as exc:
            outcome.append(exc)

    worker = threading.Thread(target=transcribe)
    worker.start()
    assert started.wait(1)
    token.cancel()
    worker.join(2)

    assert not worker.is_alive()
    assert closed.is_set()
    assert len(outcome) == 1
    assert isinstance(outcome[0], OperationCancelled)


def test_gemini_cancellation_closes_an_in_flight_client(tmp_path) -> None:
    audio_path = tmp_path / "parte.mp3"
    audio_path.write_bytes(b"audio")
    started = threading.Event()
    closed = threading.Event()
    outcome: list[BaseException] = []
    uploaded = SimpleNamespace(
        name="files/parte",
        uri="https://example.invalid/parte",
        mime_type="audio/mpeg",
        state=None,
    )

    class Files:
        def upload(self, *, file):
            assert file == str(audio_path)
            return uploaded

        def delete(self, *, name):
            assert name == uploaded.name

    class Interactions:
        def create(self, **_values):
            started.set()
            closed.wait(2)
            raise RuntimeError("conexão fechada")

    class Client:
        files = Files()
        interactions = Interactions()

        def close(self):
            closed.set()

    client = Client()

    class Provider(GeminiProvider):
        def _client(self):
            return client

    token = CancellationToken()

    def transcribe() -> None:
        try:
            Provider("segredo").transcribe(
                ProviderRequest(audio_path, "gemini-3.6-flash", 1.0),
                token,
            )
        except BaseException as exc:
            outcome.append(exc)

    worker = threading.Thread(target=transcribe)
    worker.start()
    assert started.wait(1)
    token.cancel()
    worker.join(2)

    assert not worker.is_alive()
    assert closed.is_set()
    assert len(outcome) == 1
    assert isinstance(outcome[0], OperationCancelled)


def test_openai_editorial_uses_responses_without_tools_or_storage() -> None:
    captured = {}

    class Responses:
        def create(self, **values):
            captured.update(values)
            return SimpleNamespace(
                output_text="Ana: Foram 27 casos.",
                model="gpt-5.6-terra",
                usage={
                    "input_tokens": 100,
                    "input_tokens_details": {
                        "cached_tokens": 20,
                        "cache_write_tokens": 0,
                    },
                    "output_tokens": 40,
                    "output_tokens_details": {"reasoning_tokens": 5},
                    "total_tokens": 140,
                },
            )

    class Client:
        responses = Responses()

        def close(self):
            return None

    class Provider(OpenAIEditorialProvider):
        def _client(self):
            return Client()

    response = Provider("segredo").improve(
        EditorialRequest(
            block_id="bloco-1",
            text="Ana: foram 27 casos",
            model_id="gpt-5.6-terra",
            reasoning_effort="none",
        ),
        CancellationToken(),
    )

    assert response.text == "Ana: Foram 27 casos."
    assert response.usage.total_tokens == 140
    assert captured["store"] is False
    assert captured["reasoning"] == {"effort": "none"}
    assert "tools" not in captured
    assert EDITORIAL_INSTRUCTIONS in captured["instructions"]
    assert "<bloco_alvo" in captured["input"]


def test_editorial_clients_use_bounded_timeout_without_sdk_retries() -> None:
    openai_client = OpenAIEditorialProvider("segredo")._client()  # noqa: SLF001
    try:
        assert openai_client.timeout == EDITORIAL_TIMEOUT_SECONDS
        assert openai_client.max_retries == 0
    finally:
        openai_client.close()

    gemini_client = GeminiEditorialProvider("segredo")._client()  # noqa: SLF001
    try:
        http_options = gemini_client._api_client._http_options  # noqa: SLF001
        assert http_options.timeout == int(EDITORIAL_TIMEOUT_SECONDS * 1_000)
        assert http_options.retry_options.attempts == 1
    finally:
        gemini_client.close()


def test_gemini_transcription_disables_automatic_sdk_retries() -> None:
    client = GeminiProvider("segredo")._client()  # noqa: SLF001
    try:
        retry_options = client._api_client._http_options.retry_options  # noqa: SLF001
        assert retry_options.attempts == 1
    finally:
        client.close()


def test_gemini_editorial_uses_same_contract_and_captures_usage() -> None:
    captured = {}

    class Interactions:
        def create(self, **values):
            captured.update(values)
            return SimpleNamespace(
                output_text="Texto melhorado.",
                model="gemini-3.5-flash-lite",
                usage={
                    "inputTokenCount": 80,
                    "outputTokenCount": 20,
                    "thoughtsTokenCount": 5,
                    "totalTokenCount": 105,
                },
            )

    class Client:
        interactions = Interactions()

        def close(self):
            return None

    class Provider(GeminiEditorialProvider):
        def _client(self):
            return Client()

    response = Provider("segredo").improve(
        EditorialRequest(
            block_id="bloco-1",
            text="texto melhorado",
            model_id="gemini-3.5-flash-lite",
        ),
        CancellationToken(),
    )

    assert response.usage.total_tokens == 105
    assert response.usage.reasoning_in_output is False
    assert captured["model"] == "gemini-3.5-flash-lite"
    assert EDITORIAL_INSTRUCTIONS in captured["input"]
