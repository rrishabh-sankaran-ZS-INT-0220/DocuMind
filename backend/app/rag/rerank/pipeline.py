from __future__ import annotations

import logging
from typing import Dict, Optional

from backend.app.config import settings
from backend.app.rag.retrieval.hybrid import HybridRetriever
from backend.app.rag.retrieval.models import RetrievalResult, RetrievedChunk
from .bge import BGEReranker

logger = logging.getLogger("documind.rerank.pipeline")


class HybridBGERerankPipeline:
    """Pipeline: Hybrid retrieval -> top N -> BGE reranker -> top M."""

    def __init__(
        self,
        collection_name: str = "documents_bge_large",
    ) -> None:
        self.collection_name = collection_name
        self._retriever = HybridRetriever(collection_name=collection_name)
        self._reranker = BGEReranker()

    async def search_with_rerank(
        self,
        query: str,
        filters: Optional[Dict] = None,
    ) -> RetrievalResult:
        input_top_k = settings.rerank_input_top_k
        output_top_k = settings.rerank_top_k

        logger.info(
            "rerank.pipeline.start",
            extra={
                "query": query,
                "collection_name": self.collection_name,
                "input_top_k": input_top_k,
                "output_top_k": output_top_k,
            },
        )

        # Step 1: Hybrid retrieval (top input_top_k)
        hybrid_result: RetrievalResult = await self._retriever.search(
            query=query,
            top_k=input_top_k,
            filters=filters,
        )

        # Step 2: Cross-encoder reranking (top output_top_k)
        reranked_chunks: list[RetrievedChunk] = await self._reranker.rerank(
            query=query,
            candidates=hybrid_result.chunks,
            top_k=output_top_k,
        )

        logger.info(
            "rerank.pipeline.completed",
            extra={
                "query": query,
                "num_initial": len(hybrid_result.chunks),
                "num_reranked": len(reranked_chunks),
            },
        )

        return RetrievalResult(query=query, chunks=reranked_chunks)