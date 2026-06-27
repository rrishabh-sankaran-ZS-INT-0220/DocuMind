from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID

import requests
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.config import settings
from backend.app.db.models.document import Document
from backend.app.rag.retrieval.base import RetrievedChunk
from backend.app.rag.retrieval.hybrid_retriever import HybridRetriever
from backend.app.rag.retrieval.bge_reranker import BGEReranker
from backend.app.services.search_service import SearchService
from backend.app.schemas.qa import (
    MCQOption,
    MCQOptionScore,
    MCQRequest,
    MCQResponse,
    QARequest,
    QAResponse,
    SourceCitation,
    ConfidenceLevel,
)

# ---------------------------------------------------------------------------
# Constants & Models
# ---------------------------------------------------------------------------

RELEVANCE_THRESHOLD = 0.40

# OpenRouter configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "anthropic/claude-3.5-haiku"  # change if you prefer another model




# Lazy-initialised default SearchService
_search_service: Optional[SearchService] = None


def _get_search_service() -> SearchService:
    """Return (and cache) a SearchService with default implementations."""
    global _search_service
    if _search_service is None:
        _search_service = SearchService(
            retriever=HybridRetriever(),
            reranker=BGEReranker(),
        )
    return _search_service


# ---------------------------------------------------------------------------
# Master prompts (simplified but aligned with spec)
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are an academic RAG assistant.

You must answer using ONLY the provided document context. Do not use outside knowledge.
If the context is insufficient to answer the question reliably, say you cannot find the answer.
Always cite sources with document, page, and section information.
"""

QA_PROMPT_TEMPLATE = """{system_prompt}

You are given multiple source excerpts from academic or knowledge documents.

Context:
{context_blocks}

Question:
{question}

Instructions:
- Base your answer only on the context.
- If you cannot answer confidently from the context, say you cannot answer from the documents.
- Provide a concise, well-structured answer suitable for a student or researcher.
- Do not mention that you were given 'context'; just answer normally.
"""

MCQ_PROMPT_TEMPLATE = """{system_prompt}

You are given multiple source excerpts from academic or knowledge documents.

Context:
{context_blocks}

Question:
{question}

Options:
{options_block}

