import pytest

from backend.app.rag.retrieval.models import RetrievedChunk, RetrievalResult
from backend.app.rag.rerank.pipeline import HybridBGERerankPipeline


@pytest.mark.asyncio
async def test_rerank_pipeline_calls_retriever_and_reranker(monkeypatch):
    pipeline = HybridBGERerankPipeline(collection_name="documents_bge_large")

    # Fake hybrid search
    async def fake_search(self, query, top_k, filters=None):
        chunks = [
            RetrievedChunk(
                chunk_id="doc1-0",
                document_id="doc1",
                document_name=None,
                page=1,
                section="Intro",
                chunk_index=0,
                text="foo",
                retrieval_score=0.0,
                retrieval_method="hybrid",
            )
        ]
        return RetrievalResult(query=query, chunks=chunks)

    monkeypatch.setattr(
        "backend.app.rag.retrieval.hybrid.HybridRetriever.search",
        fake_search,
    )

    # Fake reranker
    async def fake_rerank(self, query, candidates, top_k):
        return candidates

    monkeypatch.setattr(
        "backend.app.rag.rerank.bge.BGEReranker.rerank",
        fake_rerank,
    )

    result = await pipeline.search_with_rerank("query", filters=None)
    assert len(result.chunks) == 1
    assert result.chunks[0].chunk_id == "doc1-0"