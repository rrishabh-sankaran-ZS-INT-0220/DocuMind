from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from arq import cron

from backend.app.config import settings
from backend.app.db.models.document import Document
from backend.app.rag.parsers.base import ParsedDocument
from backend.app.rag.parsers.pdf import PDFParser
from backend.app.rag.parsers.docx_parser import DOCXParser
from backend.app.rag.parsers.txt_parser import TXTParser
from backend.app.rag.parsers.markdown_parser import MarkdownParser
from backend.app.rag.pipeline.chunker import chunk_document
from backend.app.rag.embeddings import embed_texts, get_embedding_model
from backend.app.rag.qdrant_client import (
    ensure_collection,
    upsert_document_chunks,
)
from backend.app.config import settings
from arq import ArqRedis
import asyncio

from backend.app.services.storage import get_storage_backend


async def _load_document_file(doc: Document) -> bytes:
    """Retrieve the uploaded file bytes from the configured storage backend."""
    storage = get_storage_backend()
    storage_key = None
    if doc.extra_metadata:
        storage_key = doc.extra_metadata.get("storage_key")
    if not storage_key:
        raise FileNotFoundError(f"No storage key found for document: {doc.id}")
    return await storage.get_bytes(storage_key)


async def _parse_file(file_bytes: bytes, filename: str, content_type: Optional[str]) -> ParsedDocument:
    """Dispatch to the correct parser based on content type / extension."""
    ext = Path(filename).suffix.lower()
    mime = content_type or ""

    if ext == ".pdf" or mime == "application/pdf":
        parser = PDFParser()
        return await parser.parse_bytes(file_bytes, filename)
    if ext == ".docx" or mime == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        parser = DOCXParser()
        return await parser.parse_bytes(file_bytes, filename)
    if ext in {".txt"} or mime == "text/plain":
        parser = TXTParser()
        return await parser.parse_bytes(file_bytes, filename)
    if ext in {".md", ".markdown"} or mime == "text/markdown":
        parser = MarkdownParser()
        return await parser.parse_bytes(file_bytes, filename)

    raise ValueError(f"Unsupported document type: {ext} ({mime})")


async def run_sync_ingestion_pipeline(document_id: str) -> None:
    """Run the document ingestion pipeline for a queued document."""
    from backend.app.db.session import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        await ingest_document(db=db, document_id=document_id)


async def enqueue_ingestion_job(document_id: str) -> None:
    """Enqueue a document ingestion job in Redis using Arq."""
    redis = ArqRedis(host=settings.redis_url.split("://", 1)[1].split("/", 1)[0].split("@")[-1].split(":")[0], port=6379)
    await redis.enqueue_job("ingest_job", document_id)


async def ingest_document(db: AsyncSession, document_id) -> None:
    """Full ingestion pipeline for a document.

    Steps:
    - Load document record
    - Set status=processing
    - Parse file
    - Chunk
    - Embed
    - Ensure Qdrant collection
    - Upsert chunks into Qdrant with rich metadata
    - Update document status / metadata
    """
    stmt = select(Document).where(Document.id == document_id)
    result = await db.execute(stmt)
    doc: Optional[Document] = result.scalar_one_or_none()
    if doc is None:
        logger.warning("document_ingestion_skipped", extra={"event": "document_ingestion_skipped", "document_id": str(document_id)})
        return

    logger.info(
        "document_ingestion_started",
        extra={"event": "document_ingestion_started", "document_id": str(doc.id), "owner_id": str(doc.owner_id)},
    )

    doc.status = "processing"
    doc.error_message = None
    await db.commit()
    await db.refresh(doc)

    try:
        file_bytes = await _load_document_file(doc)
        logger.info(
            "document_ingestion_loaded",
            extra={"event": "document_ingestion_loaded", "document_id": str(doc.id), "byte_size": len(file_bytes)},
        )
        parsed = await _parse_file(file_bytes, doc.original_filename, doc.content_type)

        chunks = chunk_document(parsed)
        if not chunks:
            raise ValueError("Parsed document produced no chunks")

        texts: List[str] = [c.text for c in chunks]
        pages: List[int] = [c.page for c in chunks]
        sections: List[Optional[str]] = [c.section for c in chunks]

        model = get_embedding_model()
        dim = model.get_sentence_embedding_dimension()

        collection_name = settings.qdrant_collection_name

        ensure_collection(collection_name=collection_name, vector_size=dim)

        vectors = embed_texts(texts)

        count = upsert_document_chunks(
            collection_name=collection_name,
            owner_id=doc.owner_id,
            collection_id=doc.collection_id,
            document_id=doc.id,
            document_title=doc.title,
            texts=texts,
            vectors=vectors,
            pages=pages,
            sections=sections,
            scores=None,
        )

        doc.status = "ready"
        doc.vector_collection = collection_name
        doc.vector_count = count
        doc.extra_metadata = (doc.extra_metadata or {}) | {
            "chunk_count": count,
        }
        await db.commit()
        await db.refresh(doc)

        logger.info(
            "document_ingestion_completed",
            extra={"event": "document_ingestion_completed", "document_id": str(doc.id), "chunk_count": count},
        )

    except Exception as exc:
        logger.exception(
            "document_ingestion_failed",
            extra={"event": "document_ingestion_failed", "document_id": str(doc.id), "error": str(exc)},
        )
        doc.status = "failed"
        doc.error_message = str(exc)
        await db.commit()
        await db.refresh(doc)