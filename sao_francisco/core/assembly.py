"""Offset and assemble independently transcribed chunks."""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Mapping, Sequence

from .models import ChunkSpec, Segment, Transcript, WordTiming

_TOKEN_RE = re.compile(r"\w+(?:[’'\-]\w+)*", re.UNICODE)


def _normalized_tokens(text: str) -> list[str]:
    tokens: list[str] = []
    for match in _TOKEN_RE.finditer(text):
        decomposed = unicodedata.normalize("NFKD", match.group(0).casefold())
        tokens.append("".join(char for char in decomposed if not unicodedata.combining(char)))
    return tokens


def overlap_word_count(previous: str, current: str, *, max_words: int = 80) -> int:
    """Count matching words between a previous suffix and a current prefix."""

    left = _normalized_tokens(previous)[-max_words:]
    right = _normalized_tokens(current)[:max_words]
    for size in range(min(len(left), len(right)), 0, -1):
        if left[-size:] == right[:size]:
            return size
    return 0


def deduplicate_text_overlap(
    previous: str,
    current: str,
    *,
    minimum_words: int = 2,
) -> tuple[str, int]:
    """Trim a repeated prefix from ``current``.

    Returns ``(trimmed_text, removed_word_count)``.  A complete one-word cue is
    also considered a duplicate; partial single-word matches are retained to
    avoid deleting natural repetitions.
    """

    matches = list(_TOKEN_RE.finditer(current))
    repeated = overlap_word_count(previous, current)
    if repeated == 0:
        return current.strip(), 0
    if repeated < minimum_words and repeated != len(matches):
        return current.strip(), 0
    if repeated >= len(matches):
        return "", repeated
    cut = matches[repeated - 1].end()
    trimmed = current[cut:].lstrip(" \t\r\n,.;:!?—–-")
    return trimmed, repeated


def offset_transcript(transcript: Transcript, offset: float) -> Transcript:
    """Shift a chunk-relative transcript onto the source timeline."""

    if offset < 0:
        raise ValueError("offset must not be negative")
    return Transcript(
        segments=tuple(segment.shifted(offset) for segment in transcript.segments),
        language=transcript.language,
        duration=(transcript.duration or 0.0) + offset,
        metadata=transcript.metadata,
    )


def _clip_segment(segment: Segment, chunk: ChunkSpec) -> Segment | None:
    """Clip provider rounding errors to the declared chunk duration."""

    local_duration = chunk.duration
    local_start = min(max(segment.start, 0.0), local_duration)
    local_end = min(max(segment.end, 0.0), local_duration)
    if local_end <= local_start or not segment.text.strip():
        return None
    words: list[WordTiming] = []
    for word in segment.words:
        start = min(max(word.start, local_start), local_end)
        end = min(max(word.end, start), local_end)
        if end > start:
            words.append(
                WordTiming(start=start, end=end, text=word.text, confidence=word.confidence)
            )
    return Segment(
        start=local_start,
        end=local_end,
        text=segment.text,
        speaker=segment.speaker,
        confidence=segment.confidence,
        words=tuple(words),
        metadata=segment.metadata,
    )


def _trim_segment_prefix(segment: Segment, text: str, removed_words: int) -> Segment | None:
    if not text:
        return None
    words = segment.words
    if words and removed_words < len(words):
        remaining_words = words[removed_words:]
        new_start = max(segment.start, words[removed_words - 1].end)
    else:
        token_count = max(1, len(_normalized_tokens(segment.text)))
        fraction = min(1.0, removed_words / token_count)
        new_start = segment.start + segment.duration * fraction
        remaining_words = ()
    if segment.end <= new_start:
        return None
    return Segment(
        start=new_start,
        end=segment.end,
        text=text,
        speaker=segment.speaker,
        confidence=segment.confidence,
        words=remaining_words,
        metadata=segment.metadata,
    )


def _transcript_for(
    transcripts: Mapping[int, Transcript] | Sequence[Transcript],
    chunk: ChunkSpec,
) -> Transcript:
    if isinstance(transcripts, Mapping):
        try:
            return transcripts[chunk.index]
        except KeyError as error:
            raise KeyError(f"missing transcript for chunk {chunk.index}") from error
    try:
        return transcripts[chunk.index]
    except IndexError as error:
        raise KeyError(f"missing transcript for chunk {chunk.index}") from error


def assemble_chunks(
    chunks: Sequence[ChunkSpec],
    transcripts: Mapping[int, Transcript] | Sequence[Transcript],
    *,
    deduplicate: bool = True,
) -> Transcript:
    """Build one source-relative transcript from chunk-relative results.

    Deduplication is limited to the overlap region declared by each
    :class:`~sao_francisco.core.models.ChunkSpec`; repetitions elsewhere remain
    untouched.
    """

    if not chunks:
        return Transcript()
    ordered_chunks = sorted(chunks, key=lambda item: item.index)
    if [chunk.index for chunk in ordered_chunks] != list(range(len(ordered_chunks))):
        raise ValueError("chunk indices must be contiguous and start at zero")

    assembled: list[Segment] = []
    language: str | None = None
    previous_text = ""

    for chunk in ordered_chunks:
        transcript = _transcript_for(transcripts, chunk)
        language = language or transcript.language
        overlap_limit = chunk.start + chunk.overlap_before

        for raw_segment in transcript.segments:
            clipped = _clip_segment(raw_segment, chunk)
            if clipped is None:
                continue
            segment = clipped.shifted(chunk.start)
            in_overlap = (
                deduplicate
                and chunk.overlap_before > 0
                and segment.start <= overlap_limit + 1.0
                and bool(assembled)
            )
            if in_overlap:
                trimmed_text, removed = deduplicate_text_overlap(
                    previous_text[-2000:], segment.text
                )
                if removed:
                    trimmed_segment = _trim_segment_prefix(
                        segment,
                        trimmed_text,
                        removed,
                    )
                    if trimmed_segment is None:
                        continue
                    segment = trimmed_segment
            assembled.append(segment)
            previous_text = f"{previous_text} {segment.text}".strip()

    source_duration = max(chunk.end for chunk in ordered_chunks)
    return Transcript(
        segments=tuple(assembled),
        language=language,
        duration=source_duration,
        metadata={
            "assembled_from_chunks": len(ordered_chunks),
            "deduplicated_overlaps": deduplicate,
        },
    )


assemble_transcripts = assemble_chunks
