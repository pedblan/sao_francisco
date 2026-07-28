"""Canonical, provider-independent models used by São Francisco.

All time values are expressed in seconds.  A transcript returned for an audio
chunk uses timestamps relative to that chunk; :mod:`assembly` turns them into
source-relative timestamps.
"""

from __future__ import annotations

import math
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType
from typing import Any

JsonMapping = Mapping[str, Any]


def _finite_non_negative(value: float, field_name: str) -> float:
    number = float(value)
    if not math.isfinite(number) or number < 0:
        raise ValueError(f"{field_name} must be a finite, non-negative number")
    return number


def _optional_confidence(value: float | None) -> float | None:
    if value is None:
        return None
    number = float(value)
    if not math.isfinite(number) or not 0 <= number <= 1:
        raise ValueError("confidence must be between 0 and 1")
    return number


def _immutable_mapping(value: JsonMapping | None) -> JsonMapping:
    return MappingProxyType(dict(value or {}))


@dataclass(frozen=True, slots=True)
class WordTiming:
    """A timed word or token within a transcript."""

    start: float
    end: float
    text: str
    confidence: float | None = None

    def __post_init__(self) -> None:
        start = _finite_non_negative(self.start, "start")
        end = _finite_non_negative(self.end, "end")
        if end < start:
            raise ValueError("end must not precede start")
        if not self.text.strip():
            raise ValueError("word text must not be empty")
        object.__setattr__(self, "start", start)
        object.__setattr__(self, "end", end)
        object.__setattr__(self, "text", self.text.strip())
        object.__setattr__(self, "confidence", _optional_confidence(self.confidence))

    def shifted(self, offset: float) -> WordTiming:
        """Return a copy shifted by ``offset`` seconds."""

        if self.start + offset < 0:
            raise ValueError("offset would produce a negative timestamp")
        return WordTiming(
            start=self.start + offset,
            end=self.end + offset,
            text=self.text,
            confidence=self.confidence,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "start": self.start,
            "end": self.end,
            "text": self.text,
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, value: JsonMapping) -> WordTiming:
        return cls(
            start=float(value["start"]),
            end=float(value["end"]),
            text=str(value["text"]),
            confidence=value.get("confidence"),
        )


@dataclass(frozen=True, slots=True)
class Segment:
    """A canonical transcript segment."""

    start: float
    end: float
    text: str
    speaker: str | None = None
    confidence: float | None = None
    words: tuple[WordTiming, ...] = ()
    metadata: JsonMapping = field(default_factory=dict, compare=False)

    def __post_init__(self) -> None:
        start = _finite_non_negative(self.start, "start")
        end = _finite_non_negative(self.end, "end")
        if end < start:
            raise ValueError("end must not precede start")
        text = self.text.strip()
        if not text:
            raise ValueError("segment text must not be empty")
        words = tuple(self.words)
        if any(word.end > end + 1e-6 or word.start < start - 1e-6 for word in words):
            raise ValueError("word timestamps must be contained by their segment")
        if any(
            left.start > right.start
            for left, right in zip(words, words[1:], strict=False)
        ):
            raise ValueError("words must be ordered by start time")
        object.__setattr__(self, "start", start)
        object.__setattr__(self, "end", end)
        object.__setattr__(self, "text", text)
        object.__setattr__(self, "speaker", self.speaker.strip() if self.speaker else None)
        object.__setattr__(self, "confidence", _optional_confidence(self.confidence))
        object.__setattr__(self, "words", words)
        object.__setattr__(self, "metadata", _immutable_mapping(self.metadata))

    @property
    def duration(self) -> float:
        return self.end - self.start

    def shifted(self, offset: float) -> Segment:
        """Return a segment with all timestamps shifted by ``offset``."""

        if self.start + offset < 0:
            raise ValueError("offset would produce a negative timestamp")
        return Segment(
            start=self.start + offset,
            end=self.end + offset,
            text=self.text,
            speaker=self.speaker,
            confidence=self.confidence,
            words=tuple(word.shifted(offset) for word in self.words),
            metadata=self.metadata,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "start": self.start,
            "end": self.end,
            "text": self.text,
            "speaker": self.speaker,
            "confidence": self.confidence,
            "words": [word.to_dict() for word in self.words],
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, value: JsonMapping) -> Segment:
        return cls(
            start=float(value["start"]),
            end=float(value["end"]),
            text=str(value["text"]),
            speaker=value.get("speaker"),
            confidence=value.get("confidence"),
            words=tuple(WordTiming.from_dict(item) for item in value.get("words", ())),
            metadata=value.get("metadata", {}),
        )


