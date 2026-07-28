"""FFmpeg/ffprobe/yt-dlp integration with cooperative cancellation."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType
from typing import Any
from urllib.parse import urlparse

from .cancellation import NEVER_CANCELLED, CancellationToken, OperationCancelled
from .models import ChunkSpec, SilenceInterval
from .subtitles import (
    ImageSubtitleUnsupportedError,
    SubtitleAsset,
    SubtitleKind,
    SubtitleOrigin,
    SubtitleStream,
    SubtitleUnavailableError,
    load_subtitle_file,
)


class MediaError(RuntimeError):
    """Base class for media preparation errors."""


class MediaDependencyError(MediaError):
    """A required command-line dependency is unavailable."""


class MediaCommandError(MediaError):
    """A media command returned a non-zero exit status."""

    def __init__(
        self,
        command: Sequence[str],
        returncode: int,
        stderr: str,
    ) -> None:
        self.command = tuple(command)
        self.returncode = returncode
        self.stderr = stderr
        message = stderr.strip().splitlines()[-1] if stderr.strip() else "unknown error"
        super().__init__(f"{Path(command[0]).name} failed ({returncode}): {message}")


@dataclass(frozen=True, slots=True)
class MediaInfo:
    path: Path
    duration: float
    format_name: str | None
    audio_stream_count: int
    video_stream_count: int
    subtitle_streams: tuple[SubtitleStream, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict, compare=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "path", Path(self.path))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    @property
    def text_subtitle_streams(self) -> tuple[SubtitleStream, ...]:
        return tuple(
            stream for stream in self.subtitle_streams if stream.kind == SubtitleKind.TEXT
        )

    @property
    def image_subtitle_streams(self) -> tuple[SubtitleStream, ...]:
        return tuple(
            stream for stream in self.subtitle_streams if stream.kind == SubtitleKind.IMAGE
        )


@dataclass(frozen=True, slots=True)
class LocalSubtitleDiscovery:
    sidecars: tuple[Path, ...] = ()
    text_streams: tuple[SubtitleStream, ...] = ()
    image_streams: tuple[SubtitleStream, ...] = ()
    unknown_streams: tuple[SubtitleStream, ...] = ()


@dataclass(slots=True)
class MediaWorkspace:
    """An owned workspace that can only clean itself when its marker exists."""

    path: Path
    marker_name: str = ".sao-francisco-workspace"
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.path = Path(self.path).resolve()

    def cleanup(self) -> None:
        marker = self.path / self.marker_name
        if not marker.is_file():
            raise MediaError(f"refusing to clean unmarked workspace {self.path}")
        shutil.rmtree(self.path)

    def __enter__(self) -> MediaWorkspace:
        return self

    def __exit__(self, _type: object, _value: object, _traceback: object) -> None:
        self.cleanup()

    def __del__(self) -> None:
        """Best-effort fallback for an explicitly leased workspace."""

        try:
            if (self.path / self.marker_name).is_file():
                shutil.rmtree(self.path)
        except BaseException:
            pass


@dataclass(frozen=True, slots=True)
class PreparedChunk:
    spec: ChunkSpec
    path: Path


@dataclass(frozen=True, slots=True)
class PreparedMedia:
    source: Path
    workspace: MediaWorkspace
    chunks: tuple[PreparedChunk, ...]


_SILENCE_START_RE = re.compile(r"silence_start:\s*(?P<time>\d+(?:\.\d+)?)")
_SILENCE_END_RE = re.compile(r"silence_end:\s*(?P<time>\d+(?:\.\d+)?)")
_SAFE_PREFIX_RE = re.compile(r"[^A-Za-z0-9._-]+")
_LANGUAGE_TAG_RE = re.compile(r"^[A-Za-z]{2,3}(?:[-_][A-Za-z0-9]{2,8})*$")
_LANGUAGE_ALIASES = {
    "ara": "ar",
    "ces": "cs",
    "chi": "zh",
    "cze": "cs",
    "dan": "da",
    "deu": "de",
    "dut": "nl",
    "ell": "el",
    "eng": "en",
    "fas": "fa",
    "fin": "fi",
    "fra": "fr",
    "fre": "fr",
    "ger": "de",
    "gre": "el",
    "heb": "he",
    "hin": "hi",
    "ind": "id",
    "ita": "it",
    "jpn": "ja",
    "kor": "ko",
    "nld": "nl",
    "nor": "no",
    "per": "fa",
    "pol": "pl",
    "por": "pt",
    "ron": "ro",
    "rum": "ro",
    "rus": "ru",
    "spa": "es",
    "swe": "sv",
    "tur": "tr",
    "ukr": "uk",
    "vie": "vi",
    "zho": "zh",
}
_UNDEFINED_LANGUAGES = frozenset({"", "und", "unknown", "zxx"})


class MediaProcessor:
    """Prepare local and remote media without involving any GUI framework."""

    def __init__(
        self,
        *,
        ffmpeg: str = "ffmpeg",
        ffprobe: str = "ffprobe",
        ytdlp: str = "yt-dlp",
        work_root: str | os.PathLike[str] | None = None,
    ) -> None:
        self.ffmpeg = ffmpeg
        self.ffprobe = ffprobe
        self.ytdlp = ytdlp
        self.work_root = Path(work_root).expanduser().resolve() if work_root else None

    def create_workspace(self, label: str = "job") -> MediaWorkspace:
        """Create an exclusive temporary directory and mark its ownership."""

        safe_label = _SAFE_PREFIX_RE.sub("-", label).strip(".-") or "job"
        if self.work_root:
            self.work_root.mkdir(parents=True, exist_ok=True)
        path = Path(
            tempfile.mkdtemp(
                prefix=f"sao-francisco-{safe_label}-",
                dir=self.work_root,
            )
        )
        marker = path / ".sao-francisco-workspace"
        marker.write_text("owned by São Francisco\n", encoding="utf-8")
        return MediaWorkspace(path)

    def probe(
        self,
        source: str | os.PathLike[str],
        *,
        cancel_token: CancellationToken | None = None,
    ) -> MediaInfo:
        path = Path(source).expanduser().resolve()
        if not path.is_file():
            raise FileNotFoundError(path)
        completed = self._run(
            [
                self.ffprobe,
                "-v",
                "error",
                "-show_format",
                "-show_streams",
                "-of",
                "json",
                str(path),
            ],
            cancel_token=cancel_token,
        )
        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError as error:
            raise MediaError(f"ffprobe returned invalid JSON for {path}") from error

        streams = payload.get("streams", [])
        format_data = payload.get("format", {})
        raw_duration = format_data.get("duration")
        if raw_duration is None:
            durations = [
                float(stream["duration"])
                for stream in streams
                if stream.get("duration") not in (None, "N/A")
            ]
            raw_duration = max(durations, default=0)
        duration = float(raw_duration or 0)
        if duration <= 0:
            raise MediaError(f"could not determine positive duration for {path}")

        subtitle_streams: list[SubtitleStream] = []
        for stream in streams:
            if stream.get("codec_type") != "subtitle":
                continue
            tags = stream.get("tags") or {}
            disposition = stream.get("disposition") or {}
            subtitle_streams.append(
                SubtitleStream(
                    index=int(stream["index"]),
                    codec_name=str(stream.get("codec_name") or ""),
                    language=tags.get("language"),
                    title=tags.get("title"),
                    default=bool(disposition.get("default", 0)),
                )
            )

        return MediaInfo(
            path=path,
            duration=duration,
            format_name=format_data.get("format_name"),
            audio_stream_count=sum(
                stream.get("codec_type") == "audio" for stream in streams
            ),
            video_stream_count=sum(
                stream.get("codec_type") == "video" for stream in streams
            ),
            subtitle_streams=tuple(subtitle_streams),
            metadata=format_data.get("tags") or {},
        )

    def detect_silences(
        self,
        source: str | os.PathLike[str],
        *,
        noise_db: float = -35.0,
        minimum_duration: float = 0.6,
        media_duration: float | None = None,
        cancel_token: CancellationToken | None = None,
    ) -> tuple[SilenceInterval, ...]:
        if minimum_duration <= 0:
            raise ValueError("minimum_duration must be positive")
        path = Path(source).expanduser().resolve()
        completed = self._run(
            [
                self.ffmpeg,
                "-nostdin",
                "-hide_banner",
                "-i",
                str(path),
                "-af",
                f"silencedetect=noise={noise_db:g}dB:d={minimum_duration:g}",
                "-f",
                "null",
                "-",
            ],
            cancel_token=cancel_token,
        )
        starts = [
            float(match.group("time"))
            for match in _SILENCE_START_RE.finditer(completed.stderr)
        ]
        ends = [
            float(match.group("time"))
            for match in _SILENCE_END_RE.finditer(completed.stderr)
        ]
        intervals: list[SilenceInterval] = []
        for index, start in enumerate(starts):
            if index < len(ends) and ends[index] > start:
                intervals.append(SilenceInterval(start, ends[index]))
        if len(starts) > len(ends):
            duration = media_duration or self.probe(path, cancel_token=cancel_token).duration
            if duration > starts[-1]:
                intervals.append(SilenceInterval(starts[-1], duration))
        return tuple(intervals)

    def split_audio(
        self,
        source: str | os.PathLike[str],
        chunks: Sequence[ChunkSpec],
        *,
        workspace: MediaWorkspace | None = None,
        codec: str = "libmp3lame",
        bitrate: str = "64k",
        cancel_token: CancellationToken | None = None,
    ) -> PreparedMedia:
        """Extract provider-friendly mono/16 kHz audio for every chunk."""

        path = Path(source).expanduser().resolve()
        if not path.is_file():
            raise FileNotFoundError(path)
        owned_workspace = workspace or self.create_workspace(path.stem)
        output_directory = owned_workspace.path / "chunks"
        output_directory.mkdir(parents=True, exist_ok=True)
        prepared: list[PreparedChunk] = []
        try:
            for chunk in sorted(chunks, key=lambda item: item.index):
                (cancel_token or NEVER_CANCELLED).raise_if_cancelled()
                output = output_directory / f"chunk-{chunk.index:06d}.mp3"
                self._run(
                    [
                        self.ffmpeg,
                        "-nostdin",
                        "-hide_banner",
                        "-loglevel",
                        "error",
                        "-ss",
                        f"{chunk.start:.6f}",
                        "-i",
                        str(path),
                        "-t",
                        f"{chunk.duration:.6f}",
                        "-vn",
                        "-map",
                        "0:a:0",
                        "-ac",
                        "1",
                        "-ar",
                        "16000",
                        "-c:a",
                        codec,
                        "-b:a",
                        bitrate,
                        "-y",
                        str(output),
                    ],
                    cancel_token=cancel_token,
                )
                if not output.is_file():
                    raise MediaError(f"ffmpeg did not create {output}")
                prepared.append(PreparedChunk(chunk, output))
        except BaseException:
            if workspace is None:
                owned_workspace.cleanup()
            raise
        return PreparedMedia(path, owned_workspace, tuple(prepared))

    def download_url(
        self,
        url: str,
        *,
        workspace: MediaWorkspace | None = None,
        cancel_token: CancellationToken | None = None,
    ) -> tuple[Path, MediaWorkspace]:
        """Download one URL with yt-dlp into an exclusive workspace."""

        self._validate_url(url)
        owned_workspace = workspace or self.create_workspace("url")
        template = owned_workspace.path / "source.%(ext)s"
        try:
            self._run(
                [
                    self.ytdlp,
                    "--ignore-config",
                    "--no-playlist",
                    "--no-warnings",
                    "--write-info-json",
                    "-f",
                    "bestaudio/best",
                    "-o",
                    str(template),
                    url,
                ],
                cancel_token=cancel_token,
            )
            candidates = sorted(
                path
                for path in owned_workspace.path.glob("source.*")
                if path.is_file()
                and not path.name.endswith((".part", ".ytdl", ".info.json"))
            )
            if not candidates:
                raise MediaError("yt-dlp completed without producing a media file")
            info_path = owned_workspace.path / "source.info.json"
            if info_path.is_file():
                try:
                    metadata = json.loads(info_path.read_text(encoding="utf-8"))
                except (json.JSONDecodeError, OSError, UnicodeError):
                    metadata = {}
                title = str(metadata.get("title") or "").strip()
                if title:
                    owned_workspace.metadata["title"] = title
            return candidates[0], owned_workspace
        except BaseException:
            if workspace is None:
                owned_workspace.cleanup()
            raise

    def discover_local_subtitles(
        self,
        source: str | os.PathLike[str],
        *,
        language: str | None = None,
        cancel_token: CancellationToken | None = None,
    ) -> LocalSubtitleDiscovery:
        path = Path(source).expanduser().resolve()
        if not path.is_file():
            raise FileNotFoundError(path)
        sidecars = self._sidecars(path, language)
        info = self.probe(path, cancel_token=cancel_token)
        return LocalSubtitleDiscovery(
            sidecars=sidecars,
            text_streams=self._rank_streams(info.text_subtitle_streams, language),
            image_streams=self._rank_streams(info.image_subtitle_streams, language),
            unknown_streams=tuple(
                stream
                for stream in info.subtitle_streams
                if stream.kind == SubtitleKind.UNKNOWN
            ),
        )

    def resolve_subtitles(
        self,
        source: str | os.PathLike[str],
        *,
        prefer_existing_subtitles: bool = False,
        language: str | None = None,
        workspace: MediaWorkspace | None = None,
        fallback_to_audio: bool = False,
        allow_automatic: bool = True,
        cancel_token: CancellationToken | None = None,
    ) -> SubtitleAsset | None:
        """Optionally resolve an existing timed transcript before audio.

        ``None`` means "continue with audio" and is only returned when the
        preference is disabled or ``fallback_to_audio`` is explicitly true.
        """

        if not prefer_existing_subtitles:
            return None
        return self.prefer_existing_subtitles(
            source,
            language=language,
            workspace=workspace,
            fallback_to_audio=fallback_to_audio,
            allow_automatic=allow_automatic,
            cancel_token=cancel_token,
        )

    def prefer_existing_subtitles(
        self,
        source: str | os.PathLike[str],
        *,
        language: str | None = None,
        workspace: MediaWorkspace | None = None,
        fallback_to_audio: bool = False,
        allow_automatic: bool = True,
        cancel_token: CancellationToken | None = None,
    ) -> SubtitleAsset | None:
        """Use sidecar/embedded/manual/automatic subtitles in that order."""

        source_text = os.fspath(source)
        if self._is_url(source_text):
            try:
                return self.download_url_subtitles(
                    source_text,
                    language=language,
                    workspace=workspace,
                    allow_automatic=allow_automatic,
                    cancel_token=cancel_token,
                )
            except SubtitleUnavailableError:
                if fallback_to_audio:
                    return None
                raise

        path = Path(source).expanduser().resolve()
        discovery = self.discover_local_subtitles(
            path, language=language, cancel_token=cancel_token
        )
        for sidecar in discovery.sidecars:
            sidecar_language = self._sidecar_language(path, sidecar)
            transcript = load_subtitle_file(
                sidecar,
                language=sidecar_language or language,
            )
            if not transcript.is_empty:
                return SubtitleAsset(
                    transcript=transcript,
                    origin=SubtitleOrigin.SIDECAR,
                    path=sidecar,
                    language=transcript.language,
                )

        if discovery.text_streams:
            owned_workspace = workspace or self.create_workspace(f"{path.stem}-subtitles")
            workspace_leased = False
            try:
                output_directory = owned_workspace.path / "subtitles"
                output_directory.mkdir(parents=True, exist_ok=True)
                for stream in discovery.text_streams:
                    output = output_directory / f"embedded-{stream.index:03d}.vtt"
                    try:
                        self._extract_subtitle_stream(
                            path, stream, output, cancel_token=cancel_token
                        )
                        transcript = load_subtitle_file(
                            output,
                            language=(
                                self._normalize_language(stream.language) or language
                            ),
                        )
                    except (MediaCommandError, UnicodeError, ValueError):
                        continue
                    if not transcript.is_empty:
                        workspace_leased = workspace is None
                        return SubtitleAsset(
                            transcript=transcript,
                            origin=SubtitleOrigin.EMBEDDED,
                            path=output,
                            language=transcript.language,
                            stream_index=stream.index,
                            workspace_owner=(
                                owned_workspace if workspace is None else None
                            ),
                        )
            finally:
                if workspace is None and not workspace_leased:
                    owned_workspace.cleanup()

        if discovery.image_streams:
            if fallback_to_audio:
                return None
            raise ImageSubtitleUnsupportedError(discovery.image_streams)
        if fallback_to_audio:
            return None
        raise SubtitleUnavailableError("no suitable text subtitles found")

    def download_url_subtitles(
        self,
        url: str,
        *,
        language: str | None,
        workspace: MediaWorkspace | None = None,
        allow_automatic: bool = True,
        cancel_token: CancellationToken | None = None,
    ) -> SubtitleAsset:
        """Ask yt-dlp for manual subtitles, then automatic captions."""

        self._validate_url(url)
        owned_workspace = workspace or self.create_workspace("url-subtitles")
        try:
            metadata_result = self._run(
                [
                    self.ytdlp,
                    "--ignore-config",
                    "--dump-single-json",
                    "--skip-download",
                    "--no-playlist",
                    "--no-warnings",
                    url,
                ],
                cancel_token=cancel_token,
            )
            try:
                metadata = json.loads(metadata_result.stdout)
            except json.JSONDecodeError as error:
                raise MediaError("yt-dlp returned invalid metadata JSON") from error
            title = str(metadata.get("title") or "").strip()
            if title:
                owned_workspace.metadata["title"] = title

            choices = [
                (False, metadata.get("subtitles") or {}),
            ]
            if allow_automatic:
                choices.append((True, metadata.get("automatic_captions") or {}))

            original_language = (
                metadata.get("language")
                or metadata.get("original_language")
                or metadata.get("audio_language")
            )
            for automatic, available in choices:
                if language is not None:
                    selected_language = self._select_language(
                        tuple(available),
                        language,
                    )
                elif original_language:
                    selected_language = self._select_language(
                        tuple(available),
                        str(original_language),
                    )
                else:
                    selected_language = None
                if selected_language is None and language is None:
                    selected_language = self._select_language(tuple(available), None)
                if selected_language is None:
                    continue
                output = self._download_one_url_subtitle(
                    url,
                    selected_language,
                    automatic=automatic,
                    workspace=owned_workspace,
                    cancel_token=cancel_token,
                )
                transcript = load_subtitle_file(output, language=selected_language)
                if transcript.is_empty:
                    continue
                return SubtitleAsset(
                    transcript=transcript,
                    origin=(
                        SubtitleOrigin.URL_AUTOMATIC
                        if automatic
                        else SubtitleOrigin.URL_MANUAL
                    ),
                    path=output,
                    language=selected_language,
                    automatic=automatic,
                    workspace_owner=owned_workspace if workspace is None else None,
                )
            raise SubtitleUnavailableError(
                f"no subtitles available for language {language!r}"
            )
        except BaseException:
            if workspace is None:
                owned_workspace.cleanup()
            raise

    def _download_one_url_subtitle(
        self,
        url: str,
        language: str,
        *,
        automatic: bool,
        workspace: MediaWorkspace,
        cancel_token: CancellationToken | None,
    ) -> Path:
        prefix = "automatic" if automatic else "manual"
        template = workspace.path / f"{prefix}.%(language)s.%(ext)s"
        mode = (
            ["--no-write-subs", "--write-auto-subs"]
            if automatic
            else ["--write-subs", "--no-write-auto-subs"]
        )
        self._run(
            [
                self.ytdlp,
                "--ignore-config",
                "--skip-download",
                "--no-playlist",
                "--no-warnings",
                *mode,
                "--sub-langs",
                language,
                "--sub-format",
                "vtt/best",
                "--convert-subs",
                "vtt",
                "-o",
                str(template),
                url,
            ],
            cancel_token=cancel_token,
        )
        candidates = sorted(workspace.path.glob(f"{prefix}.*.vtt"))
        if not candidates:
            raise SubtitleUnavailableError(
                f"yt-dlp did not download {language!r} subtitles"
            )
        return candidates[0]

    def _extract_subtitle_stream(
        self,
        source: Path,
        stream: SubtitleStream,
        output: Path,
        *,
        cancel_token: CancellationToken | None,
    ) -> None:
        if stream.kind == SubtitleKind.IMAGE:
            raise ImageSubtitleUnsupportedError((stream,))
        self._run(
            [
                self.ffmpeg,
                "-nostdin",
                "-hide_banner",
                "-loglevel",
                "error",
                "-i",
                str(source),
                "-map",
                f"0:{stream.index}",
                "-c:s",
                "webvtt",
                "-f",
                "webvtt",
                "-y",
                str(output),
            ],
            cancel_token=cancel_token,
        )

    def _run(
        self,
        command: Sequence[str],
        *,
        cancel_token: CancellationToken | None = None,
    ) -> subprocess.CompletedProcess[str]:
        token = cancel_token or NEVER_CANCELLED
        token.raise_if_cancelled()
        executable = command[0]
        if not (
            (os.path.isabs(executable) and os.access(executable, os.X_OK))
            or shutil.which(executable)
        ):
            raise MediaDependencyError(f"required executable not found: {executable}")

        process = subprocess.Popen(
            list(command),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        while True:
            try:
                stdout, stderr = process.communicate(timeout=0.2)
                break
            except subprocess.TimeoutExpired:
                if token.cancelled:
                    process.terminate()
                    try:
                        process.communicate(timeout=1)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.communicate()
                    raise OperationCancelled("operation cancelled") from None
        completed = subprocess.CompletedProcess(command, process.returncode, stdout, stderr)
        if process.returncode:
            raise MediaCommandError(command, process.returncode, stderr)
        return completed

    @staticmethod
    def _sidecars(source: Path, language: str | None) -> tuple[Path, ...]:
        base = source.stem.casefold()
        candidates = [
            path
            for path in source.parent.iterdir()
            if path.is_file()
            and path.suffix.casefold() in {".srt", ".vtt"}
            and (
                path.stem.casefold() == base
                or path.stem.casefold().startswith(f"{base}.")
            )
            and MediaProcessor._language_compatible(
                MediaProcessor._sidecar_language(source, path),
                language,
            )
        ]

        def rank(path: Path) -> tuple[int, int, str]:
            sidecar_language = MediaProcessor._sidecar_language(source, path)
            language_rank = MediaProcessor._language_rank(sidecar_language, language)
            format_rank = 0 if path.suffix.casefold() == ".vtt" else 1
            return language_rank, format_rank, path.name.casefold()

        return tuple(sorted(candidates, key=rank))

    @staticmethod
    def _sidecar_language(source: Path, sidecar: Path) -> str | None:
        suffix = sidecar.stem[len(source.stem) :].lstrip(".")
        for token in suffix.split("."):
            candidate = token.strip()
            if not _LANGUAGE_TAG_RE.fullmatch(candidate):
                continue
            base = candidate.replace("_", "-").casefold().split("-", 1)[0]
            if len(base) == 2 or base in _LANGUAGE_ALIASES:
                return MediaProcessor._normalize_language(candidate)
        return None

    @staticmethod
    def _rank_streams(
        streams: Sequence[SubtitleStream],
        language: str | None,
    ) -> tuple[SubtitleStream, ...]:
        def rank(stream: SubtitleStream) -> tuple[int | bool, int | bool, int]:
            language_rank = MediaProcessor._language_rank(stream.language, language)
            if language is None:
                return not stream.default, language_rank, stream.index
            return language_rank, not stream.default, stream.index

        return tuple(
            sorted(
                (
                    stream
                    for stream in streams
                    if MediaProcessor._language_compatible(stream.language, language)
                ),
                key=rank,
            )
        )

    @staticmethod
    def _language_rank(candidate: str | None, requested: str | None) -> int:
        if not requested:
            return 1 if MediaProcessor._normalize_language(candidate) else 0
        if not candidate:
            return 3
        normalized_candidate = MediaProcessor._normalize_language(candidate)
        normalized_requested = MediaProcessor._normalize_language(requested)
        if not normalized_candidate or not normalized_requested:
            return 3
        if normalized_candidate == normalized_requested:
            return 0
        requested_base = normalized_requested.split("-", 1)[0]
        candidate_base = normalized_candidate.split("-", 1)[0]
        if candidate_base == requested_base:
            return 1
        return 4

    @staticmethod
    def _normalize_language(language: str | None) -> str | None:
        normalized = (language or "").strip().replace("_", "-").casefold()
        if normalized in _UNDEFINED_LANGUAGES:
            return None
        base, separator, remainder = normalized.partition("-")
        base = _LANGUAGE_ALIASES.get(base, base)
        return f"{base}-{remainder}" if separator and remainder else base

    @staticmethod
    def _language_compatible(candidate: str | None, requested: str | None) -> bool:
        normalized_candidate = MediaProcessor._normalize_language(candidate)
        normalized_requested = MediaProcessor._normalize_language(requested)
        if not normalized_candidate or not normalized_requested:
            return True
        return (
            normalized_candidate == normalized_requested
            or normalized_candidate.split("-", 1)[0]
            == normalized_requested.split("-", 1)[0]
        )

    @staticmethod
    def _select_language(
        available: Sequence[str],
        requested: str | None,
    ) -> str | None:
        candidates = tuple(
            candidate
            for candidate in available
            if candidate.casefold() != "live_chat"
        )
        if not candidates:
            return None
        if requested:
            ranked = sorted(
                (
                    (MediaProcessor._language_rank(candidate, requested), candidate)
                    for candidate in candidates
                ),
                key=lambda item: (item[0], item[1]),
            )
            return ranked[0][1] if ranked[0][0] <= 1 else None
        return candidates[0]

    @staticmethod
    def _is_url(value: str) -> bool:
        parsed = urlparse(value)
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)

    @classmethod
    def _validate_url(cls, value: str) -> None:
        if not cls._is_url(value):
            raise ValueError("only http(s) media URLs are supported")
