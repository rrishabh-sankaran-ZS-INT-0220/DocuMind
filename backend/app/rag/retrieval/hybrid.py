from __future__ import annotations

import logging
import time
from typing import Dict, Optional

from backend.app.config import settings
from .base import BaseRetriever
from .models import RetrievalResult
from .vector import VectorRetriever
from .bm25 import BM25Retriever
from .fusion import reciprocal_rank_fusion

logger = logging.getLogger("documind.retrieval.hybrid")


class HybridRetriever(BaseRetriever):
    """Hybrid retriever combining vector and BM25 via Reciprocal Rank Fusion."""

    def __init__(
        self,
        collection_name: str = "documents_bge_large",
    ) -> None:
        self.collection_name = collection_name
        self.vector_retriever = VectorRetriever(collection_name=collection_name)
        self.bm25_retriever = BM25Retriever(collection_name=collection_name)

    async def search(
        self,
        query: str,
        top_k: int = 0,
        filters: Optional[Dict] = None,
    ) -> RetrievalResult:
        vector_top_k = settings.vector_top_k
        bm25_top_k = settings.bm25_top_k
        hybrid_top_k = top_k or settings.hybrid_top_k
        rrf_k = settings.rrf_k

        start_vector = time.perf_counter()
        vector_result = await self.vector_retriever.search(
            query=query,
            top_k=vector_top_k,
            filters=filters,
        )
        end_vector = time.perf_counter()

        bm25_result = await self.bm25_retriever.search(
            query=query,
            top_k=bm25_top_k,
            filters=filters,
        )
        end_bm25 = time.perf_counter()

        fused_chunks = reciprocal_rank_fusion(
            vector_results=vector_result.chunks,
            bm25_results=bm25_result.chunks,
            k=rrf_k,
            top_k=hybrid_top_k,
        )
        end_fusion = time.perf_counter()

        logger.info(
            "retrieval.hybrid.completed",
            extra={
                "query": query,
                "collection_name": self.collection_name,
                "vector_ms": (end_vector - start_vector) * 1000.0,
                "bm25_ms": (end_bm25 - end_vector) * 1000.0,
                "fusion_ms": (end_fusion - end_bm25) * 1000.0,
                "num_vector": len(vector_result.chunks),
                "num_bm25": len(bm25_result.chunks),
                "num_final": len(fused_chunks),
            },
        )

        return RetrievalResult(query=query, chunks=fused_chunks)