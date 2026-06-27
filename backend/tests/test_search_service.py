"""Unit tests for SearchService using mocked retriever and reranker."""

from __future__ import annotations

import logging
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest

from backend.app.rag.retrieval.base import (
    BaseReranker,
    BaseRetriever,
    EmptyQueryError,
    RetrieverUnavailableError,
    RerankerUnavailableError,
    RetrievedChunk,
    SearchError,
)
from backend.app.services.search_service import SearchService


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_retriever() -> MagicMock:
    retriever = MagicMock(spec=BaseRetriever)
    retriever.retrieve = AsyncMock()
    return retriever


@pytest.fixture
def mock_reranker() -> MagicMock:
    reranker = MagicMock(spec=BaseReranker)
    reranker.rerank = AsyncMock()
    return reranker


@pytest.fixture
def user_id() -> UUID:
    return uuid4()


@pytest.fixture
def sample_chunks() -> list[RetrievedChunk]:
    return [
        RetrievedChunk(
            text="Chunk one content about RAG.",
            page=1,
            section="Introduction",
            score=0.85,
            document_id=str(uuid4()),
            chunk_index=0,
        ),
        RetrievedChunk(
            text="Chunk two content about embeddings.",
            page=2,
            section="Methods",
            score=0.72,
            document_id=str(uuid4()),
            chunk_index=1,
        ),
        RetrievedChunk(
            text="Chunk three content about retrieval.",
            page=3,
            section="Results",
            score=0.64,
            document_id=str(uuid4()),
            chunk_index=2,
        ),
    ]


# ---------------------------------------------------------------------------
# Constructor
# ---------------------------------------------------------------------------


def test_constructor_accepts_valid_implementations(
    mock_retriever: MagicMock,
    mock_reranker: MagicMock,
) -> None:
    service = SearchService(retriever=mock_retriever, reranker=mock_reranker)
    assert service is not None



def test_constructor_rejects_non_retriever(mock_reranker: MagicMock) -> None:
    with pytest.raises(TypeError, match="retriever must implement BaseRetriever"):
        SearchService(retriever="not-a-retriever", reranker=mock_reranker)


def test_constructor_rejects_non_reranker(mock_retriever: MagicMock) -> None:
    with pytest.raises(TypeError, match="reranker must implement BaseReranker"):
        SearchService(retriever=mock_retriever, reranker="not-a-reranker")


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_search_returns_reranked_chunks(
    mock_retriever: MagicMock,
    mock_reranker: MagicMock,
    user_id: UUID,
    sample_chunks: list[RetrievedChunk],
) -> None:
    reranked = sorted(sample_chunks, key=lambda c: c.score, reverse=True)
    mock_retriever.retrieve.return_value = sample_chunks
    mock_reranker.rerank.return_value = reranked

    service = SearchService(retriever=mock_retriever, reranker=mock_reranker)
    result = await service.search(query="What is RAG?", user_id=user_id, top_k=5)

    assert len(result) == 3
    assert result[0].score >= result[1].score >= result[2].score
    assert result[0].text == "Chunk one content about RAG."

    mock_retriever.retrieve.assert_awaited_once_with(
        query="What is RAG?",
        user_id=user_id,
        collection_id=None,
        document_ids=None,
        top_k=5,
    )
    mock_reranker.rerank.assert_awaited_once_with(
        query="What is RAG?",
        chunks=sample_chunks,
        top_k=5,
    )


@pytest.mark.asyncio
async def test_search_strips_query_whitespace(
    mock_retriever: MagicMock,
    mock_reranker: MagicMock,
    user_id: UUID,
    sample_chunks: list[RetrievedChunk],
) -> None:
    mock_retriever.retrieve.return_value = sample_chunks
    mock_reranker.rerank.return_value = sample_chunks

    service = SearchService(retriever=mock_retriever, reranker=mock_reranker)
    await service.search(query="  Hello World  ", user_id=user_id, top_k=3)

    mock_retriever.retrieve.assert_awaited_once()
    call_args = mock_retriever.retrieve.await_args
    assert call_args is not None
    assert call_args.kwargs["query"] == "Hello World"


@pytest.mark.asyncio
async def test_search_passes_scoping_parameters(
    mock_retriever: MagicMock,
    mock_reranker: MagicMock,
    user_id: UUID,
    sample_chunks: list[RetrievedChunk],
) -> None:
    mock_retriever.retrieve.return_value = sample_chunks
    mock_reranker.rerank.return_value = sample_chunks

    col_id = uuid4()
    doc_ids = [uuid4(), uuid4()]

    service = SearchService(retriever=mock_retriever, reranker=mock_reranker)
    await service.search(
        query="test",
        user_id=user_id,
        collection_id=col_id,
        document_ids=doc_ids,
        top_k=3,
    )

    mock_retriever.retrieve.assert_awaited_once_with(
        query="test",
        user_id=user_id,
        collection_id=col_id,
        document_ids=doc_ids,
        top_k=3,
    )


# ---------------------------------------------------------------------------
# Empty / edge cases
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_search_raises_empty_query_error(
    mock_retriever: MagicMock,
    mock_reranker: MagicMock,
    user_id: UUID,
) -> None:
    service = SearchService(retriever=mock_retriever, reranker=mock_reranker)

    with pytest.raises(EmptyQueryError, match="must not be empty"):
        await service.search(query="", user_id=user_id)

    with pytest.raises(EmptyQueryError, match="must not be empty"):
        await service.search(query="   ", user_id=user_id)

    mock_retriever.retrieve.assert_not_called()
    mock_reranker.rerank.assert_not_called()


