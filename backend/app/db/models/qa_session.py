from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Table,
    Column,
    Boolean,
    DateTime,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base

# Association table: many-to-many between QASession and Document
session_documents = Table(
    "session_documents",
    Base.metadata,
    Column(
        "session_id",
        UUID(as_uuid=True),
        ForeignKey("qa_sessions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "document_id",
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class QASession(Base):
    __tablename__ = "qa_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="qa_sessions",
    )
    messages: Mapped[list["QAMessage"]] = relationship(
        "QAMessage",
        back_populates="session",
        cascade="all, delete-orphan",
    )
    documents: Mapped[list["Document"]] = relationship(
        "Document",
        secondary=session_documents,
        back_populates="qa_sessions",
    )


class QAMessage(Base):
    __tablename__ = "qa_messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("qa_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # 'user' | 'assistant'
    content: Mapped[str] = mapped_column(Text, nullable=False)
    message_type: Mapped[str] = mapped_column(
        String(20),
        default="open_ended",
        nullable=False,
    )  # 'open_ended' | 'mcq'

    # JSONB fields for structured metadata
    sources: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    confidence: Mapped[str | None] = mapped_column(String(20), nullable=True)
    retrieval_meta: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    llm_provider: Mapped[str | None] = mapped_column(String(50), nullable=True)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationships
    session: Mapped["QASession"] = relationship(
        "QASession",
        back_populates="messages",
    )