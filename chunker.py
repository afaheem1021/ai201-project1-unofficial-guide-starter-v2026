"""Stage 2: keep short campus posts intact, with a boundary-aware long-post path.

The current campus_life documents all fit within the 600-character soft budget.
Longer posts are split at paragraphs, then sentence punctuation when needed.
An oversized sentence remains intact even if it exceeds the budget. Body text
is never overlapped; a long post's title is repeated only to preserve context.
The original fixed-window implementation remains available as fallback_split.
"""

from dataclasses import dataclass
import re

import config
from ingest import Document


@dataclass
class Chunk:
    """One piece of one document."""

    text: str
    source: str        # which file it came from
    index: int         # which chunk within that file, starting at 0
    produced_by: str   # the function that made it — cite this in your README

    @property
    def label(self) -> str:
        return f"{self.source}#{self.index}"


def fallback_split(
    documents: list[Document],
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    """
    The starter's original chunker. Fixed-size character windows with overlap.

    Keep this function. Milestone 3's stop rule points back at it, and having
    something to compare your own strategy against is useful in unit 2.
    """
    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP

    if overlap >= chunk_size:
        raise ValueError("overlap has to be smaller than chunk_size")

    chunks: list[Chunk] = []
    for doc in documents:
        start = 0
        index = 0
        while start < len(doc.text):
            piece = doc.text[start : start + chunk_size].strip()
            if piece:
                chunks.append(
                    Chunk(
                        text=piece,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::fallback_split",
                    )
                )
                index += 1
            start += chunk_size - overlap

    return chunks


def split_documents(documents: list[Document]) -> list[Chunk]:
    """
    Keep complete short posts, splitting longer ones without body overlap.

    A single first line followed by a blank line is treated as a title unless
    it ends in sentence punctuation. This matches the campus_life post format.
    The title counts toward the soft budget and accompanies each body chunk.
    Sentence detection uses punctuation followed by whitespace; it is a small
    plain-text heuristic, not a general-purpose language parser.
    """
    chunk_size = config.CHUNK_SIZE
    if not isinstance(chunk_size, int) or isinstance(chunk_size, bool) or chunk_size <= 0:
        raise ValueError("CHUNK_SIZE must be a positive integer")

    chunks: list[Chunk] = []
    for doc in documents:
        text = doc.text.strip()
        if not text:
            continue

        if len(text) <= chunk_size:
            pieces = [text]
        else:
            first, separator, rest = text.partition("\n\n")
            has_title = separator and "\n" not in first and first[-1] not in ".!?"
            title = first + "\n\n" if has_title else ""
            body = rest if has_title else text
            body_budget = max(1, chunk_size - len(title))
            pieces = [title + piece for piece in _split_body(body, body_budget)]

        for index, piece in enumerate(pieces):
            chunks.append(Chunk(piece, doc.source, index, "chunker.py::split_documents"))

    return chunks


def _split_body(body: str, budget: int) -> list[str]:
    """Pack paragraphs or whole sentences, allowing a long sentence to overflow."""
    pieces: list[str] = []
    current = ""
    for paragraph in re.split(r"\n[ \t]*\n", body):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        units = [paragraph]
        if len(paragraph) > budget:
            units = re.split(r"(?<=[.!?])\s+", paragraph)
        for index, unit in enumerate(units):
            separator = "\n\n" if index == 0 else " "
            candidate = current + separator + unit if current else unit
            if current and len(candidate) > budget:
                pieces.append(current)
                current = unit
            else:
                current = candidate
    if current:
        pieces.append(current)
    return pieces


def describe(chunks: list[Chunk]) -> str:
    """A one-line summary, printed after indexing."""
    if not chunks:
        return "0 chunks"
    lengths = [len(c.text) for c in chunks]
    return (
        f"{len(chunks)} chunks, "
        f"{sum(lengths) // len(lengths)} characters on average "
        f"(shortest {min(lengths)}, longest {max(lengths)}), "
        f"produced by {chunks[0].produced_by}"
    )


if __name__ == "__main__":
    from ingest import load_documents

    chunks = split_documents(load_documents())
    print(describe(chunks))