@pytest.mark.asyncio
async def test_search_returns_empty_list_when_no_chunks_retrieved(
    mock_retriever: MagicMock,
    mock_reranker: MagicMock,
    user_id: UUID,
) -> None:
    mock_retriever.retrieve.return_value = []

    service = SearchService(retriever=mock_retriever, reranker=mock_reranker)
    result = await service.search(query="empty query", user_id=user_id, top_k=5)

    assert result == []
    mock_reranker.rerank.assert_not_called()




# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_search_propagates_retriever_exception(
    mock_retriever: MagicMock,
    mock_reranker: MagicMock,
    user_id: UUID,
) -> None:
    mock_retriever.retrieve.side_effect = RetrieverUnavailableError("Qdrant down")

    service = SearchService(retriever=mock_retriever, reranker=mock_reranker)
    with pytest.raises(RetrieverUnavailableError, match="Qdrant down"):
        await service.search(query="test", user_id=user_id, top_k=5)


@pytest.mark.asyncio
async def test_search_propagates_reranker_exception(
    mock_retriever: MagicMock,
    mock_reranker: MagicMock,
    user_id: UUID,
    sample_chunks: list[RetrievedChunk],
) -> None:
    mock_retriever.retrieve.return_value = sample_chunks
    mock_reranker.rerank.side_effect = RerankerUnavailableError("Model OOM")

    service = SearchService(retriever=mock_retriever, reranker=mock_reranker)
    with pytest.raises(RerankerUnavailableError, match="Model OOM"):
        await service.search(query="test", user_id=user_id, top_k=5)


@pytest.mark.asyncio
async def test_search_wraps_unexpected_retriever_error(
    mock_retriever: MagicMock,
    mock_reranker: MagicMock,
    user_id: UUID,
) -> None:
    mock_retriever.retrieve.side_effect = RuntimeError("unexpected")

    service = SearchService(retriever=mock_retriever, reranker=mock_reranker)
    with pytest.raises(SearchError, match="Retrieval failed: unexpected"):
        await service.search(query="test", user_id=user_id, top_k=5)


@pytest.mark.asyncio
async def test_search_wraps_unexpected_reranker_error(
    mock_retriever: MagicMock,
    mock_reranker: MagicMock,
    user_id: UUID,
    sample_chunks: list[RetrievedChunk],
) -> None:
    mock_retriever.retrieve.return_value = sample_chunks
    mock_reranker.rerank.side_effect = RuntimeError("unexpected")

    service = SearchService(retriever=mock_retriever, reranker=mock_reranker)
    with pytest.raises(SearchError, match="Reranking failed: unexpected"):
        await service.search(query="test", user_id=user_id, top_k=5)


# ---------------------------------------------------------------------------
# Metadata preservation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_search_preserves_chunk_metadata_through_rerank(
    mock_retriever: MagicMock,
    mock_reranker: MagicMock,
    user_id: UUID,
) -> None:
    doc_id = str(uuid4())
    chunks = [
        RetrievedChunk(
            text="Some content.",
            page=42,
            section="Appendix",
            score=0.5,
            document_id=doc_id,
            chunk_index=7,
        )
    ]
    mock_retriever.retrieve.return_value = chunks
    mock_reranker.rerank.return_value = chunks

    service = SearchService(retriever=mock_retriever, reranker=mock_reranker)
    result = await service.search(query="test", user_id=user_id, top_k=5)

    assert len(result) == 1
    chunk = result[0]
    assert chunk.text == "Some content."
    assert chunk.page == 42
    assert chunk.section == "Appendix"
    assert chunk.document_id == doc_id
    assert chunk.chunk_index == 7


# ---------------------------------------------------------------------------
# Latency logging
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_search_logs_latency_metrics(
    caplog: pytest.LogCaptureFixture,
    mock_retriever: MagicMock,
    mock_reranker: MagicMock,
    user_id: UUID,
    sample_chunks: list[RetrievedChunk],
) -> None:
    mock_retriever.retrieve.return_value = sample_chunks
    mock_reranker.rerank.return_value = sample_chunks[:2]

    with caplog.at_level(logging.INFO):
        service = SearchService(retriever=mock_retriever, reranker=mock_reranker)
        result = await service.search(query="log test", user_id=user_id, top_k=2)

    assert len(result) == 2
    assert "Search completed" in caplog.text
    assert "query=log test" in caplog.text
    assert f"user_id={user_id}" in caplog.text
    assert "retrieval_latency=" in caplog.text
    assert "rerank_latency=" in caplog.text
    assert "total_latency=" in caplog.text
    assert "retrieved=3" in caplog.text
    assert "reranked=2" in caplog.text


@pytest.mark.asyncio
async def test_search_logs_empty_retrieval(
    caplog: pytest.LogCaptureFixture,
    mock_retriever: MagicMock,
    mock_reranker: MagicMock,
    user_id: UUID,
) -> None:
    mock_retriever.retrieve.return_value = []

    with caplog.at_level(logging.INFO):
        service = SearchService(retriever=mock_retriever, reranker=mock_reranker)
        result = await service.search(query="nothing", user_id=user_id, top_k=5)

    assert result == []
    assert "Empty retrieval" in caplog.text
    assert "query=nothing" in caplog.text
