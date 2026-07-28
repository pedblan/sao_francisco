"""Subtitle discovery models plus dependency-free SRT/WebVTT parsing."""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass, field
from enum import StrEnum
from html import unescape
from pathlib import Path
from typing import Protocol

from .models import Segment, Transcript


class SubtitleError(RuntimeError):
    """Base class for subtitle acquisition errors."""


class SubtitleUnavailableError(SubtitleError):
    """No suitable text subtitle was available."""


class ImageSubtitleUnsupportedError(SubtitleError):
    """Only bitmap subtitles were found; OCR is deliberately not implicit."""

    def __init__(self, streams: Iterable[SubtitleStream]) -> None:
        self.streams = tuple(streams)
        labels = ", ".join(
            f"stream {stream.index} ({stream.codec_name})" for stream in self.streams
        )
        super().__init__(
            f"image subtitles require OCR and are not supported: {labels or 'unknown stream'}"
        )


class SubtitleKind(StrEnum):
    TEXT = "text"
    IMAGE = "image"
    UNKNOWN = "unknown"


class SubtitleOrigin(StrEnum):
    SIDECAR = "sidecar"
    EMBEDDED = "embedded"
    URL_MANUAL = "url_manual"
    URL_AUTOMATIC = "url_automatic"


class CleanupOwner(Protocol):
    """Resource owner attached to an asset created in a temporary workspace."""

    def cleanup(self) -> None: ...


TEXT_SUBTITLE_CODECS = frozenset(
    {
        "ass",
        "eia_608",
        "eia_708",
        "mov_text",
        "srt",
        "ssa",
        "subrip",
        "text",
        "ttml",
        "webvtt",
    }
)
IMAGE_SUBTITLE_CODECS = frozenset(
    {
        "dvb_subtitle",
        "dvd_subtitle",
        "hdmv_pgs_subtitle",
        "pgssub",
        "vobsub",
        "xsub",
    }
)


def classify_subtitle_codec(codec_name: str | None) -> SubtitleKind:
    normalized = (codec_name or "").strip().casefold()
    if normalized in TEXT_SUBTITLE_CODECS:
        return SubtitleKind.TEXT
    if normalized in IMAGE_SUBTITLE_CODECS:
        return SubtitleKind.IMAGE
    return SubtitleKind.UNKNOWN


@dataclass(frozen=True, slots=True)
class SubtitleStream:
    """Subtitle stream metadata reported by ffprobe."""

    index: int
    codec_name: str
    language: str | None = None
    title: str | None = None
    default: bool = False
    kind: SubtitleKind = SubtitleKind.UNKNOWN

    def __post_init__(self) -> None:
        if self.index < 0:
            raise ValueError("subtitle stream index must not be negative")
        object.__setattr__(self, "codec_name", self.codec_name.strip().casefold())
        object.__setattr__(self, "language", self.language.strip() if self.language else None)
        object.__setattr__(self, "title", self.title.strip() if self.title else None)
        kind = self.kind
        if kind == SubtitleKind.UNKNOWN:
            kind = classify_subtitle_codec(self.codec_name)
        object.__setattr__(self, "kind", SubtitleKind(kind))


@dataclass(frozen=True, slots=True)
class SubtitleAsset:
    """A decoded subtitle selected instead of audio transcription."""

    transcript: Transcript
    origin: SubtitleOrigin
    path: Path
    language: str | None = None
    automatic: bool = False
    stream_index: int | None = None
    workspace_owner: CleanupOwner | None = field(
        default=None,
        repr=False,
        compare=False,
    )

    def __post_init__(self) -> None:
        object.__setattr__(self, "path", Path(self.path))
        object.__setattr__(self, "origin", SubtitleOrigin(self.origin))

    def cleanup(self) -> None:
        """Release a temporary workspace owned by this asset, if any."""

        owner = self.workspace_owner
        if owner is not None:
            owner.cleanup()
            object.__setattr__(self, "workspace_owner", None)

    def __enter__(self) -> SubtitleAsset:
        return self

    def __exit__(self, _type: object, _value: object, _traceback: object) -> None:
        self.cleanup()


