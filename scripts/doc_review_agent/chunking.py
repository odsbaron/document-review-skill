from __future__ import annotations

import re
from dataclasses import dataclass


_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$")


@dataclass(frozen=True)
class Chunk:
    text: str
    section: str = ""


@dataclass(frozen=True)
class _SectionedUnit:
    text: str
    section: str


def chunk_text(text: str, max_chars: int = 8000, overlap_chars: int = 500) -> list[str]:
    """Backward-compatible wrapper returning plain text chunks."""
    return [chunk.text for chunk in chunk_document(text, max_chars=max_chars, overlap_chars=overlap_chars)]


def chunk_document(text: str, max_chars: int = 8000, overlap_chars: int = 500) -> list[Chunk]:
    """Split text into chunks, tracking the Markdown heading path of each chunk.

    The section label is the heading path (e.g. ``"Title > Options"``) that is
    active at the first unit of the chunk, so findings can be located in the
    original document instead of only by chunk index.
    """
    if max_chars < 50:
        raise ValueError("max_chars must be at least 50")
    if overlap_chars < 0:
        raise ValueError("overlap_chars must be non-negative")

    normalized = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not normalized:
        return []

    units = _split_into_units(normalized, max_chars)
    if len(normalized) <= max_chars:
        return [Chunk(text=normalized, section=units[0].section if units else "")]

    chunks: list[Chunk] = []
    current = ""
    current_section = ""

    for unit in units:
        candidate = _join_blocks(current, unit.text)
        if current and len(candidate) > max_chars:
            chunks.append(Chunk(text=current, section=current_section))
            overlap = _tail_overlap(current, overlap_chars)
            current = _join_blocks(overlap, unit.text)
            current_section = unit.section
            if len(current) > max_chars:
                current = unit.text
        else:
            if not current:
                current_section = unit.section
            current = candidate

    if current:
        chunks.append(Chunk(text=current, section=current_section))

    return chunks


def _split_into_units(text: str, max_chars: int) -> list[_SectionedUnit]:
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    heading_stack: list[tuple[int, str]] = []
    units: list[_SectionedUnit] = []

    for paragraph in paragraphs:
        match = _HEADING_RE.match(paragraph.splitlines()[0])
        if match:
            level = len(match.group(1))
            title = match.group(2).strip()
            while heading_stack and heading_stack[-1][0] >= level:
                heading_stack.pop()
            heading_stack.append((level, title))
        section = " > ".join(title for _, title in heading_stack)

        if len(paragraph) <= max_chars:
            units.append(_SectionedUnit(paragraph, section))
            continue
        for piece in _split_long_block(paragraph, max_chars):
            units.append(_SectionedUnit(piece, section))

    return units


def _split_long_block(text: str, max_chars: int) -> list[str]:
    pieces: list[str] = []
    start = 0
    while start < len(text):
        pieces.append(text[start : start + max_chars].strip())
        start += max_chars
    return [piece for piece in pieces if piece]


def _join_blocks(left: str, right: str) -> str:
    if not left:
        return right
    if not right:
        return left
    return f"{left}\n\n{right}"


def _tail_overlap(text: str, overlap_chars: int) -> str:
    if overlap_chars == 0:
        return ""
    if len(text) <= overlap_chars:
        return text
    return text[-overlap_chars:].lstrip()
