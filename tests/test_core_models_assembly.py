from __future__ import annotations

import pytest

from sao_francisco.core import (
    BoundaryKind,
    ChunkSpec,
    Segment,
    Transcript,
    WordTiming,
    assemble_chunks,
    deduplicate_text_overlap,
)


def test_canonical_transcript_round_trip_preserves_unicode_and_words() -> None:
    original = Transcript(
        segments=(
            Segment(
                start=1.0,
                end=2.5,
                text="São Francisco.",
                speaker="Falante 1",
                confidence=0.92,
                words=(
                    WordTiming(1.0, 1.5, "São"),
                    WordTiming(1.6, 2.5, "Francisco."),
                ),
                metadata={"provider_segment_id": 7},
            ),
        ),
        language="pt-BR",
        duration=3,
        metadata={"provider": "example"},
    )

    restored = Transcript.from_dict(original.to_dict())

    assert restored == original
    assert restored.text == "São Francisco."
    assert restored.metadata["provider"] == "example"


def test_models_reject_invalid_timestamps() -> None:
    with pytest.raises(ValueError):
        Segment(start=2, end=1, text="inválido")
    with pytest.raises(ValueError):
        WordTiming(start=-1, end=1, text="inválido")
    with pytest.raises(ValueError):
        Transcript(segments=(Segment(0, 3, "fala"),), duration=2)


def test_text_overlap_is_accent_and_case_insensitive() -> None:
    text, removed = deduplicate_text_overlap(
        "Terminamos em SÃO FRANCISCO",
        "são francisco e seguimos adiante",
    )

    assert removed == 2
    assert text == "e seguimos adiante"


def test_assembly_offsets_chunks_and_removes_only_declared_overlap() -> None:
    chunks = (
        ChunkSpec(0, 0, 60, boundary=BoundaryKind.HARD),
        ChunkSpec(1, 58, 118, overlap_before=2, boundary=BoundaryKind.END),
    )
    first = Transcript(
        segments=(Segment(55, 60, "fim em comum"),),
        language="pt",
        duration=60,
    )
    second = Transcript(
        segments=(
            Segment(0, 3, "fim em comum e continua"),
            Segment(4, 7, "novo trecho"),
        ),
        language="pt",
        duration=60,
    )

    assembled = assemble_chunks(chunks, {0: first, 1: second})

    assert assembled.text == "fim em comum e continua novo trecho"
    assert assembled.segments[1].text == "e continua"
    assert assembled.segments[1].start > 58
    assert assembled.segments[2].start == 62
    assert assembled.duration == 118


def test_assembly_requires_every_chunk_result() -> None:
    chunks = (
        ChunkSpec(0, 0, 10),
        ChunkSpec(1, 10, 20),
    )
    with pytest.raises(KeyError, match="chunk 1"):
        assemble_chunks(chunks, {0: Transcript()})
