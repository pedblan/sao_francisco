from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal

ProviderId = Literal["openai", "gemini"]


@dataclass(frozen=True, slots=True)
class TranscriptionModel:
    id: str
    provider: ProviderId
    name: str
    summary: str
    response_kind: Literal["text", "segments", "speaker_segments"]
    supports_context_prompt: bool
    supports_speakers: bool
    precise_timestamps: bool
    recommended: bool = False

    def to_ui_dict(self) -> dict[str, object]:
        value = asdict(self)
        value["providerName"] = "OpenAI" if self.provider == "openai" else "Gemini"
        value["capability"] = self.capability_label
        return value

    @property
    def capability_label(self) -> str:
        if self.supports_speakers:
            return "Falantes e marcações de tempo"
        if self.precise_timestamps:
            return "Marcações de tempo precisas"
        return "Texto contínuo"


# Revisado em 27/07/2026 contra a documentação oficial de cada provedor.
# Os nomes exibidos descrevem a finalidade; o ID técnico permanece disponível
# nos detalhes e no manifesto de cada trabalho.
MODEL_CATALOG: tuple[TranscriptionModel, ...] = (
    TranscriptionModel(
        id="gpt-4o-mini-transcribe",
        provider="openai",
        name="Econômico",
        summary="Boa qualidade com menor custo e resposta rápida.",
        response_kind="text",
        supports_context_prompt=True,
        supports_speakers=False,
        precise_timestamps=False,
        recommended=True,
    ),
    TranscriptionModel(
        id="gpt-4o-transcribe",
        provider="openai",
        name="Maior precisão",
        summary="Prioriza fidelidade quando nomes e vocabulário importam.",
        response_kind="text",
        supports_context_prompt=True,
        supports_speakers=False,
        precise_timestamps=False,
    ),
    TranscriptionModel(
        id="gpt-4o-transcribe-diarize",
        provider="openai",
        name="Identificar falantes",
        summary="Separa as falas por participante e preserva seus intervalos.",
        response_kind="speaker_segments",
        supports_context_prompt=False,
        supports_speakers=True,
        precise_timestamps=True,
    ),
    TranscriptionModel(
        id="whisper-1",
        provider="openai",
        name="Legendas e tempos",
        summary="Fornece segmentos precisos para SRT e VTT.",
        response_kind="segments",
        supports_context_prompt=True,
        supports_speakers=False,
        precise_timestamps=True,
    ),
    TranscriptionModel(
        id="gemini-3.6-flash",
        provider="gemini",
        name="Gemini detalhado",
        summary="Alternativa multimodal com saída estruturada e contexto amplo.",
        response_kind="speaker_segments",
        supports_context_prompt=True,
        supports_speakers=True,
        precise_timestamps=False,
    ),
    TranscriptionModel(
        id="gemini-3.5-flash-lite",
        provider="gemini",
        name="Gemini econômico",
        summary="Opção rápida para grande volume e extração estruturada.",
        response_kind="speaker_segments",
        supports_context_prompt=True,
        supports_speakers=True,
        precise_timestamps=False,
    ),
)


def model_by_id(model_id: str) -> TranscriptionModel:
    for option in MODEL_CATALOG:
        if option.id == model_id:
            return option
    raise KeyError(f"Modelo de transcrição desconhecido: {model_id}")


def models_for_provider(provider: ProviderId) -> tuple[TranscriptionModel, ...]:
    return tuple(option for option in MODEL_CATALOG if option.provider == provider)