Instructions:
- For each option, assess how well it is supported by the context.
- Choose the single best option.
- Provide a short justification for your choice.
- If none can be supported, say that explicitly.
"""


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------


def _confidence_from_score(score: float) -> ConfidenceLevel:
    if score < RELEVANCE_THRESHOLD:
        return "not_found"
    if score >= 0.85:
        return "high"
    if score >= 0.60:
        return "medium"
    return "low"


def _build_context_blocks(chunks: List[RetrievedChunk]) -> str:
    blocks = []
    for i, c in enumerate(chunks):
        blocks.append(
            f"--- Source {i + 1} ---\n"
            f"Document ID: {c.document_id}\n"
            f"Title: {c.document_title or 'Unknown'}\n"
            f"Page: {c.page}\n"
            f"Section: {c.section or 'N/A'}\n"
            f"Relevance: {c.score:.2f}\n"
            f"Content: {c.text}"
        )
    return "\n\n".join(blocks)


def _build_mcq_options_block(options: List[MCQOption]) -> str:
    lines = []
    for opt in options:
        lines.append(f"{opt.id}. {opt.text}")
    return "\n".join(lines)


async def _load_document_titles(
    db: AsyncSession,
    document_ids: List[str],
) -> dict[str, str]:
    """Load titles for documents referenced in results."""
    unique_ids = list({doc_id for doc_id in document_ids})
    if not unique_ids:
        return {}

    stmt = select(Document).where(Document.id.in_(unique_ids))
    result = await db.execute(stmt)
    docs = result.scalars().all()

    id_to_title: dict[str, str] = {}
    for d in docs:
        id_to_title[str(d.id)] = d.title
    return id_to_title


# (Retrieval and reranking moved to SearchService / HybridRetriever / BGEReranker)


# ---------------------------------------------------------------------------
# LLM call helper (OpenRouter)
# ---------------------------------------------------------------------------


def _call_llm(prompt: str) -> str:
    """Call an LLM via OpenRouter with temperature 0.1.

    Requires OPENROUTER_API_KEY environment variable.
    """
    if not OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set")

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "model": OPENROUTER_MODEL,
        "temperature": 0.1,
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful academic assistant.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    }

    resp = requests.post(OPENROUTER_ENDPOINT, json=body, headers=headers, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    # OpenRouter follows OpenAI-style response shape
    choices = data.get("choices") or []
    if not choices:
        return ""

    message = choices[0].get("message") or {}
    return message.get("content", "") or ""


# ---------------------------------------------------------------------------
# Public pipeline APIs
# ---------------------------------------------------------------------------


async def run_qa_pipeline(
    db: AsyncSession,
    user_id: str,
    req: QARequest,
) -> QAResponse:
    # 1. Search via SearchService
    search = _get_search_service()
    reranked = await search.search(
        query=req.question,
        user_id=UUID(user_id),
        top_k=req.top_k,
    )

    if not reranked:
        return QAResponse(
            answer="I could not find relevant information in the documents.",
            confidence="not_found",
            score=0.0,
            sources=[],
        )

    # Score is best reranker score
    best_score = reranked[0].score
    confidence = _confidence_from_score(best_score)

    if confidence == "not_found":
        return QAResponse(
            answer="I could not find relevant information in the documents.",
            confidence=confidence,
            score=best_score,
            sources=[],
        )

    # 4. Build context + prompt
    # Load document titles for citations
    id_to_title = await _load_document_titles(
        db=db,
        document_ids=[c.document_id for c in reranked],
    )
    for c in reranked:
        c.document_title = id_to_title.get(c.document_id, None)

    context_blocks = _build_context_blocks(reranked)
    prompt = QA_PROMPT_TEMPLATE.format(
        system_prompt=SYSTEM_PROMPT,
        context_blocks=context_blocks,
        question=req.question,
    )

    # 5. Call LLM
    answer_text = _call_llm(prompt)

    # 6. Build citations
    sources: List[SourceCitation] = []
    for c in reranked:
        snippet = c.text[:500]
        sources.append(
            SourceCitation(
                document_id=c.document_id,
                document_title=c.document_title,
                page=c.page,
                section=c.section,
                snippet=snippet,
                score=c.score,
            )
        )

    return QAResponse(
        answer=answer_text,
        confidence=confidence,
        score=best_score,
        sources=sources,
    )


async def run_mcq_pipeline(
    db: AsyncSession,
    user_id: str,
    req: MCQRequest,
) -> MCQResponse:
    # 1. Search via SearchService
    search = _get_search_service()
    reranked = await search.search(
        query=req.question,
        user_id=UUID(user_id),
        top_k=req.top_k,
    )
    if not reranked:
        return MCQResponse(
            selected_option_id=None,
            confidence="not_found",
            options=[],
            sources=[],
        )

    best_score = reranked[0].score
    confidence = _confidence_from_score(best_score)

    # Load document titles for citations
    id_to_title = await _load_document_titles(
        db=db,
        document_ids=[c.document_id for c in reranked],
    )
    for c in reranked:
        c.document_title = id_to_title.get(c.document_id, None)

    context_blocks = _build_context_blocks(reranked)
    options_block = _build_mcq_options_block(req.options)

    prompt = MCQ_PROMPT_TEMPLATE.format(
        system_prompt=SYSTEM_PROMPT,
        context_blocks=context_blocks,
        question=req.question,
        options_block=options_block,
    )

    llm_output = _call_llm(prompt)

    # Basic parsing: look for e.g. "Answer: A" or "A." or "(A)" in the LLM output
    selected_id: Optional[str] = None
    normalized_output = llm_output.upper()
    for opt in req.options:
        marker_variants = [
            f"ANSWER: {opt.id.upper()}",
            f"{opt.id.upper()}.",
            f"({opt.id.upper()})",
            f"OPTION {opt.id.upper()}",
        ]
        if any(m in normalized_output for m in marker_variants):
            selected_id = opt.id
            break

    # We also assign simple scores:
    option_scores: List[MCQOptionScore] = []
    for opt in req.options:
        option_scores.append(
            MCQOptionScore(
                id=opt.id,
                score=1.0 if opt.id == selected_id else 0.0,
                justification=llm_output[:500],
            )
        )

    sources: List[SourceCitation] = []
    for c in reranked:
        snippet = c.text[:500]
        sources.append(
            SourceCitation(
                document_id=c.document_id,
                document_title=c.document_title,
                page=c.page,
                section=c.section,
                snippet=snippet,
                score=c.score,
            )
        )

    return MCQResponse(
        selected_option_id=selected_id,
        confidence=confidence,
        options=option_scores,
        sources=sources,
    )