from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

from sao_francisco.core import (
    CancellationToken,
    ImageSubtitleUnsupportedError,
    MediaInfo,
    MediaProcessor,
    OperationCancelled,
    SubtitleKind,
    SubtitleOrigin,
    SubtitleStream,
    classify_subtitle_codec,
    parse_srt,
    parse_vtt,
)
from sao_francisco.core.media import (
    _default_ytdlp_command,
    _resolve_executable,
    _subprocess_environment,
)

SAMPLE_VTT = """WEBVTT

00:00:01.000 --> 00:00:02.500
<v Ana>Bom dia.</v>

00:02.500 --> 00:04.000 align:start
Tudo bem?
"""


def test_srt_and_vtt_are_parsed_into_canonical_segments() -> None:
    srt = """1
00:00:00,500 --> 00:00:01,750
Olá, mundo.

2
00:00:02,000 --> 00:00:03,000
Segunda linha.
"""

    srt_transcript = parse_srt(srt, language="pt")
    vtt_transcript = parse_vtt(SAMPLE_VTT, language="pt")

    assert srt_transcript.segments[0].start == 0.5
    assert srt_transcript.segments[0].end == 1.75
    assert vtt_transcript.segments[0].speaker == "Ana"
    assert vtt_transcript.segments[1].text == "Tudo bem?"
    assert vtt_transcript.duration == 4


def test_progressive_youtube_vtt_cues_are_deduplicated_and_compacted() -> None:
    progressive = """WEBVTT

00:00:03.000 --> 00:00:03.800
trata-se de um projeto de lei já

00:00:03.800 --> 00:00:07.800
trata-se de um projeto de lei já
aprovado que detalha o

00:00:07.800 --> 00:00:07.900
aprovado que detalha o

00:00:07.900 --> 00:00:11.000
aprovado que detalha o
investimento nas estradas
"""

    transcript = parse_vtt(progressive, language="pt")

    assert len(transcript.segments) == 1
    assert transcript.text == (
        "trata-se de um projeto de lei já aprovado que detalha o "
        "investimento nas estradas"
    )
    assert transcript.text.count("aprovado que detalha o") == 1
    assert transcript.segments[0].metadata["rolling_cues_normalized"] is True


def test_bitmap_subtitle_codecs_are_explicitly_classified() -> None:
    assert classify_subtitle_codec("hdmv_pgs_subtitle") == SubtitleKind.IMAGE
    assert classify_subtitle_codec("dvd_subtitle") == SubtitleKind.IMAGE
    assert classify_subtitle_codec("subrip") == SubtitleKind.TEXT