@dataclass(frozen=True, slots=True)
class Transcript:
    """A provider-independent transcript.

    ``segments`` are normalized into chronological order.  ``duration`` may be
    longer than the final segment (for example, when the media ends in silence).
    """

    segments: tuple[Segment, ...] = ()
    language: str | None = None
    duration: float | None = None
    metadata: JsonMapping = field(default_factory=dict, compare=False)

    def __post_init__(self) -> None:
        segments = tuple(sorted(self.segments, key=lambda item: (item.start, item.end)))
        inferred_duration = max((segment.end for segment in segments), default=0.0)
        duration = inferred_duration if self.duration is None else _finite_non_negative(
            self.duration, "duration"
        )
        if duration + 1e-6 < inferred_duration:
            raise ValueError("duration must contain every segment")
        object.__setattr__(self, "segments", segments)
        object.__setattr__(self, "language", self.language.strip() if self.language else None)
        object.__setattr__(self, "duration", duration)
        object.__setattr__(self, "metadata", _immutable_mapping(self.metadata))

    @property
    def text(self) -> str:
        """Plain text assembled from the non-empty segments."""

        return " ".join(segment.text for segment in self.segments).strip()

    @property
    def is_empty(self) -> bool:
        return not self.segments

    def shifted(self, offset: float) -> Transcript:
        """Return a transcript with all segments shifted by ``offset``."""

        shifted_duration = (self.duration or 0) + offset
        return Transcript(
            segments=tuple(segment.shifted(offset) for segment in self.segments),
            language=self.language,
            duration=shifted_duration,
            metadata=self.metadata,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "segments": [segment.to_dict() for segment in self.segments],
            "language": self.language,
            "duration": self.duration,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, value: JsonMapping) -> Transcript:
        return cls(
            segments=tuple(Segment.from_dict(item) for item in value.get("segments", ())),
            language=value.get("language"),
            duration=value.get("duration"),
            metadata=value.get("metadata", {}),
        )

    @classmethod
    def from_segments(
        cls,
        segments: Iterable[Segment],
        *,
        language: str | None = None,
        duration: float | None = None,
        metadata: JsonMapping | None = None,
    ) -> Transcript:
        return cls(tuple(segments), language, duration, metadata or {})


@dataclass(frozen=True, slots=True)
class SilenceInterval:
    """A detected interval with no meaningful audio."""

    start: float
    end: float

    def __post_init__(self) -> None:
        start = _finite_non_negative(self.start, "start")
        end = _finite_non_negative(self.end, "end")
        if end <= start:
            raise ValueError("a silence interval must have positive duration")
        object.__setattr__(self, "start", start)
        object.__setattr__(self, "end", end)

    @property
    def midpoint(self) -> float:
        return (self.start + self.end) / 2

    @property
    def duration(self) -> float:
        return self.end - self.start

    def to_dict(self) -> dict[str, float]:
        return {"start": self.start, "end": self.end}

    @classmethod
    def from_dict(cls, value: JsonMapping) -> SilenceInterval:
        return cls(start=float(value["start"]), end=float(value["end"]))


class BoundaryKind(StrEnum):
    """How a chunk's right boundary was chosen."""

    END = "end"
    SILENCE = "silence"
    HARD = "hard"


@dataclass(frozen=True, slots=True)
class ChunkSpec:
    """A source interval sent independently to a transcription provider."""

    index: int
    start: float
    end: float
    overlap_before: float = 0.0
    boundary: BoundaryKind = BoundaryKind.END

    def __post_init__(self) -> None:
        if isinstance(self.index, bool) or int(self.index) != self.index or self.index < 0:
            raise ValueError("index must be a non-negative integer")
        start = _finite_non_negative(self.start, "start")
        end = _finite_non_negative(self.end, "end")
        overlap = _finite_non_negative(self.overlap_before, "overlap_before")
        if end <= start:
            raise ValueError("chunk end must be after start")
        if overlap > end - start:
            raise ValueError("overlap_before cannot exceed chunk duration")
        object.__setattr__(self, "index", int(self.index))
        object.__setattr__(self, "start", start)
        object.__setattr__(self, "end", end)
        object.__setattr__(self, "overlap_before", overlap)
        object.__setattr__(self, "boundary", BoundaryKind(self.boundary))

    @property
    def duration(self) -> float:
        return self.end - self.start

    def to_dict(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "start": self.start,
            "end": self.end,
            "overlap_before": self.overlap_before,
            "boundary": self.boundary.value,
        }

    @classmethod
    def from_dict(cls, value: JsonMapping) -> ChunkSpec:
        return cls(
            index=int(value["index"]),
            start=float(value["start"]),
            end=float(value["end"]),
            overlap_before=float(value.get("overlap_before", 0)),
            boundary=BoundaryKind(value.get("boundary", BoundaryKind.END.value)),
        )


# Explicit names make the intent clearer to API-provider adapters.
TranscriptionSegment = Segment
Transcription = Transcript
