from pathlib import Path

from sao_francisco.catalog import MODEL_CATALOG, model_by_id, models_for_provider


def test_catalog_has_stable_unique_ids_and_two_providers() -> None:
    ids = [option.id for option in MODEL_CATALOG]
    assert len(ids) == len(set(ids))
    assert {option.provider for option in MODEL_CATALOG} == {"openai", "gemini"}


def test_catalog_preserves_timestamp_and_speaker_capabilities() -> None:
    whisper = model_by_id("whisper-1")
    diarize = model_by_id("gpt-4o-transcribe-diarize")

    assert whisper.precise_timestamps is True
    assert whisper.supports_speakers is False
    assert diarize.supports_speakers is True
    assert diarize.supports_context_prompt is False
    assert len(models_for_provider("gemini")) == 2


def test_packaged_and_repository_notices_stay_in_sync() -> None:
    project_root = Path(__file__).resolve().parents[1]
    repository_notice = project_root / "THIRD_PARTY_NOTICES.md"
    packaged_notice = project_root / "sao_francisco" / "THIRD_PARTY_NOTICES.md"

    assert repository_notice.read_bytes() == packaged_notice.read_bytes()
