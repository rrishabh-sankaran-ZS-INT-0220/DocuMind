import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, String, Table, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base


session_documents = Table(
    "session_documents",
    Base.metadata,
    mapped_column("session_id", UUID(as_uuid=True), ForeignKey("qa_sessions.id", ondelete="CASCADE")),
    mapped_column("document_id", UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE")),
)


class QASession(Base):
    __tablename__ = "qa_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="qa_sessions")
    messages: Mapped[list["QAMessage"]] = relationship(
        "QAMessage", back_populates="session", cascade="all, delete-orphan"
    )
    documents: Mapped[list["Document"]] = relationship(
        "Document", secondary=session_documents, back_populates="qa_sessions"
    )


class QAMessage(Base):
    __tablename__ = "qa_messages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # user | assistant
    content: Mapped[str] = mapped_column(Text, nullable=False)

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("qa_sessions.id", ondelete="CASCADE"), nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    session: Mapped["QASession"] = relationship("QASession", back_populates="messages")
