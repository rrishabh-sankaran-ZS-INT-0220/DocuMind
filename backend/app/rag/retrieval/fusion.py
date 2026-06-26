from __future__ import annotations

import logging
import time
from typing import Dict, Iterable, List

from .models import RetrievedChunk

logger = logging.getLogger("documind.retrieval.fusion")


def reciprocal_rank_fusion(
    vector_results: Iterable[RetrievedChunk],
    bm25_results: Iterable[RetrievedChunk],
    k: float,
    top_k: int,
) -> List[RetrievedChunk]:
    """Combine vector and BM25 rankings using Reciprocal Rank Fusion.

    RRF score for a chunk = sum over systems of 1 / (k + rank_i),
    where rank_i is zero-based rank in that system.
    """
    start = time.perf_counter()

    # Rank maps
    vector_rank: Dict[str, int] = {}
    bm25_rank: Dict[str, int] = {}

    vector_list = list(vector_results)
    bm25_list = list(bm25_results)

    for idx, chunk in enumerate(vector_list):
        if chunk.chunk_id not in vector_rank:
            vector_rank[chunk.chunk_id] = idx

    for idx, chunk in enumerate(bm25_list):
        if chunk.chunk_id not in bm25_rank:
            bm25_rank[chunk.chunk_id] = idx

    # Representative chunk per id (prefer vector, then bm25)
    by_id: Dict[str, RetrievedChunk] = {}
    for chunk in bm25_list:
        by_id.setdefault(chunk.chunk_id, chunk)
    for chunk in vector_list:
        by_id[chunk.chunk_id] = chunk

    fused_scores: Dict[str, float] = {}
    for chunk_id in by_id.keys():
        score = 0.0
        if chunk_id in vector_rank:
            score += 1.0 / (k + vector_rank[chunk_id])
        if chunk_id in bm25_rank:
            score += 1.0 / (k + bm25_rank[chunk_id])
        fused_scores[chunk_id] = score

    fused_chunks: List[RetrievedChunk] = []
    for chunk_id, score in fused_scores.items():
        base = by_id[chunk_id]
        fused_chunks.append(
            RetrievedChunk(
                chunk_id=base.chunk_id,
                document_id=base.document_id,
                document_name=base.document_name,
                page=base.page,
                section=base.section,
                chunk_index=base.chunk_index,
                text=base.text,
                retrieval_score=score,
                retrieval_method="hybrid",
            )
        )

    fused_chunks.sort(key=lambda c: c.retrieval_score, reverse=True)
    fused_chunks = fused_chunks[:top_k]

    elapsed_ms = (time.perf_counter() - start) * 1000.0

    logger.info(
        "retrieval.fusion.completed",
        extra={
            "k": k,
            "top_k": top_k,
            "latency_ms": elapsed_ms,
            "num_results": len(fused_chunks),
        },
    )

    return fused_chunks