_TIMING_RE = re.compile(
    r"^\s*(?P<start>(?:\d{1,3}:)?\d{1,2}:\d{2}(?:[,.]\d{1,3})?)"
    r"\s*-->\s*"
    r"(?P<end>(?:\d{1,3}:)?\d{1,2}:\d{2}(?:[,.]\d{1,3})?)"
    r"(?:\s+.*)?$"
)
_VOICE_RE = re.compile(r"<v(?:\.[^ >]+)*\s+([^>]+)>", re.IGNORECASE)
_TAG_RE = re.compile(r"</?[^>]+>")


def parse_timestamp(value: str) -> float:
    """Parse SRT or WebVTT timestamps into seconds."""

    normalized = value.strip().replace(",", ".")
    parts = normalized.split(":")
    if len(parts) == 3:
        hours, minutes, seconds = parts
    elif len(parts) == 2:
        hours = "0"
        minutes, seconds = parts
    else:
        raise ValueError(f"invalid subtitle timestamp {value!r}")
    result = int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    if result < 0 or int(minutes) >= 60 or float(seconds) >= 60:
        raise ValueError(f"invalid subtitle timestamp {value!r}")
    return result


def _clean_cue(lines: list[str]) -> tuple[str, str | None]:
    raw = "\n".join(line.strip() for line in lines).strip()
    voice = _VOICE_RE.search(raw)
    speaker = unescape(voice.group(1)).strip() if voice else None
    text = _TAG_RE.sub("", raw)
    text = unescape(text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n[ \t]+", "\n", text)
    return text.strip(), speaker or None


def _parse_blocks(text: str, *, language: str | None, source_format: str) -> Transcript:
    normalized = text.lstrip("\ufeff").replace("\r\n", "\n").replace("\r", "\n")
    blocks = re.split(r"\n[ \t]*\n", normalized)
    segments: list[Segment] = []

    for block in blocks:
        lines = block.splitlines()
        if not lines:
            continue
        first = lines[0].strip()
        if first == "WEBVTT" or first.startswith(("NOTE", "STYLE", "REGION")):
            continue
        timing_index = next(
            (index for index, line in enumerate(lines) if _TIMING_RE.match(line)),
            None,
        )
        if timing_index is None:
            continue
        timing = _TIMING_RE.match(lines[timing_index])
        assert timing is not None
        start = parse_timestamp(timing.group("start"))
        end = parse_timestamp(timing.group("end"))
        if end <= start:
            continue
        cue_text, speaker = _clean_cue(lines[timing_index + 1 :])
        if cue_text:
            segments.append(
                Segment(
                    start=start,
                    end=end,
                    text=cue_text,
                    speaker=speaker,
                    metadata={"subtitle_format": source_format},
                )
            )

    duration = max((segment.end for segment in segments), default=0.0)
    return Transcript(
        segments=tuple(segments),
        language=language,
        duration=duration,
        metadata={"source": "subtitles", "format": source_format},
    )


def parse_srt(text: str, *, language: str | None = None) -> Transcript:
    return _parse_blocks(text, language=language, source_format="srt")


def parse_vtt(text: str, *, language: str | None = None) -> Transcript:
    return _parse_blocks(text, language=language, source_format="vtt")


def parse_subtitle_text(
    text: str,
    *,
    format_hint: str | None = None,
    language: str | None = None,
) -> Transcript:
    hint = (format_hint or "").lower().lstrip(".")
    if hint in {"vtt", "webvtt"} or text.lstrip("\ufeff").startswith("WEBVTT"):
        return parse_vtt(text, language=language)
    if hint in {"srt", "subrip", ""}:
        return parse_srt(text, language=language)
    raise ValueError(f"unsupported subtitle format {format_hint!r}")


def load_subtitle_file(
    path: str | Path,
    *,
    language: str | None = None,
) -> Transcript:
    source = Path(path)
    if source.suffix.casefold() not in {".srt", ".vtt"}:
        raise ValueError(f"unsupported subtitle file {source.name!r}")
    return parse_subtitle_text(
        source.read_text(encoding="utf-8-sig"),
        format_hint=source.suffix,
        language=language,
    )
