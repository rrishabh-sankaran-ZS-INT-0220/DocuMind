"""Cross-encoder reranker using BAAI/bge-reranker-large."""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import Optional

from sentence_transformers import CrossEncoder

from backend.app.config import settings
from backend.app.rag.retrieval.base import (
    BaseReranker,
    RerankerUnavailableError,
    RetrievedChunk,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Module-level model cache (shared across service restarts via LRU)
# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def _load_reranker_model(model_name: str) -> CrossEncoder:
    """Load (or return cached) CrossEncoder instance."""
    logger.info("Loading reranker model: %s", model_name)
    return CrossEncoder(model_name)


# ---------------------------------------------------------------------------
# Default reranker
# ---------------------------------------------------------------------------


class BGEReranker(BaseReranker):
    """Reranker powered by ``BAAI/bge-reranker-large``.

    Uses a cross-encoder to re-score every retrieved chunk against the
    original query, producing a more accurate relevance ordering than
    pure bi-encoder cosine similarity.
    """

    def __init__(self, model_name: str | None = None) -> None:
        self._model_name = model_name or settings.reranker_model_name

    async def rerank(
        self,
        *,
        query: str,
        chunks: list[RetrievedChunk],
        top_k: int = 5,
    ) -> list[RetrievedChunk]:
        if not chunks:
            return []

        try:
            model = _load_reranker_model(self._model_name)
        except Exception as exc:
            logger.error("Failed to load reranker model '%s': %s", self._model_name, exc)
            raise RerankerUnavailableError(
                f"Reranker model '{self._model_name}' could not be loaded: {exc}"
            ) from exc

        try:
            pairs = [(query, c.text) for c in chunks]
            scores = model.predict(pairs)
            scores = [float(s) for s in scores]
        except Exception as exc:
            logger.error("Reranker prediction failed: %s", exc)
            raise RerankerUnavailableError(
                f"Reranker prediction failed: {exc}"
            ) from exc

        for chunk, score in zip(chunks, scores):
            chunk.score = score

        chunks.sort(key=lambda c: c.score, reverse=True)
        return chunks[:top_k]
