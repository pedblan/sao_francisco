"""Safe text chunking and validation for the optional editorial stage."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

from .models import Transcript

EDITORIAL_CONTRACT_VERSION = "1"
DEFAULT_EDITORIAL_BLOCK_CHARS = 12_000
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?…])\s+")


class EditorialValidationError(ValueError):
    """An editorial response cannot safely be assembled."""


@dataclass(frozen=True, slots=True)
class EditorialBlock:
    index: int
    block_id: str
    text: str

    def to_dict(self) -> dict[str, Any]:
        return {"index": self.index, "block_id": self.block_id, "text": self.text}

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> EditorialBlock:
        return cls(
            index=int(value["index"]),
            block_id=str(value["block_id"]),
            text=str(value["text"]),
        )


def transcript_to_editorial_text(transcript: Transcript) -> str:
    """Render every segment once, preserving speaker labels as plain text."""

    paragraphs: list[str] = []
    current_speaker: str | None = None
    current_parts: list[str] = []

    def flush() -> None:
        if not current_parts:
            return
        body = " ".join(current_parts).strip()
        paragraphs.append(f"{current_speaker}: {body}" if current_speaker else body)

    for segment in transcript.segments:
        speaker = segment.speaker
        if current_parts and speaker != current_speaker:
            flush()
            current_parts = []
        current_speaker = speaker
        current_parts.append(segment.text.strip())
    flush()
    return "\n\n".join(item for item in paragraphs if item).strip()


def plan_editorial_blocks(
    text: str,
    *,
    max_chars: int = DEFAULT_EDITORIAL_BLOCK_CHARS,
    contract_version: str = EDITORIAL_CONTRACT_VERSION,
) -> tuple[EditorialBlock, ...]:
    if max_chars < 500:
        raise ValueError("max_chars is too small for safe editorial blocks")
    normalized = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not normalized:
        return ()

    units: list[str] = []
    for paragraph in re.split(r"\n{2,}", normalized):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        units.extend(_split_oversized_unit(paragraph, max_chars))

    groups: list[str] = []
    current: list[str] = []
    current_size = 0
    for unit in units:
        separator = 2 if current else 0
        if current and current_size + separator + len(unit) > max_chars:
            groups.append("\n\n".join(current))
            current = []
            current_size = 0
            separator = 0
        current.append(unit)
        current_size += separator + len(unit)
    if current:
        groups.append("\n\n".join(current))

    blocks = []
    for index, block_text in enumerate(groups):
        digest = hashlib.sha256(
            f"{contract_version}\0{index}\0{block_text}".encode()
        ).hexdigest()[:20]
        blocks.append(EditorialBlock(index=index, block_id=digest, text=block_text))
    return tuple(blocks)


def validate_editorial_result(
    original: str,
    improved: str,
    *,
    protected_speakers: Iterable[str] = (),
) -> str:
    """Validate only that a provider returned usable text.

    The original transcript is the canonical result and remains available next
    to the optional improved version.  Runtime comparisons of numbers,
    speakers, markers, or relative length produced false rejections while
    claiming a degree of semantic certainty the application cannot provide.

    ``original`` and ``protected_speakers`` remain in the signature so saved
    jobs and integrations written against the first editorial contract keep
    working.
    """

    del original, protected_speakers
    candidate = improved.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not candidate:
        raise EditorialValidationError("A melhoria devolveu um bloco vazio.")
    return candidate


def assemble_editorial_results(
    blocks: Iterable[EditorialBlock],
    results: Mapping[str, str],
) -> str:
    ordered = tuple(sorted(blocks, key=lambda item: item.index))
    if [item.index for item in ordered] != list(range(len(ordered))):
        raise EditorialValidationError("O plano editorial está fora de ordem.")
    expected = [item.block_id for item in ordered]
    if len(set(expected)) != len(expected) or set(results) != set(expected):
        raise EditorialValidationError("A melhoria está incompleta ou duplicada.")
    values = [str(results[item.block_id]).strip() for item in ordered]
    if any(not value for value in values):
        raise EditorialValidationError("A melhoria contém um bloco vazio.")
    return "\n\n".join(values).strip()


def _split_oversized_unit(value: str, max_chars: int) -> list[str]:
    if len(value) <= max_chars:
        return [value]
    sentences = [item.strip() for item in _SENTENCE_SPLIT_RE.split(value) if item.strip()]
    if len(sentences) <= 1:
        return _split_words(value, max_chars)
    result: list[str] = []
    current: list[str] = []
    size = 0
    for sentence in sentences:
        if len(sentence) > max_chars:
            if current:
                result.append(" ".join(current))
                current = []
                size = 0
            result.extend(_split_words(sentence, max_chars))
            continue
        separator = 1 if current else 0
        if current and size + separator + len(sentence) > max_chars:
            result.append(" ".join(current))
            current = []
            size = 0
            separator = 0
        current.append(sentence)
        size += separator + len(sentence)
    if current:
        result.append(" ".join(current))
    return result


def _split_words(value: str, max_chars: int) -> list[str]:
    result: list[str] = []
    current: list[str] = []
    size = 0
    for word in value.split():
        if len(word) > max_chars:
            if current:
                result.append(" ".join(current))
                current = []
                size = 0
            result.extend(
                word[index : index + max_chars]
                for index in range(0, len(word), max_chars)
            )
            continue
        separator = 1 if current else 0
        if current and size + separator + len(word) > max_chars:
            result.append(" ".join(current))
            current = []
            size = 0
            separator = 0
        current.append(word)
        size += separator + len(word)
    if current:
        result.append(" ".join(current))
    return result


__all__ = [
    "DEFAULT_EDITORIAL_BLOCK_CHARS",
    "EDITORIAL_CONTRACT_VERSION",
    "EditorialBlock",
    "EditorialValidationError",
    "assemble_editorial_results",
    "plan_editorial_blocks",
    "transcript_to_editorial_text",
    "validate_editorial_result",
]
