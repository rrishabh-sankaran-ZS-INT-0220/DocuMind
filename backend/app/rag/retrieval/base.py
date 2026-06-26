from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Optional

from .models import RetrievalResult


class BaseRetriever(ABC):
    """Abstract base class for retrieval strategies."""

    @abstractmethod
    async def search(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict] = None,
    ) -> RetrievalResult:
        """Search for the most relevant chunks."""
        raise NotImplementedError