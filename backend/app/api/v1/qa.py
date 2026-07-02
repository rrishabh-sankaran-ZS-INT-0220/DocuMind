import logging
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.db.session import get_db
from backend.app.db.models import (
    User,
    Document,
    QASession,
    QAMessage,
)
from backend.app.dependencies import get_current_user
from backend.app.schemas.qa import (
    QARequest,
    QAResponse,
    MCQRequest,
    MCQResponse,
    QASessionCreate,
    QASessionResponse,
    QASessionWithMessages,
    QAMessageResponse,
)
from backend.app.services.rag_pipeline import run_qa_pipeline, run_mcq_pipeline
from backend.app.core.rate_limit import build_rate_limiter
from backend.app.config import settings

router = APIRouter(prefix="/qa", tags=["qa"])
logger = logging.getLogger(__name__)
qa_rate_limiter = build_rate_limiter(
    limit=settings.qa_rate_limit_requests,
    window_seconds=settings.qa_rate_limit_window_seconds,
    limiter_name="qa",
)


# ----------------- Session management -----------------


@router.post("/sessions", response_model=QASessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    payload: QASessionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QASession:
    """Create a new QA session, optionally attaching documents."""
    session = QASession(
        user_id=current_user.id,
        title=payload.title,
        is_active=True,
    )
    db.add(session)
    await db.flush()  # get session.id before associating docs

    # Attach documents if provided
    if payload.document_ids:
        stmt_docs = select(Document).where(
            Document.owner_id == current_user.id,
            Document.id.in_(payload.document_ids),
        )
        result_docs = await db.execute(stmt_docs)
        docs = list(result_docs.scalars().all())

        for doc in docs:
            session.documents.append(doc)

    await db.commit()
    await db.refresh(session)
    return session


@router.get("/sessions", response_model=list[QASessionResponse])
async def list_sessions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[QASession]:
    """List QA sessions for the current user."""
    stmt = select(QASession).where(QASession.user_id == current_user.id).order_by(QASession.created_at.desc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("/sessions/{session_id}", response_model=QASessionWithMessages)
async def get_session(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QASessionWithMessages:
    """Get a QA session with its message history."""
    stmt = select(QASession).where(
        QASession.id == session_id,
        QASession.user_id == current_user.id,
    )
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    messages_res: List[QAMessageResponse] = []
    for msg in session.messages:
        messages_res.append(
            QAMessageResponse(
                id=msg.id,
                session_id=msg.session_id,
                role=msg.role,
                content=msg.content,
                message_type=msg.message_type,
                confidence=msg.confidence,
            )
        )

    return QASessionWithMessages(
        id=session.id,
        title=session.title,
        is_active=session.is_active,
        user_id=session.user_id,
        messages=messages_res,
    )


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete a QA session and its messages."""
    stmt = select(QASession).where(
        QASession.id == session_id,
        QASession.user_id == current_user.id,
    )
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    await db.delete(session)
    await db.commit()


# ----------------- QA over documents (global) -----------------


@router.post("/ask", response_model=QAResponse)
async def ask_question(
    payload: QARequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _rate_limit: None = Depends(qa_rate_limiter),
) -> QAResponse:
    """Ask an open-ended question over ingested documents."""
    if not payload.question.strip():
        logger.warning(
            "qa_question_empty",
            extra={"event": "qa_question_empty", "user_id": str(current_user.id)},
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question must not be empty",
        )

    logger.info(
        "qa_question_received",
        extra={"event": "qa_question_received", "user_id": str(current_user.id), "question_length": len(payload.question)},
    )

    return await run_qa_pipeline(
        db=db,
        user_id=str(current_user.id),
        req=payload,
    )


@router.post("/mcq", response_model=MCQResponse)
async def mcq_question(
    payload: MCQRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MCQResponse:
    """Ask a multiple-choice question and score options."""
    if not payload.question.strip():
        logger.warning(
            "qa_mcq_question_empty",
            extra={"event": "qa_mcq_question_empty", "user_id": str(current_user.id)},
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question must not be empty",
        )
    if not payload.options:
        logger.warning(
            "qa_mcq_options_empty",
            extra={"event": "qa_mcq_options_empty", "user_id": str(current_user.id)},
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one option is required",
        )

    logger.info(
        "qa_mcq_question_received",
        extra={"event": "qa_mcq_question_received", "user_id": str(current_user.id), "option_count": len(payload.options)},
    )

    return await run_mcq_pipeline(
        db=db,
        user_id=str(current_user.id),
        req=payload,
    )