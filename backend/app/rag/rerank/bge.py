from __future__ import annotations

import logging
from typing import List, Tuple

from sentence_transformers import CrossEncoder

from backend.app.config import settings
from backend.app.rag.retrieval.models import RetrievedChunk
from .base import BaseReranker

logger = logging.getLogger("documind.rerank.bge")

_cross_encoder: CrossEncoder | None = None


def _get_cross_encoder() -> CrossEncoder:
    global _cross_encoder
    if _cross_encoder is None:
        logger.info(
            "rerank.bge.load_model",
            extra={
                "model_name": settings.rerank_model_name,
                "device": settings.rerank_device,
            },
        )
        _cross_encoder = CrossEncoder(
            settings.rerank_model_name,
            device=settings.rerank_device,
        )
    return _cross_encoder


class BGEReranker(BaseReranker):
    """Cross-encoder reranker using BAAI/bge-reranker-large."""

    async def rerank(
        self,
        query: str,
        candidates: List[RetrievedChunk],
        top_k: int,
    ) -> List[RetrievedChunk]:
        if not candidates:
            return []

        model = _get_cross_encoder()

        pairs: List[Tuple[str, str]] = [(query, c.text) for c in candidates]

        logger.info(
            "rerank.bge.start",
            extra={
                "num_candidates": len(candidates),
                "top_k": top_k,
            },
        )

        scores = model.predict(pairs)

        reranked: List[RetrievedChunk] = []
        for c, score in zip(candidates, scores):
            reranked.append(
                RetrievedChunk(
                    chunk_id=c.chunk_id,
                    document_id=c.document_id,
                    document_name=c.document_name,
                    page=c.page,
                    section=c.section,
                    chunk_index=c.chunk_index,
                    text=c.text,
                    retrieval_score=float(score),
                    retrieval_method="cross_encoder",
                )
            )

        reranked.sort(key=lambda c: c.retrieval_score, reverse=True)
        reranked = reranked[:top_k]

        logger.info(
            "rerank.bge.completed",
            extra={
                "num_final": len(reranked),
            },
        )

        return reranked