"""SearchService – single entry point for all document retrieval.

Responsibilities:
    - Validate search requests.
    - Invoke the configured retriever (BaseRetriever).
    - Invoke the configured reranker (BaseReranker).
    - Return reranked RetrievedChunk objects.
    - Log retrieval/reranking/total latency and chunk counts.

The service is completely independent of LLMs, prompt builders, and QA.
"""

from __future__ import annotations

import logging
import time
from typing import Optional
from uuid import UUID

from backend.app.rag.retrieval.base import (
    BaseReranker,
    BaseRetriever,
    EmptyQueryError,
    RetrievedChunk,
    SearchError,
    SearchTimeoutError,
)

logger = logging.getLogger(__name__)


class SearchService:
    """Orchestrates retrieval and reranking for a single search query.

    Typical usage::

        service = SearchService(retriever=..., reranker=...)
        chunks = await service.search(
            query="What is RAG?",
            user_id=UUID("..."),
            top_k=5,
        )
    """

    def __init__(
        self,
        retriever: BaseRetriever,
        reranker: BaseReranker,
    ) -> None:
        """Inject the retriever and reranker implementations.

        Args:
            retriever: A concrete ``BaseRetriever`` (e.g. ``HybridRetriever``).
            reranker: A concrete ``BaseReranker`` (e.g. ``BGEReranker``).
        """
        if not isinstance(retriever, BaseRetriever):
            raise TypeError("retriever must implement BaseRetriever")
        if not isinstance(reranker, BaseReranker):
            raise TypeError("reranker must implement BaseReranker")

        self._retriever = retriever
        self._reranker = reranker

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def search(
        self,
        *,
        query: str,
        user_id: UUID,
        collection_id: UUID | None = None,
        document_ids: list[UUID] | None = None,
        top_k: int = 5,
    ) -> list[RetrievedChunk]:
        """Execute a search: validate → retrieve → rerank → return.

        Args:
            query: The user's search query (must not be empty).
            user_id: The authenticated user's UUID (used for access scoping).
            collection_id: Optional collection UUID to scope the search.
            document_ids: Optional list of document UUIDs to scope the search.
            top_k: Number of final reranked chunks to return (default 5).

        Returns:
            A list of ``RetrievedChunk`` objects ordered by descending
            relevance score. May be empty when no relevant content is found.

        Raises:
            EmptyQueryError: If ``query`` is empty or whitespace-only.
            SearchError: Base class for all search failures.
            RetrieverUnavailableError: When the vector store is unreachable.
            RerankerUnavailableError: When the reranker model cannot load.
            SearchTimeoutError: When the overall operation exceeds a timeout.
        """
        # ------------------------------------------------------------------
        # 1. Validate
        # ------------------------------------------------------------------
        if not query or not query.strip():
            raise EmptyQueryError("Search query must not be empty")

        start_time = time.monotonic()

        # ------------------------------------------------------------------
        # 2. Retrieve
        # ------------------------------------------------------------------
        retrieval_start = time.monotonic()
        try:
            retrieved = await self._retriever.retrieve(
                query=query.strip(),
                user_id=user_id,
                collection_id=collection_id,
                document_ids=document_ids,
                top_k=top_k,
            )
        except SearchError:
            raise
        except Exception as exc:
            logger.error("Unexpected error during retrieval: %s", exc)
            raise SearchError(f"Retrieval failed: {exc}") from exc

        retrieval_latency = time.monotonic() - retrieval_start
        retrieved_count = len(retrieved)

        if not retrieved:
            logger.info(
                "Empty retrieval | query=%s user_id=%s collection_id=%s "
                "retrieval_latency=%.3fs",
                query,
                user_id,
                collection_id,
                retrieval_latency,
            )
            return []

        # ------------------------------------------------------------------
        # 3. Rerank
        # ------------------------------------------------------------------
        rerank_start = time.monotonic()
        try:
            reranked = await self._reranker.rerank(
                query=query.strip(),
                chunks=retrieved,
                top_k=top_k,
            )
        except SearchError:
            raise
        except Exception as exc:
            logger.error("Unexpected error during reranking: %s", exc)
            raise SearchError(f"Reranking failed: {exc}") from exc

        rerank_latency = time.monotonic() - rerank_start
        total_latency = time.monotonic() - start_time
        reranked_count = len(reranked)

        # ------------------------------------------------------------------
        # 4. Log
        # ------------------------------------------------------------------
        logger.info(
            "Search completed | query=%s user_id=%s collection_id=%s "
            "retrieval_latency=%.3fs rerank_latency=%.3fs total_latency=%.3fs "
            "retrieved=%d reranked=%d",
            query,
            user_id,
            collection_id,
            retrieval_latency,
            rerank_latency,
            total_latency,
            retrieved_count,
            reranked_count,
        )

        return reranked
