"""Abstract base classes for retrievers and rerankers, plus domain model."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID


# ---------------------------------------------------------------------------
# Domain model
# ---------------------------------------------------------------------------


@dataclass
class RetrievedChunk:
    """A single chunk returned from the retrieval pipeline.

    Attributes:
        text: The chunk text content.
        page: The source page number.
        section: The source section title, if any.
        score: The relevance score (cosine similarity or reranker score).
        document_id: The UUID of the parent document.
        document_title: Resolved document title, populated after retrieval.
        chunk_index: The index of this chunk within the document.
    """

    text: str
    page: int
    section: Optional[str]
    score: float
    document_id: str
    document_title: Optional[str] = None
    chunk_index: Optional[int] = None


# ---------------------------------------------------------------------------
# Domain exceptions
# ---------------------------------------------------------------------------


class SearchError(Exception):
    """Base exception for all search-related errors."""


class EmptyQueryError(SearchError):
    """Raised when the search query is empty or only whitespace."""


class RetrieverUnavailableError(SearchError):
    """Raised when the configured retriever cannot be reached."""


class RerankerUnavailableError(SearchError):
    """Raised when the configured reranker cannot be loaded or used."""


class SearchTimeoutError(SearchError):
    """Raised when the search operation exceeds the configured timeout."""


# ---------------------------------------------------------------------------
# Abstract retriever
# ---------------------------------------------------------------------------


class BaseRetriever(ABC):
    """Interface for document retrievers.

    Implementations should connect to a vector store, search engine,
    or hybrid backend and return semantically relevant chunks.
    """

    @abstractmethod
    async def retrieve(
        self,
        *,
        query: str,
        user_id: UUID | None = None,
        collection_id: UUID | None = None,
        document_ids: list[UUID] | None = None,
        top_k: int = 5,
    ) -> list[RetrievedChunk]:
        """Retrieve the top-k most relevant chunks for *query*.

        Args:
            query: The user's search query.
            user_id: If provided, scope results to documents owned by this user.
            collection_id: If provided, scope results to a specific collection.
            document_ids: If provided, scope results to the listed document IDs.
            top_k: Maximum number of chunks to return before reranking.

        Returns:
            A list of ``RetrievedChunk`` objects, ordered by descending relevance.

        Raises:
            RetrieverUnavailableError: When the underlying store is unreachable.
            SearchTimeoutError: When the operation exceeds the timeout.
        """
        ...


# ---------------------------------------------------------------------------
# Abstract reranker
# ---------------------------------------------------------------------------


class BaseReranker(ABC):
    """Interface for cross-encoder rerankers.

    Implementations should take an initial set of retrieved chunks and
    re-score them against the query for improved relevance ordering.
    """

    @abstractmethod
    async def rerank(
        self,
        *,
        query: str,
        chunks: list[RetrievedChunk],
        top_k: int = 5,
    ) -> list[RetrievedChunk]:
        """Re-score and re-rank the provided chunks.

        Args:
            query: The original search query.
            chunks: Chunks returned from a retriever, typically oversampled.
            top_k: Maximum number of chunks to return after reranking.

        Returns:
            A list of ``RetrievedChunk`` objects with updated ``score`` fields,
            ordered by descending relevance.

        Raises:
            RerankerUnavailableError: When the model cannot be loaded.
        """
        ...
