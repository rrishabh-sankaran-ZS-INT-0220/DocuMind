import pytest

from backend.app.rag.retrieval.models import RetrievedChunk
from backend.app.rag.rerank.bge import BGEReranker


@pytest.mark.asyncio
async def test_bge_reranker_preserves_metadata(monkeypatch):
    # Prepare fake candidates
    candidates = [
        RetrievedChunk(
            chunk_id="doc1-0",
            document_id="doc1",
            document_name=None,
            page=1,
            section="Intro",
            chunk_index=0,
            text="This is about Python.",
            retrieval_score=0.0,
            retrieval_method="hybrid",
        ),
        RetrievedChunk(
            chunk_id="doc2-0",
            document_id="doc2",
            document_name=None,
            page=2,
            section="Body",
            chunk_index=0,
            text="This is about Java.",
            retrieval_score=0.0,
            retrieval_method="hybrid",
        ),
    ]

    # Monkeypatch CrossEncoder.predict to return deterministic scores
    from backend.app.rerank.bge import _get_cross_encoder

    class DummyModel:
        def predict(self, pairs):
            return [0.9, 0.1]

    monkeypatch.setattr(
        "backend.app.rag.rerank.bge._get_cross_encoder",
        lambda: DummyModel(),
    )

    reranker = BGEReranker()
    reranked = await reranker.rerank("python", candidates, top_k=1)

    assert len(reranked) == 1
    best = reranked[0]
    assert best.chunk_id == "doc1-0"
    assert best.retrieval_method == "cross_encoder"
    assert best.document_id == "doc1"
    assert best.page == 1
    assert best.section == "Intro"