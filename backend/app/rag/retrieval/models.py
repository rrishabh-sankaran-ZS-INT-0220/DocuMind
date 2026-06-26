from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel


class RetrievedChunk(BaseModel):
    """Single retrieved chunk of text with associated metadata."""

    chunk_id: str
    document_id: str
    document_name: Optional[str] = None
    page: Optional[int] = None
    section: Optional[str] = None
    chunk_index: int
    text: str
    retrieval_score: float
    retrieval_method: str  # e.g. "vector", "bm25", "hybrid"


class RetrievalResult(BaseModel):
    """Container for retrieval results for a given query."""

    query: str
    chunks: List[RetrievedChunk]