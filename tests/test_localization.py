from __future__ import annotations

import json
import re
from pathlib import Path
from string import Formatter

import pytest

from sao_francisco.catalog import MODEL_CATALOG
from sao_francisco.help_system import HelpDocument
from sao_francisco.i18n import (
    DEFAULT_LOCALE,
    LANGUAGES,
    RESOURCE_ROOT,
    Localizer,
    catalog,
    normalize_locale,
    translated_help,
)
from scripts.inventory_i18n import LITERAL, human_text


def test_default_and_unknown_locale_use_english() -> None:
    assert DEFAULT_LOCALE == normalize_locale(None) == normalize_locale("xx-ZZ") == "en-US"
    assert normalize_locale("pt_BR") == "pt-BR"
    assert normalize_locale("ar") == "ar"
    assert Localizer().text("Transcrever") == "Transcribe"
    assert Localizer("pt-BR").text("Transcrever") == "Transcrever"


def _fields(text: str) -> set[str]:
    return {name for _part, name, _fmt, _conv in Formatter().parse(text) if name}


def test_catalogs_have_no_duplicates_empty_values_or_broken_placeholders() -> None:
    seen: set[str] = set()
    for path in RESOURCE_ROOT.glob("*.json"):
        pairs = json.loads(path.read_text(), object_pairs_hook=list)
        for source, translations in pairs:
            assert source not in seen, source
            seen.add(source)
            assert len(translations) == 8, source
            for translated in translations:
                assert translated.strip(), source
                assert _fields(source) == _fields(translated), source
    assert len(catalog()) >= 300


@pytest.mark.parametrize("locale", [code for code, _name in LANGUAGES])
def test_help_sections_and_links_are_complete(locale: str) -> None:
    original = HelpDocument(translated_help("pt-BR"))
    anchors = tuple(section.anchor for section in original.sections)
    doc = HelpDocument(translated_help(locale), anchors=anchors)
    assert len(doc.sections) == 11
    assert tuple(section.anchor for section in doc.sections) == anchors
    assert set(re.findall(r"https://[^)\s]+", original.markdown)) == set(
        re.findall(r"https://[^)\s]+", doc.markdown)
    )
    assert doc.search(doc.sections[0].title.split()[0])
    if locale != "pt-BR":
        assert (RESOURCE_ROOT / "help" / f"{locale}.md").is_file()
        assert "Preços de referência" not in doc.markdown


def test_qml_product_copy_is_catalogued_and_wrapped() -> None:
    for path in (RESOURCE_ROOT.parent / "qml").rglob("*.qml"):
        for number, line in enumerate(path.read_text().splitlines(), 1):
            if line.lstrip().startswith(("//", "import ")):
                continue
            for literal in LITERAL.finditer(line):
                source = json.loads(literal.group())
                if human_text(source):
                    assert source in catalog(), f"{path.name}:{number}: {source}"
                    call = f'qsTranslate("App", {literal.group()})'
                    assert call in line, f"{path.name}:{number}: {source}"


@pytest.mark.parametrize("locale", [code for code, _name in LANGUAGES])
def test_models_and_system_messages_do_not_translate_user_content(locale: str) -> None:
    localizer = Localizer(locale)
    for model in MODEL_CATALOG:
        for source in (model.name, model.summary, model.capability_label):
            assert source in catalog()
    title = "Concluída; os arquivos estão prontos."
    snapshot = {"title": title, "sourceName": title, "path": "C:/Users/Fonte/áudio.wav",
                "detail": "Transcrevendo parte 2 de 17…", "model": "whisper-1"}
    translated = localizer.presentation(snapshot)
    for field in ("title", "sourceName", "path", "model"):
        assert translated[field] == snapshot[field]
    assert snapshot["detail"] == "Transcrevendo parte 2 de 17…"
    assert "2" in translated["detail"] and "17" in translated["detail"]
    if locale != "pt-BR":
        assert translated["detail"] != snapshot["detail"]
        assert localizer.message("A OpenAI não aceitou a chave configurada.") != (
            "A OpenAI não aceitou a chave configurada."
        )
        assert localizer.message("O Gemini não aceitou a chave configurada.") != (
            "O Gemini não aceitou a chave configurada."
        )
    private = "private unrelated text {example}"
    assert localizer.message(private) == private


def test_missing_help_locale_falls_back_to_english(monkeypatch, tmp_path: Path) -> None:
    import sao_francisco.i18n as module

    (tmp_path / "help").mkdir()
    (tmp_path / "help/en-US.md").write_text("English fallback", encoding="utf-8")
    monkeypatch.setattr(module, "RESOURCE_ROOT", tmp_path)
    assert module.translated_help("de-DE") == "English fallback"
