"""Offline product-copy localization. Never translate arbitrary user/provider text."""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

DEFAULT_LOCALE = "en-US"
TRANSLATION_LOCALES = ("en-US", "fr-FR", "es-ES", "de-DE", "it-IT", "ru-RU", "zh-CN", "ar")
LANGUAGES = (
    ("en-US", "English"), ("pt-BR", "Português (Brasil)"), ("fr-FR", "Français"),
    ("es-ES", "Español"), ("de-DE", "Deutsch"), ("it-IT", "Italiano"),
    ("ru-RU", "Русский"), ("zh-CN", "简体中文"), ("ar", "العربية"),
)
RESOURCE_ROOT = Path(__file__).with_name("translations")


def normalize_locale(value: str | None) -> str:
    normalized = (value or "").replace("_", "-").lower()
    for code, _name in LANGUAGES:
        if normalized == code.lower() or normalized == code.split("-")[0]:
            return code
    return DEFAULT_LOCALE


@lru_cache(maxsize=1)
def catalog() -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for path in sorted(RESOURCE_ROOT.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        for source, translations in data.items():
            if source in result or len(translations) != len(TRANSLATION_LOCALES):
                raise ValueError(f"Invalid translation entry in {path.name}: {source}")
            if not all(isinstance(text, str) and text for text in translations):
                raise ValueError(f"Empty translation in {path.name}: {source}")
            result[source] = translations
    # Exact variants keep provider names intact while handling Portuguese articles.
    for source, translations in tuple(result.items()):
        if "{provider}" not in source:
            continue
        for provider in ("OpenAI", "Gemini"):
            variant = source.replace("{provider}", provider)
            if provider == "Gemini":
                for before, after in (("A Gemini", "O Gemini"),
                                      ("da Gemini", "do Gemini"),
                                      ("a Gemini", "o Gemini")):
                    variant = variant.replace(before, after)
            result.setdefault(variant, [t.replace("{provider}", provider) for t in translations])
    return result


class Localizer:
    def __init__(self, locale: str | None = None) -> None:
        self.locale = normalize_locale(locale)

    def text(self, source: str) -> str:
        if self.locale == "pt-BR":
            return source
        translations = catalog().get(source)
        if translations is None:
            return source
        index = TRANSLATION_LOCALES.index(self.locale)
        return translations[index] or translations[0]

    def message(self, source: str) -> str:
        """Only match complete, catalogued system sentences, preserving inserted values."""
        direct = self.text(source)
        if source in catalog() or self.locale == "pt-BR":
            return direct
        for template, pattern, names in message_patterns():
            match = pattern.fullmatch(source)
            if match:
                values = dict(zip(names, match.groups(), strict=True))
                if "message" in values:
                    values["message"] = self.text(values["message"])
                if "amount" in values and self.locale in {"en-US", "zh-CN", "ar"}:
                    values["amount"] = values["amount"].replace(",", ".")
                if "tokens" in values and self.locale in {"en-US", "zh-CN", "ar"}:
                    values["tokens"] = values["tokens"].replace(".", ",")
                # Values may include names, paths or provider errors: never translate them.
                return self.text(template).format_map(values)
        return source

    def presentation(self, value: dict[str, Any]) -> dict[str, Any]:
        result = dict(value)
        for key in ("detail", "modelLabel", "costLabel", "usageLabel", "summary", "capability"):
            if isinstance(result.get(key), str):
                result[key] = self.message(result[key])
        return result

    def notices(self, markdown: str) -> str:
        if self.locale == "pt-BR":
            return markdown
        blocks = re.split(r"\n\s*\n|\n(?=- )", markdown.strip())
        return "\n\n".join(self.text(" ".join(block.split())) for block in blocks) + "\n"


@lru_cache(maxsize=1)
def message_patterns() -> tuple[tuple[str, re.Pattern[str], tuple[str, ...]], ...]:
    patterns = []
    for source in catalog():
        names = tuple(re.findall(r"\{([a-z][a-z0-9_]*)\}", source))
        if not names:
            continue
        pattern = re.escape(source)
        for name in names:
            capture = "(.+?)"
            if name in {"done", "total", "part", "count", "code"}:
                capture = r"(-?\d+)"
            elif name in {"tokens", "amount"}:
                capture = r"([\d.,]+)"
            pattern = pattern.replace(re.escape("{" + name + "}"), capture, 1)
        patterns.append((source, re.compile(pattern, re.DOTALL), names))
    return tuple(sorted(patterns, key=lambda item: len(item[0]), reverse=True))


def translated_help(locale: str) -> str:
    path = RESOURCE_ROOT / "help" / f"{normalize_locale(locale)}.md"
    if normalize_locale(locale) == "pt-BR":
        path = RESOURCE_ROOT.parent / "AJUDA.md"
    if not path.is_file():
        path = RESOURCE_ROOT / "help" / f"{DEFAULT_LOCALE}.md"
    return path.read_text(encoding="utf-8")
