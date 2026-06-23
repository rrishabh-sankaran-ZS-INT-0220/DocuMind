from __future__ import annotations

from dataclasses import dataclass

from backend.app.rag.parsers.base import ParsedDocument, ParsedPage


@dataclass
class Chunk:
    text: str
    page: int
    section: str | None
    chunk_index: int


def _tokenize(text: str) -> list[str]:
    # Simple whitespace tokenizer for V1; can be replaced later.
    return text.split()


def _detokenize(tokens: list[str]) -> str:
    return " ".join(tokens)


def chunk_document(parsed: ParsedDocument, max_tokens: int = 512, overlap: int = 64) -> list[Chunk]:
    """Chunk a ParsedDocument into overlapping token windows.

    - Respects page boundaries: chunks do not cross pages.
    - Preserves section/page metadata.
    - Avoids tiny trailing fragments by merging when reasonable.
    """

    chunks: list[Chunk] = []
    chunk_idx = 0

    for page in parsed.pages:
        tokens = _tokenize(page.text)
        if not tokens:
            continue

        start = 0
        while start < len(tokens):
            end = min(start + max_tokens, len(tokens))
            window = tokens[start:end]

            remaining = len(tokens) - end
            # If we would leave a tiny tail smaller than overlap, merge into previous chunk.
            if remaining > 0 and remaining < overlap and end == len(tokens):
                if chunks and chunks[-1].page == page.page_number:
                    prev_tokens = _tokenize(chunks[-1].text)
                    merged_tokens = prev_tokens + window
                    chunks[-1].text = _detokenize(merged_tokens)
                    break

            text = _detokenize(window)
            chunks.append(
                Chunk(
                    text=text,
                    page=page.page_number,
                    section=page.section_title,
                    chunk_index=chunk_idx,
                )
            )
            chunk_idx += 1

            if end == len(tokens):
                break

            start = max(0, end - overlap)

    return chunks
