from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass
class ParsedPage:
    page_number: int
    text: str
    section_title: str | None = None


@dataclass
class ParsedDocument:
    pages: list[ParsedPage]


class BaseParser(Protocol):
    """Base parser interface for documents.

    Concrete parsers should implement parse and return a ParsedDocument.
    """

    async def parse(self, path: Path) -> ParsedDocument:  # pragma: no cover - interface
        ...
