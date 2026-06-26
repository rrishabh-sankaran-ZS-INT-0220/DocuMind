from __future__ import annotations

import logging
import math
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from qdrant_client.http import models as qmodels

from backend.app.config import settings
from backend.app.rag.qdrant_client import get_qdrant_client
from .base import BaseRetriever
from .models import RetrievedChunk, RetrievalResult

logger = logging.getLogger("documind.retrieval.bm25")


def default_tokenizer(text: str) -> List[str]:
    return [t for t in text.lower().split() if t]


DEFAULT_STOP_WORDS = {
    "the",
    "and",
    "of",
    "to",
    "a",
    "in",
    "is",
    "it",
    "for",
    "on",
    "that",
    "this",
}


@dataclass
class _BM25Document:
    chunk_id: str
    document_id: str
    document_name: Optional[str]
    page: Optional[int]
    section: Optional[str]
    chunk_index: int
    text: str
    tokens: List[str]


@dataclass
class _BM25Index:
    documents: List[_BM25Document]
    idf: Dict[str, float]
    avg_doc_len: float


class BM25Retriever(BaseRetriever):
    """Lexical BM25 retriever over chunk texts stored in Qdrant."""

    def __init__(
        self,
        collection_name: str = "documents_bge_large",
        tokenizer=default_tokenizer,
        stop_words: Optional[set[str]] = None,
    ) -> None:
        self.collection_name = collection_name
        self._client = get_qdrant_client()
        self._tokenizer = tokenizer
        self._stop_words = stop_words or DEFAULT_STOP_WORDS
        self._index: Optional[_BM25Index] = None

    def _ensure_index(self, filters: Optional[Dict[str, Any]] = None) -> None:
        if self._index is not None:
            return

        logger.info(
            "retrieval.bm25.build_index.start",
            extra={"collection_name": self.collection_name},
        )

        # For now, build index for the whole collection.
        documents: List[_BM25Document] = []

        # Scroll through all points in the collection.
        offset: Optional[qmodels.ScrollResult] = None
        while True:
            result = self._client.scroll(
                collection_name=self.collection_name,
                scroll_filter=None,
                limit=256,
                offset=offset.offset if offset else None,
                with_payload=True,
                with_vectors=False,
            )
            points = result[0]
            offset = result[1]
            if not points:
                break

            for point in points:
                payload = point.payload or {}
                text = payload.get("text")
                if not text:
                    continue

                document_id = str(payload.get("document_id", ""))
                chunk_index = int(payload.get("chunk_index", 0))
                page = payload.get("page")
                section = payload.get("section")
                document_name = None

                tokens = [
                    t for t in self._tokenizer(text) if t not in self._stop_words
                ]

                documents.append(
                    _BM25Document(
                        chunk_id=str(point.id),
                        document_id=document_id,
                        document_name=document_name,
                        page=page,
                        section=section,
                        chunk_index=chunk_index,
                        text=text,
                        tokens=tokens,
                    )
                )

            if offset is None or offset.offset is None:
                break

        # Compute idf and average doc length
        doc_count = len(documents)
        if doc_count == 0:
            self._index = _BM25Index(documents=documents, idf={}, avg_doc_len=0.0)
            return

        df: Dict[str, int] = {}
        for doc in documents:
            unique_tokens = set(doc.tokens)
            for token in unique_tokens:
                df[token] = df.get(token, 0) + 1

        idf: Dict[str, float] = {}
        for token, freq in df.items():
            # BM25 idf formula with smoothing
            idf[token] = math.log(1 + (doc_count - freq + 0.5) / (freq + 0.5))

        avg_len = sum(len(doc.tokens) for doc in documents) / float(doc_count)

        self._index = _BM25Index(documents=documents, idf=idf, avg_doc_len=avg_len)

        logger.info(
            "retrieval.bm25.build_index.success",
            extra={
                "collection_name": self.collection_name,
                "doc_count": doc_count,
                "avg_doc_len": avg_len,
            },
        )

    def _score_query(self, query_tokens: List[str]) -> List[Tuple[_BM25Document, float]]:
        assert self._index is not None

        k1 = 1.5
        b = 0.75

        scores: List[Tuple[_BM25Document, float]] = []

        for doc in self._index.documents:
            score = 0.0
            doc_len = len(doc.tokens) or 1
            for token in query_tokens:
                tf = doc.tokens.count(token)
                if tf == 0:
                    continue
                idf = self._index.idf.get(token)
                if idf is None:
                    continue
                numerator = tf * (k1 + 1.0)
                denominator = tf + k1 * (1.0 - b + b * (doc_len / self._index.avg_doc_len))
                score += idf * (numerator / denominator)
            if score > 0.0:
                scores.append((doc, score))

        return scores

    async def search(
        self,
        query: str,
        top_k: int = 0,
        filters: Optional[Dict[str, Any]] = None,
    ) -> RetrievalResult:
        limit = top_k or settings.bm25_top_k

        self._ensure_index(filters)

        start = time.perf_counter()

        query_tokens = [
            t for t in self._tokenizer(query) if t not in self._stop_words
        ]

        if not query_tokens or self._index is None:
            logger.info(
                "retrieval.bm25.no_query_tokens",
                extra={"query": query},
            )
            return RetrievalResult(query=query, chunks=[])

        # Apply simple filters by document_id or user_id if present.
        # For now, only document_id is defined in payload.
        doc_id_filter = None
        if filters:
            doc_id_filter = filters.get("document_id")

        scores = self._score_query(query_tokens)

        if doc_id_filter is not None:
            scores = [
                (doc, score)
                for doc, score in scores
                if doc.document_id == str(doc_id_filter)
            ]

        scores.sort(key=lambda pair: pair[1], reverse=True)
        scores = scores[:limit]

        chunks: List[RetrievedChunk] = []
        for doc, score in scores:
            chunk = RetrievedChunk(
                chunk_id=doc.chunk_id,
                document_id=doc.document_id,
                document_name=doc.document_name,
                page=doc.page,
                section=doc.section,
                chunk_index=doc.chunk_index,
                text=doc.text,
                retrieval_score=score,
                retrieval_method="bm25",
            )
            chunks.append(chunk)

        elapsed_ms = (time.perf_counter() - start) * 1000.0

        logger.info(
            "retrieval.bm25.completed",
            extra={
                "query": query,
                "collection_name": self.collection_name,
                "top_k": limit,
                "latency_ms": elapsed_ms,
                "num_results": len(chunks),
            },
        )

        return RetrievalResult(query=query, chunks=chunks)