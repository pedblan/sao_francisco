from __future__ import annotations

import zipfile

import pytest

from sao_francisco.core import (
    Segment,
    Transcript,
    export_docx,
    export_srt,
    export_transcript,
    export_txt,
    export_vtt,
    format_timestamp,
)


@pytest.fixture
def transcript() -> Transcript:
    return Transcript(
        segments=(
            Segment(0.25, 2.5, "Bom dia.", speaker="Ana"),
            Segment(3, 4.125, "Tudo bem?"),
        ),
        language="pt-BR",
        duration=5,
        metadata={"title": "Entrevista"},
    )


def test_timestamp_rounding_carries_across_seconds() -> None:
    assert format_timestamp(59.9996, decimal_separator=",") == "00:01:00,000"
    assert format_timestamp(100 * 3600) == "100:00:00.000"


def test_text_and_caption_exports_are_utf8_and_timed(tmp_path, transcript) -> None:
    txt = export_txt(transcript, tmp_path / "fala.txt", include_timestamps=True)
    srt = export_srt(transcript, tmp_path / "fala.srt")
    vtt = export_vtt(transcript, tmp_path / "fala.vtt")

    assert "[00:00:00] Ana: Bom dia." in txt.read_text(encoding="utf-8")
    assert "00:00:00,250 --> 00:00:02,500" in srt.read_text(encoding="utf-8")
    assert vtt.read_text(encoding="utf-8").startswith("WEBVTT\n\n")
    assert "<v Ana>Bom dia.</v>" in vtt.read_text(encoding="utf-8")


def test_untimed_text_merges_caption_cues_into_readable_paragraphs(
    tmp_path, transcript
) -> None:
    txt = export_txt(transcript, tmp_path / "fala-sem-tempos.txt")

    assert txt.read_text(encoding="utf-8") == "Ana: Bom dia.\n\nTudo bem?\n"


def test_generic_export_uses_suffix_and_rejects_unknown_format(
    tmp_path, transcript
) -> None:
    result = export_transcript(transcript, tmp_path / "automatico.srt")
    assert result.suffix == ".srt"
    with pytest.raises(ValueError, match="unsupported"):
        export_transcript(transcript, tmp_path / "automatico.xyz")


def test_docx_export_is_a_valid_office_package(tmp_path, transcript) -> None:
    pytest.importorskip("docx")
    output = export_docx(
        transcript,
        tmp_path / "fala.docx",
        include_timestamps=True,
        title="Entrevista",
    )

    assert zipfile.is_zipfile(output)
    with zipfile.ZipFile(output) as package:
        document_xml = package.read("word/document.xml").decode("utf-8")
    assert "Entrevista" in document_xml
    assert "Bom dia." in document_xml
