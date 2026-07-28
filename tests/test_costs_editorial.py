from __future__ import annotations

from decimal import Decimal

import pytest

from sao_francisco.core import (
    EditorialValidationError,
    Segment,
    Transcript,
    UsageMetrics,
    assemble_editorial_results,
    build_cost_record,
    format_cost_label,
    format_usage_label,
    plan_editorial_blocks,
    summarize_costs,
    transcript_to_editorial_text,
    validate_editorial_result,
    zero_cost_record,
)


def test_token_costs_use_decimal_rates_and_reported_total_only() -> None:
    record = build_cost_record(
        stage="transcription",
        unit_id="chunk-0",
        provider="openai",
        model="gpt-4o-mini-transcribe",
        usage=UsageMetrics(
            input_tokens=1_000_000,
            output_tokens=1_000_000,
            total_tokens=2_000_000,
        ),
    )

    assert record.usd == Decimal("6.25")
    summary = summarize_costs([record])
    assert summary["usd"] == "6.25"
    assert format_cost_label(summary) == "Custo estimado: cerca de US$ 6,25"
    assert format_usage_label(summary) == "Uso informado: 2.000.000 tokens"


def test_cached_and_long_context_rates_are_not_rounded_with_float() -> None:
    short = build_cost_record(
        stage="improvement",
        unit_id="short",
        provider="openai",
        model="gpt-5.6-terra",
        usage=UsageMetrics(
            input_tokens=1_000,
            cached_input_tokens=500,
            output_tokens=100,
            total_tokens=1_100,
        ),
    )
    long = build_cost_record(
        stage="improvement",
        unit_id="long",
        provider="openai",
        model="gpt-5.6-terra",
        usage=UsageMetrics(
            input_tokens=300_000,
            output_tokens=10_000,
            total_tokens=310_000,
        ),
    )

    assert short.usd == Decimal("0.002875")
    assert long.usd == Decimal("1.725")


def test_duration_fallback_and_honest_unavailable_cost() -> None:
    temporal = build_cost_record(
        stage="transcription",
        unit_id="chunk-0",
        provider="openai",
        model="whisper-1",
        duration_seconds=30,
    )
    unavailable = build_cost_record(
        stage="transcription",
        unit_id="chunk-1",
        provider="gemini",
        model="gemini-3.6-flash",
        duration_seconds=30,
    )

    assert temporal.usd == Decimal("0.003")
    assert format_cost_label(summarize_costs([temporal])) == (
        "Custo estimado: menos de US$ 0,01"
    )
    summary = summarize_costs([unavailable])
    assert summary["available"] is False
    assert format_cost_label(summary) == ""


def test_captions_are_proven_zero_only_when_the_whole_flow_is_free() -> None:
    caption = zero_cost_record(
        stage="transcription",
        unit_id="caption-0",
        provider="openai",
        model="gpt-4o-mini-transcribe",
    )
    free = summarize_costs([caption], zero_proven=True)
    editorial = build_cost_record(
        stage="improvement",
        unit_id="block-0",
        provider="openai",
        model="gpt-5.6-terra",
        usage=UsageMetrics(input_tokens=100, output_tokens=100, total_tokens=200),
    )
    paid = summarize_costs([caption, editorial], zero_proven=False)

    assert format_cost_label(free) == "Sem custo de API"
    assert paid["proven_zero"] is False
    assert Decimal(str(paid["usd"])) > 0


def test_editorial_plan_is_stable_bounded_and_assembled_once() -> None:
    text = "\n\n".join(
        f"Parágrafo {index}. " + ("palavra " * 80)
        for index in range(12)
    )
    first = plan_editorial_blocks(text, max_chars=900)
    second = plan_editorial_blocks(text, max_chars=900)
    results = {block.block_id: block.text for block in first}

    assert first == second
    assert len(first) > 1
    assert all(len(block.text) <= 900 for block in first)
    assembled = assemble_editorial_results(first, results)
    assert assembled.count("Parágrafo") == 12


def test_editorial_validation_preserves_numbers_speakers_and_uncertainty() -> None:
    original = "Ana: Foram 27 casos em 28/07/2026. [inaudível]"
    assert validate_editorial_result(
        original,
        "Ana: Foram 27 casos em 28/07/2026.\n\n[inaudível]",
    )

    with pytest.raises(EditorialValidationError, match="números"):
        validate_editorial_result(original, "Ana: Foram 28 casos em 28/07/2026. [inaudível]")
    with pytest.raises(EditorialValidationError, match="falantes"):
        validate_editorial_result(
            original,
            "Bia: Foram 27 casos em 28/07/2026. [inaudível]",
            protected_speakers=("Ana",),
        )
    with pytest.raises(EditorialValidationError, match="inaudível"):
        validate_editorial_result(original, "Ana: Foram 27 casos em 28/07/2026.")


def test_editorial_validation_allows_punctuation_around_unchanged_numbers() -> None:
    original = "Ana: em 28/07/2026 foram 27 casos."
    improved = "Ana: Em 28/07/2026, foram 27 casos."

    assert validate_editorial_result(original, improved) == improved


def test_editorial_validation_does_not_infer_speakers_from_new_paragraphs() -> None:
    original = 'Ele disse o seguinte: "Cerrão: minha vida está em risco."'
    improved = 'Ele disse o seguinte:\n\n"Cerrão: minha vida está em risco."'

    assert validate_editorial_result(original, improved) == improved


def test_transcript_to_editorial_text_preserves_speaker_associations() -> None:
    transcript = Transcript(
        segments=(
            Segment(0, 1, "Bom dia.", speaker="Ana"),
            Segment(1, 2, "Vamos começar.", speaker="Ana"),
            Segment(2, 3, "Perfeito.", speaker="Bruno"),
        ),
        duration=3,
    )

    assert transcript_to_editorial_text(transcript) == (
        "Ana: Bom dia. Vamos começar.\n\nBruno: Perfeito."
    )
