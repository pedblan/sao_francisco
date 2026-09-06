from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path


class HelpContentError(RuntimeError):
    """O manual integrado não pôde ser carregado com segurança."""


@dataclass(frozen=True, slots=True)
class HelpSection:
    title: str
    anchor: str
    markdown: str
    searchable_text: str

    def to_result(self) -> dict[str, str]:
        plain = _plain_text(self.markdown)
        excerpt = plain[:132].strip()
        if len(plain) > 132:
            excerpt += "…"
        return {
            "title": self.title,
            "anchor": self.anchor,
            "excerpt": excerpt,
        }


class HelpDocument:
    def __init__(self, markdown: str, *, anchors: tuple[str, ...] | None = None) -> None:
        self.markdown = markdown
        self.title, self.sections = _parse(markdown)
        if anchors is not None:
            if len(anchors) != len(self.sections) or len(set(anchors)) != len(anchors):
                raise HelpContentError("Invalid localized Help section mapping.")
            self.sections = tuple(
                HelpSection(section.title, anchor, section.markdown, section.searchable_text)
                for section, anchor in zip(self.sections, anchors, strict=True)
            )
        self._by_anchor = {section.anchor: section for section in self.sections}

    @classmethod
    def from_path(cls, path: Path) -> HelpDocument:
        try:
            markdown = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            raise HelpContentError(
                "A Ajuda integrada não pôde ser carregada. "
                "Reinstale o aplicativo para restaurar o manual."
            ) from exc
        return cls(markdown)

    @property
    def first_anchor(self) -> str:
        return self.sections[0].anchor

    def section(self, anchor: str) -> HelpSection:
        return self._by_anchor.get(anchor, self.sections[0])

    def has_anchor(self, anchor: str) -> bool:
        return anchor in self._by_anchor

    def search(self, query: str) -> list[dict[str, str]]:
        terms = [_normalize(term) for term in query.split() if term.strip()]
        matches = [
            section
            for section in self.sections
            if not terms
            or all(term in section.searchable_text for term in terms)
        ]
        if terms:
            matches = matches[:24]
        return [section.to_result() for section in matches]


def slugify(value: str) -> str:
    normalized = _normalize(value)
    slug = re.sub(r"[^\w\s-]", "", normalized)
    slug = re.sub(r"[\s_]+", "-", slug).strip("-")
    return slug or "inicio"


def _parse(markdown: str) -> tuple[str, tuple[HelpSection, ...]]:
    if not markdown.strip():
        raise HelpContentError("O arquivo de Ajuda está vazio.")

    root_titles = [
        line[2:].strip()
        for line in markdown.splitlines()
        if line.startswith("# ") and not line.startswith("## ")
    ]
    if len(root_titles) != 1:
        raise HelpContentError("A Ajuda precisa ter exatamente um título principal.")

    sections: list[HelpSection] = []
    current_title: str | None = None
    current_lines: list[str] = []
    seen_anchors: set[str] = set()

    def append_current() -> None:
        if current_title is None:
            return
        body = "\n".join(current_lines).strip()
        if not body:
            return
        anchor = slugify(current_title)
        if anchor in seen_anchors:
            raise HelpContentError(
                f"Duas seções da Ajuda geram a mesma âncora: {anchor}."
            )
        seen_anchors.add(anchor)
        sections.append(
            HelpSection(
                title=current_title,
                anchor=anchor,
                markdown=body,
                searchable_text=_normalize(
                    f"{current_title} {_plain_text(body)}"
                ),
            )
        )

    for line in markdown.splitlines():
        if line.startswith("## "):
            append_current()
            current_title = line[3:].strip()
            current_lines = [line]
        elif current_title is not None:
            current_lines.append(line)
    append_current()

    if not sections:
        raise HelpContentError("A Ajuda não contém artigos navegáveis.")
    return root_titles[0], tuple(sections)


def _normalize(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value.casefold())
    return "".join(character for character in normalized if not unicodedata.combining(character))


def _plain_text(markdown: str) -> str:
    without_links = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", markdown)
    without_marks = re.sub(r"[#*`>\[\]()]", " ", without_links)
    return re.sub(r"\s+", " ", without_marks).strip()
