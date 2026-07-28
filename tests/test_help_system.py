from pathlib import Path

import pytest

from sao_francisco.help_system import HelpContentError, HelpDocument

HELP_PATH = Path(__file__).resolve().parents[1] / "sao_francisco" / "AJUDA.md"


def test_real_help_is_complete_searchable_and_has_unique_anchors() -> None:
    document = HelpDocument.from_path(HELP_PATH)

    assert document.title == "Ajuda do São Francisco"
    assert len(document.sections) >= 10
    assert len({section.anchor for section in document.sections}) == len(
        document.sections
    )
    assert document.first_anchor == "primeiros-passos"
    assert "Como mídias longas são processadas" in [
        result["title"] for result in document.search("MIDIAS longas")
    ]
    assert len(document.search("")) == len(document.sections)


def test_invalid_anchor_falls_back_to_first_section() -> None:
    document = HelpDocument.from_path(HELP_PATH)
    assert document.section("nao-existe").anchor == document.first_anchor


def test_duplicate_normalized_anchors_are_rejected() -> None:
    with pytest.raises(HelpContentError, match="mesma âncora"):
        HelpDocument("# Ajuda\n\n## Ação\nTexto.\n\n## Acao\nOutro.")