class LocalProcessor(MediaProcessor):
    def __init__(self, info: MediaInfo, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.info = info

    def probe(self, source: str | Path, **_kwargs: object) -> MediaInfo:
        return self.info


def test_local_sidecar_in_requested_language_wins(tmp_path) -> None:
    media = tmp_path / "aula.mp4"
    media.write_bytes(b"not real media")
    (tmp_path / "aula.en.vtt").write_text(
        SAMPLE_VTT.replace("Bom dia.", "Good morning."),
        encoding="utf-8",
    )
    preferred = tmp_path / "aula.pt-BR.srt"
    preferred.write_text(
        "1\n00:00:01,000 --> 00:00:02,000\nBom dia.\n",
        encoding="utf-8",
    )
    info = MediaInfo(media, 10, "mp4", 1, 1)
    processor = LocalProcessor(info)

    asset = processor.prefer_existing_subtitles(media, language="pt-BR")

    assert asset is not None
    assert asset.origin == SubtitleOrigin.SIDECAR
    assert asset.path == preferred
    assert asset.transcript.text == "Bom dia."


def test_incompatible_labeled_sidecar_falls_back_to_audio(tmp_path) -> None:
    media = tmp_path / "aula.mp4"
    media.write_bytes(b"not real media")
    (tmp_path / "aula.en.vtt").write_text(SAMPLE_VTT, encoding="utf-8")
    info = MediaInfo(media, 10, "mp4", 1, 1)
    processor = LocalProcessor(info)

    assert (
        processor.prefer_existing_subtitles(
            media,
            language="pt-BR",
            fallback_to_audio=True,
        )
        is None
    )


def test_iso_639_three_letter_alias_matches_requested_language(tmp_path) -> None:
    media = tmp_path / "aula.mkv"
    media.write_bytes(b"not real media")
    portuguese = SubtitleStream(2, "webvtt", language="por")
    english = SubtitleStream(3, "webvtt", language="eng", default=True)
    info = MediaInfo(media, 10, "matroska", 1, 1, (english, portuguese))
    processor = LocalProcessor(info)

    discovery = processor.discover_local_subtitles(media, language="pt-BR")

    assert discovery.text_streams == (portuguese,)


def test_automatic_language_prefers_default_embedded_stream(tmp_path) -> None:
    media = tmp_path / "aula.mkv"
    media.write_bytes(b"not real media")
    first = SubtitleStream(2, "webvtt")
    default = SubtitleStream(3, "webvtt", language="en", default=True)
    info = MediaInfo(media, 10, "matroska", 1, 1, (first, default))
    processor = LocalProcessor(info)

    discovery = processor.discover_local_subtitles(media)

    assert discovery.text_streams == (default, first)


class ExtractingLocalProcessor(LocalProcessor):
    def _extract_subtitle_stream(
        self,
        source: Path,
        stream: SubtitleStream,
        output: Path,
        *,
        cancel_token: CancellationToken | None,
    ) -> None:
        output.write_text(SAMPLE_VTT, encoding="utf-8")


def test_internally_owned_embedded_subtitle_workspace_can_be_released(tmp_path) -> None:
    media = tmp_path / "aula.mkv"
    media.write_bytes(b"not real media")
    stream = SubtitleStream(2, "webvtt", language="por")
    info = MediaInfo(media, 10, "matroska", 1, 1, (stream,))
    processor = ExtractingLocalProcessor(info, work_root=tmp_path)

    asset = processor.prefer_existing_subtitles(media, language="pt")

    assert asset is not None
    assert asset.path.is_file()
    workspace_path = asset.path.parent.parent
    asset.cleanup()
    assert not workspace_path.exists()


def test_image_only_local_subtitles_require_explicit_audio_fallback(tmp_path) -> None:
    media = tmp_path / "filme.mkv"
    media.write_bytes(b"not real media")
    stream = SubtitleStream(2, "hdmv_pgs_subtitle", language="pt")
    info = MediaInfo(media, 10, "matroska", 1, 1, (stream,))
    processor = LocalProcessor(info)

    with pytest.raises(ImageSubtitleUnsupportedError) as captured:
        processor.prefer_existing_subtitles(media, language="pt")
    assert captured.value.streams[0].kind == SubtitleKind.IMAGE
    assert (
        processor.prefer_existing_subtitles(
            media, language="pt", fallback_to_audio=True
        )
        is None
    )


class UrlSubtitleProcessor(MediaProcessor):
    def _run(
        self,
        command: list[str] | tuple[str, ...],
        *,
        cancel_token: CancellationToken | None = None,
    ) -> subprocess.CompletedProcess[str]:
        if "--dump-single-json" in command:
            metadata = {
                "title": "Aula publicada",
                "subtitles": {"en": [{"ext": "vtt"}]},
                "automatic_captions": {"pt-BR": [{"ext": "vtt"}]},
            }
            return subprocess.CompletedProcess(command, 0, json.dumps(metadata), "")
        output_template = Path(command[command.index("-o") + 1])
        prefix = output_template.name.split(".", 1)[0]
        language = command[command.index("--sub-langs") + 1]
        output = output_template.parent / f"{prefix}.{language}.vtt"
        output.write_text(SAMPLE_VTT, encoding="utf-8")
        return subprocess.CompletedProcess(command, 0, "", "")


class UrlDownloadProcessor(MediaProcessor):
    def _run(
        self,
        command: list[str] | tuple[str, ...],
        *,
        cancel_token: CancellationToken | None = None,
    ) -> subprocess.CompletedProcess[str]:
        assert "--write-info-json" in command
        output_template = Path(command[command.index("-o") + 1])
        (output_template.parent / "source.mp3").write_bytes(b"audio")
        (output_template.parent / "source.info.json").write_text(
            json.dumps({"title": "Conferência anual"}),
            encoding="utf-8",
        )
        return subprocess.CompletedProcess(command, 0, "", "")


def test_url_download_keeps_title_metadata_separate_from_media(tmp_path) -> None:
    processor = UrlDownloadProcessor(work_root=tmp_path)
    with processor.create_workspace("download") as workspace:
        path, returned_workspace = processor.download_url(
            "https://example.com/video",
            workspace=workspace,
        )

        assert path.name == "source.mp3"
        assert returned_workspace is workspace
        assert workspace.metadata["title"] == "Conferência anual"


def test_url_subtitles_try_manual_then_matching_automatic_language(tmp_path) -> None:
    processor = UrlSubtitleProcessor(work_root=tmp_path)
    with processor.create_workspace("captions") as workspace:
        asset = processor.download_url_subtitles(
            "https://example.com/video",
            language="pt-BR",
            workspace=workspace,
        )

        assert asset.origin == SubtitleOrigin.URL_AUTOMATIC
        assert asset.automatic
        assert asset.language == "pt-BR"
        assert asset.transcript.text == "Bom dia. Tudo bem?"
        assert workspace.metadata["title"] == "Aula publicada"


class OriginalLanguageUrlProcessor(UrlSubtitleProcessor):
    def _run(
        self,
        command: list[str] | tuple[str, ...],
        *,
        cancel_token: CancellationToken | None = None,
    ) -> subprocess.CompletedProcess[str]:
        if "--dump-single-json" in command:
            metadata = {
                "language": "por",
                "subtitles": {
                    "en": [{"ext": "vtt"}],
                    "pt-BR": [{"ext": "vtt"}],
                },
            }
            return subprocess.CompletedProcess(command, 0, json.dumps(metadata), "")
        return super()._run(command, cancel_token=cancel_token)


def test_automatic_language_uses_url_original_language_hint(tmp_path) -> None:
    processor = OriginalLanguageUrlProcessor(work_root=tmp_path)
    with processor.create_workspace("captions") as workspace:
        asset = processor.download_url_subtitles(
            "https://example.com/video",
            language=None,
            workspace=workspace,
        )

    assert asset.language == "pt-BR"


def test_internally_owned_url_subtitle_workspace_can_be_released(tmp_path) -> None:
    processor = UrlSubtitleProcessor(work_root=tmp_path)

    asset = processor.download_url_subtitles(
        "https://example.com/video",
        language="pt-BR",
    )

    assert asset.path.is_file()
    workspace_path = asset.path.parent
    asset.cleanup()
    assert not workspace_path.exists()


def test_cancelled_media_command_does_not_start_subprocess() -> None:
    token = CancellationToken()
    token.cancel()
    with pytest.raises(OperationCancelled):
        MediaProcessor()._run(["executable-that-does-not-exist"], cancel_token=token)


def test_executable_resolution_uses_the_explicit_search_path(tmp_path) -> None:
    executable = tmp_path / "media-tool"
    executable.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    executable.chmod(0o755)

    assert _resolve_executable("media-tool", str(tmp_path)) == str(executable)


def test_default_ytdlp_command_uses_bundled_executable_when_frozen(
    monkeypatch,
) -> None:
    monkeypatch.setattr("sao_francisco.core.media.sys.frozen", True, raising=False)
    monkeypatch.setattr(
        "sao_francisco.core.media.sys.executable",
        "/Applications/São Francisco.app/Contents/MacOS/São Francisco",
    )

    assert _default_ytdlp_command() == (
        "/Applications/São Francisco.app/Contents/MacOS/São Francisco",
        "--yt-dlp",
    )


def test_default_ytdlp_command_uses_installed_module_from_source(
    monkeypatch,
) -> None:
    monkeypatch.delattr("sao_francisco.core.media.sys.frozen", raising=False)
    monkeypatch.setattr(
        "sao_francisco.core.media.sys.executable",
        "/private/tmp/sao-francisco-venv/bin/python",
    )

    assert _default_ytdlp_command() == (
        "/private/tmp/sao-francisco-venv/bin/python",
        "-m",
        "yt_dlp",
    )


def test_frozen_application_directory_is_first_on_media_path(
    tmp_path,
    monkeypatch,
) -> None:
    executable = tmp_path / "São Francisco.exe"
    monkeypatch.setattr("sao_francisco.core.media.sys.frozen", True, raising=False)
    monkeypatch.setattr("sao_francisco.core.media.sys.executable", str(executable))

    search_path = _subprocess_environment()["PATH"].split(os.pathsep)

    assert search_path[0] == str(tmp_path)
