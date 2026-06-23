from __future__ import annotations

from pathlib import Path

from backend.app.rag.parsers.base import ParsedDocument, ParsedPage


class TXTParser:
    async def parse(self, path: Path) -> ParsedDocument:
        text = path.read_text(encoding="utf-8")
        page = ParsedPage(page_number=1, text=text, section_title=None)
        return ParsedDocument(pages=[page])
