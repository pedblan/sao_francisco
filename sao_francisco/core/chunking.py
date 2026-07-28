"""Plan bounded audio chunks while preferring natural silence boundaries."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from .models import BoundaryKind, ChunkSpec, SilenceInterval


def _coerce_silence(value: SilenceInterval | Sequence[float]) -> SilenceInterval:
    if isinstance(value, SilenceInterval):
        return value
    if len(value) != 2:
        raise ValueError("silence tuples must contain (start, end)")
    return SilenceInterval(float(value[0]), float(value[1]))


def normalize_silences(
    silences: Iterable[SilenceInterval | Sequence[float]],
    *,
    duration: float,
) -> tuple[SilenceInterval, ...]:
    """Clamp, sort and merge silence intervals for a media timeline."""

    if duration <= 0:
        raise ValueError("duration must be positive")
    clamped: list[SilenceInterval] = []
    for raw in silences:
        silence = _coerce_silence(raw)
        start = min(max(0.0, silence.start), duration)
        end = min(max(0.0, silence.end), duration)
        if end > start:
            clamped.append(SilenceInterval(start, end))
    clamped.sort(key=lambda item: (item.start, item.end))

    merged: list[SilenceInterval] = []
    for silence in clamped:
        if merged and silence.start <= merged[-1].end:
            merged[-1] = SilenceInterval(
                merged[-1].start, max(merged[-1].end, silence.end)
            )
        else:
            merged.append(silence)
    return tuple(merged)


@dataclass(frozen=True, slots=True)
class ChunkPlanner:
    """Configuration for deterministic chunk planning."""

    target_duration: float = 600.0
    search_window: float = 30.0
    overlap: float = 2.0
    min_duration: float = 15.0

    def __post_init__(self) -> None:
        if self.target_duration <= 0:
            raise ValueError("target_duration must be positive")
        if self.search_window < 0:
            raise ValueError("search_window must not be negative")
        if self.overlap < 0:
            raise ValueError("overlap must not be negative")
        if self.overlap >= self.target_duration:
            raise ValueError("overlap must be shorter than target_duration")
        if self.min_duration <= 0:
            raise ValueError("min_duration must be positive")
        if self.min_duration > self.target_duration:
            raise ValueError("min_duration cannot exceed target_duration")

    def plan(
        self,
        duration: float,
        silences: Iterable[SilenceInterval | Sequence[float]] = (),
    ) -> tuple[ChunkSpec, ...]:
        """Return a complete, ordered plan for ``duration`` seconds.

        A silence midpoint is selected when it lies within ``search_window`` of
        the ideal boundary and leaves viable media on both sides.  If no such
        silence exists, a hard cut is made and the following chunk receives the
        configured overlap.  Silence cuts do not need overlap.
        """

        if duration <= 0:
            raise ValueError("duration must be positive")
        timeline = normalize_silences(silences, duration=duration)
        if duration <= self.target_duration:
            return (ChunkSpec(0, 0.0, float(duration), boundary=BoundaryKind.END),)

        chunks: list[ChunkSpec] = []
        start = 0.0
        overlap_before = 0.0
        epsilon = 1e-6

        while duration - start > self.target_duration + epsilon:
            ideal = start + self.target_duration

            # Avoid manufacturing a tiny tail: a slightly long final chunk is
            # preferable to another provider request for a few seconds.
            if duration - ideal < self.min_duration:
                break

            lower = max(start + self.min_duration, ideal - self.search_window)
            upper = min(duration - self.min_duration, ideal + self.search_window)
            candidates = [
                silence
                for silence in timeline
                if lower - epsilon <= silence.midpoint <= upper + epsilon
            ]

            if candidates:
                chosen = min(
                    candidates,
                    key=lambda item: (abs(item.midpoint - ideal), -item.duration, item.start),
                )
                end = chosen.midpoint
                boundary = BoundaryKind.SILENCE
                next_start = end
            else:
                end = ideal
                boundary = BoundaryKind.HARD
                next_start = max(start + epsilon, end - self.overlap)

            chunks.append(
                ChunkSpec(
                    index=len(chunks),
                    start=start,
                    end=end,
                    overlap_before=overlap_before,
                    boundary=boundary,
                )
            )
            next_overlap = end - next_start
            if next_start <= start + epsilon:
                raise RuntimeError("chunk planner made no forward progress")
            start = next_start
            overlap_before = next_overlap

        chunks.append(
            ChunkSpec(
                index=len(chunks),
                start=start,
                end=float(duration),
                overlap_before=overlap_before,
                boundary=BoundaryKind.END,
            )
        )
        return tuple(chunks)


def plan_chunks(
    duration: float,
    silences: Iterable[SilenceInterval | Sequence[float]] = (),
    *,
    target_duration: float = 600.0,
    search_window: float = 30.0,
    overlap: float = 2.0,
    min_duration: float = 15.0,
) -> tuple[ChunkSpec, ...]:
    """Functional wrapper around :class:`ChunkPlanner`."""

    return ChunkPlanner(
        target_duration=target_duration,
        search_window=search_window,
        overlap=overlap,
        min_duration=min_duration,
    ).plan(duration, silences)
