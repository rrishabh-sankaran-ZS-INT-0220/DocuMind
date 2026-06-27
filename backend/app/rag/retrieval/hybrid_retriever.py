"""Hybrid (vector) retriever backed by Qdrant.

Currently implements dense vector search via Qdrant's COSINE similarity.
A future sparse / BM25 leg can be added without changing the public interface.
"""

from __future__ import annotations

import logging
from typing import Optional
from uuid import UUID

from qdrant_client.http import models as qmodels

from backend.app.config import settings
from backend.app.rag.embeddings import embed_texts
from backend.app.rag.qdrant_client import get_qdrant_client
from backend.app.rag.retrieval.base import (
    BaseRetriever,
    RetrieverUnavailableError,
    RetrievedChunk,
    SearchTimeoutError,
)

logger = logging.getLogger(__name__)


class HybridRetriever(BaseRetriever):
    """Retriever that performs dense vector search against a Qdrant collection.

    The ``HybridRetriever`` name signals the intended architecture – a future
    enhancement will add a sparse (BM25) leg with reciprocal-rank fusion.
    For now, only the dense leg is active.
    """

    def __init__(
        self,
        collection_name: str | None = None,
        oversample_factor: int = 2,
    ) -> None:
        self._collection_name = collection_name or settings.qdrant_collection_name
        self._oversample_factor = oversample_factor
        self._client = get_qdrant_client()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def retrieve(
        self,
        *,
        query: str,
        user_id: UUID | None = None,
        collection_id: UUID | None = None,
        document_ids: list[UUID] | None = None,
        top_k: int = 5,
    ) -> list[RetrievedChunk]:
        """Embed the query and search Qdrant with optional payload filters."""
        query_vector = embed_texts([query])[0]

        search_filter = self._build_filter(
            user_id=user_id,
            collection_id=collection_id,
            document_ids=document_ids,
        )

        try:
            search_result = self._client.search(
                collection_name=self._collection_name,
                query_vector=query_vector,
                limit=top_k * self._oversample_factor,
                query_filter=search_filter,
                with_payload=True,
                timeout=settings.search_timeout,
            )
        except Exception as exc:
            logger.error("Qdrant search failed: %s", exc)
            raise RetrieverUnavailableError(
                f"Vector store search failed: {exc}"
            ) from exc

        chunks: list[RetrievedChunk] = []
        for point in search_result:
            payload = point.payload or {}
            chunks.append(
                RetrievedChunk(
                    text=payload.get("text", ""),
                    page=int(payload.get("page", 0)),
                    section=payload.get("section"),
                    score=float(point.score),
                    document_id=str(payload.get("document_id", "")),
                    chunk_index=payload.get("chunk_index"),
                )
            )
        return chunks

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_filter(
        self,
        user_id: UUID | None,
        collection_id: UUID | None,
        document_ids: list[UUID] | None,
    ) -> qmodels.Filter | None:
        """Build an optional Qdrant ``Filter`` from scoping parameters.

        .. note::

            The ingestion pipeline does **not** currently store ``owner_id``
            in the Qdrant payload, so ``user_id`` filtering will be a no-op
            until that field is added at upsert time.
        """
        conditions: list[qmodels.FieldCondition | qmodels.Filter] = []

        if user_id is not None:
            conditions.append(
                qmodels.FieldCondition(
                    key="owner_id",
                    match=qmodels.MatchValue(value=str(user_id)),
                )
            )

        if collection_id is not None:
            conditions.append(
                qmodels.FieldCondition(
                    key="collection_id",
                    match=qmodels.MatchValue(value=str(collection_id)),
                )
            )

        if document_ids:
            conditions.append(
                qmodels.FieldCondition(
                    key="document_id",
                    match=qmodels.MatchAny(any=[str(did) for did in document_ids]),
                )
            )

        if not conditions:
            return None

        return qmodels.Filter(must=conditions)
