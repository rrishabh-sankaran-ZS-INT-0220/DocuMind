import sqlalchemy as sa
from sqlalchemy import inspect

from backend.app.db.base import Base
from backend.app.db.models import Collection, Document, QAMessage, QASession, User


def test_metadata_creates_all_tables():
    engine = sa.create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    inspector = inspect(engine)
    tables = set(inspector.get_table_names())

    assert "users" in tables
    assert "collections" in tables
    assert "documents" in tables
    assert "qa_sessions" in tables
    assert "qa_messages" in tables
    assert "session_documents" in tables

    # Basic relationship sanity checks via foreign keys
    user_fks = inspector.get_foreign_keys("collections")
    assert any(fk["referred_table"] == "users" for fk in user_fks)

    doc_fks = inspector.get_foreign_keys("documents")
    assert any(fk["referred_table"] == "users" for fk in doc_fks)

    qa_session_fks = inspector.get_foreign_keys("qa_sessions")
    assert any(fk["referred_table"] == "users" for fk in qa_session_fks)

    qa_message_fks = inspector.get_foreign_keys("qa_messages")
    assert any(fk["referred_table"] == "qa_sessions" for fk in qa_message_fks)

    session_docs_fks = inspector.get_foreign_keys("session_documents")
    referred_tables = {fk["referred_table"] for fk in session_docs_fks}
    assert {"qa_sessions", "documents"}.issubset(referred_tables)
