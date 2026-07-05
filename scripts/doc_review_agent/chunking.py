from __future__ import annotations

import re


def chunk_text(text: str, max_chars: int = 8000, overlap_chars: int = 500) -> list[str]:
    if max_chars < 50:
        raise ValueError("max_chars must be at least 50")
    if overlap_chars < 0:
        raise ValueError("overlap_chars must be non-negative")

    normalized = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not normalized:
        return []
    if len(normalized) <= max_chars:
        return [normalized]

    units = _split_into_units(normalized, max_chars)
    chunks: list[str] = []
    current = ""

    for unit in units:
        candidate = _join_blocks(current, unit)
        if current and len(candidate) > max_chars:
            chunks.append(current)
            overlap = _tail_overlap(current, overlap_chars)
            current = _join_blocks(overlap, unit)
            if len(current) > max_chars:
                current = unit
        else:
            current = candidate

    if current:
        chunks.append(current)

    return chunks


def _split_into_units(text: str, max_chars: int) -> list[str]:
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    units: list[str] = []
    for paragraph in paragraphs:
        if len(paragraph) <= max_chars:
            units.append(paragraph)
            continue
        units.extend(_split_long_block(paragraph, max_chars))
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
