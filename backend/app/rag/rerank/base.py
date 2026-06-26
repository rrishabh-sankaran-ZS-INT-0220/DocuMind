from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from backend.app.rag.retrieval.models import RetrievedChunk


class BaseReranker(ABC):
    """Abstract base class for reranking strategies."""

    @abstractmethod
    async def rerank(
        self,
        query: str,
        candidates: List[RetrievedChunk],
        top_k: int,
    ) -> List[RetrievedChunk]:
        """Rerank candidates and return top_k chunks."""
        raise NotImplementedError