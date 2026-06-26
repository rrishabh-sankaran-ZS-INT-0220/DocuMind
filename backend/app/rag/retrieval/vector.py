from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional

from qdrant_client.http import models as qmodels

from backend.app.config import settings
from backend.app.rag.embeddings import get_embedding_model
from backend.app.rag.qdrant_client import get_qdrant_client
from .base import BaseRetriever
from .models import RetrievedChunk, RetrievalResult

logger = logging.getLogger("documind.retrieval.vector")


def _build_qdrant_filter(filters: Optional[Dict[str, Any]]) -> Optional[qmodels.Filter]:
    """Build a Qdrant filter from a simple dict.

    Supported keys:
    - "document_id"
    - "user_id"
    """
    if not filters:
        return None

    must: List[qmodels.Condition] = []

    document_id = filters.get("document_id")
    if document_id is not None:
        must.append(
            qmodels.FieldCondition(
                key="document_id",
                match=qmodels.MatchValue(value=str(document_id)),
            )
        )

    user_id = filters.get("user_id")
    if user_id is not None:
        must.append(
            qmodels.FieldCondition(
                key="user_id",
                match=qmodels.MatchValue(value=str(user_id)),
            )
        )

    if not must:
        return None

    return qmodels.Filter(must=must)


class VectorRetriever(BaseRetriever):
    """Semantic retriever using Qdrant and sentence-transformer embeddings."""

    def __init__(self, collection_name: str = "documents_bge_large") -> None:
        self.collection_name = collection_name
        self._model = get_embedding_model()
        self._client = get_qdrant_client()

    async def search(
        self,
        query: str,
        top_k: int = 0,
        filters: Optional[Dict] = None,
    ) -> RetrievalResult:
        limit = top_k or settings.vector_top_k

        q_filter = _build_qdrant_filter(filters)

        start = time.perf_counter()
        # Encode query into a single vector
        query_vector = self._model.encode(
            [query],
            batch_size=1,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )[0].tolist()

        hits = self._client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit,
            query_filter=q_filter,
        )
        elapsed_ms = (time.perf_counter() - start) * 1000.0

        chunks: List[RetrievedChunk] = []
        for hit in hits:
            payload = hit.payload or {}
            document_id = str(payload.get("document_id", ""))
            chunk_index = int(payload.get("chunk_index", 0))
            page = payload.get("page")
            section = payload.get("section")
            text = payload.get("text", "")

            chunk = RetrievedChunk(
                chunk_id=str(hit.id),
                document_id=document_id,
                document_name=None,
                page=page,
                section=section,
                chunk_index=chunk_index,
                text=text,
                retrieval_score=float(hit.score) if hit.score is not None else 0.0,
                retrieval_method="vector",
            )
            chunks.append(chunk)

        logger.info(
            "retrieval.vector.completed",
            extra={
                "query": query,
                "collection_name": self.collection_name,
                "top_k": limit,
                "latency_ms": elapsed_ms,
                "num_results": len(chunks),
            },
        )

        return RetrievalResult(query=query, chunks=chunks)