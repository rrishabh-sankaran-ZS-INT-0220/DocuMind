import logging
from pathlib import Path
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.models.document import Document
from backend.app.rag.parsers.base import ParsedDocument
from backend.app.rag.parsers.pdf import PDFParser
from backend.app.rag.parsers.docx_parser import DOCXParser
from backend.app.rag.parsers.txt_parser import TXTParser
from backend.app.rag.parsers.markdown_parser import MarkdownParser
from backend.app.rag.pipeline.chunker import chunk_document
from backend.app.rag.embeddings import embed_texts, get_embedding_model
from backend.app.rag.qdrant_client import ensure_collection, upsert_document_chunks
from backend.app.services.document_service import UPLOAD_ROOT
from backend.app.db.models.document_chunk import DocumentChunk

logger = logging.getLogger("documind.ingestion")


class IngestionError(Exception):
    """Base exception for ingestion pipeline errors."""


class DocumentNotFoundError(IngestionError):
    """Raised when a document record cannot be found."""


class DocumentFileNotFoundError(IngestionError):
    """Raised when the uploaded file for a document is missing."""


class IngestionManager:
    """Orchestrates the ingestion pipeline for a single document.

    Stages:
    - load_document
    - mark_processing
    - load_file
    - parse
    - chunk
    - embed
    - ensure_collection
    - index_chunks
    - mark_ready / mark_failed
    """

    def __init__(self, db: AsyncSession, collection_name: str = "documents_bge_large") -> None:
        self.db = db
        self.collection_name = collection_name

    async def load_document(self, document_id) -> Document:
        logger.info("ingestion.load_document.start", extra={"document_id": str(document_id)})
        stmt = select(Document).where(Document.id == document_id)
        result = await self.db.execute(stmt)
        doc = result.scalar_one_or_none()

        if doc is None:
            logger.warning("ingestion.load_document.missing", extra={"document_id": str(document_id)})
            raise DocumentNotFoundError(f"Document {document_id} not found")

        logger.info(
            "ingestion.load_document.success",
            extra={"document_id": str(doc.id), "status": doc.status},
        )
        return doc

    async def mark_processing(self, doc: Document) -> None:
        logger.info("ingestion.status.processing", extra={"document_id": str(doc.id)})
        doc.status = "processing"
        doc.error_message = None
        await self.db.commit()
        await self.db.refresh(doc)

    async def mark_ready(
        self,
        doc: Document,
        vector_collection: str,
        vector_count: int,
        extra_metadata: Optional[dict] = None,
    ) -> None:
        logger.info(
            "ingestion.status.ready",
            extra={
                "document_id": str(doc.id),
                "vector_collection": vector_collection,
                "vector_count": vector_count,
            },
        )
        doc.status = "ready"
        doc.vector_collection = vector_collection
        doc.vector_count = vector_count
        base_meta = doc.extra_metadata or {}
        merged_meta = {**base_meta, **(extra_metadata or {})}
        doc.extra_metadata = merged_meta
        await self.db.commit()
        await self.db.refresh(doc)

    async def mark_failed(self, doc: Document, error_message: str) -> None:
        logger.error(
            "ingestion.status.failed",
            extra={"document_id": str(doc.id), "error": error_message},
        )
        doc.status = "failed"
        doc.error_message = error_message
        await self.db.commit()
        await self.db.refresh(doc)

    def _load_document_file(self, doc: Document) -> Path:
        """Locate the uploaded file path for a given document."""
        logger.info("ingestion.load_file.start", extra={"document_id": str(doc.id)})

        user_dir = UPLOAD_ROOT / str(doc.owner_id)
        doc_dir = user_dir / str(doc.id)

        if not doc_dir.exists():
            msg = f"Document directory not found: {doc_dir}"
            logger.error(
                "ingestion.load_file.missing_directory",
                extra={"document_id": str(doc.id), "directory": str(doc_dir)},
            )
            raise DocumentFileNotFoundError(msg)

        files = list(doc_dir.iterdir())
        if not files:
            msg = f"No files found for document: {doc.id}"
            logger.error(
                "ingestion.load_file.no_files",
                extra={"document_id": str(doc.id), "directory": str(doc_dir)},
            )
            raise DocumentFileNotFoundError(msg)

        file_path = files[0]
        logger.info(
            "ingestion.load_file.success",
            extra={"document_id": str(doc.id), "file_path": str(file_path)},
        )
        return file_path

    async def _parse_file(self, path: Path, content_type: str | None) -> ParsedDocument:
        """Dispatch to the correct parser based on content type / extension."""
        logger.info(
            "ingestion.parse.start",
            extra={"file_path": str(path), "content_type": content_type},
        )

        ext = path.suffix.lower()
        mime = content_type or ""

        if ext == ".pdf" or mime == "application/pdf":
            parser = PDFParser()
            parsed = await parser.parse(path)
        elif ext == ".docx" or mime == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            parser = DOCXParser()
            parsed = await parser.parse(path)
        elif ext in {".txt"} or mime == "text/plain":
            parser = TXTParser()
            parsed = await parser.parse(path)
        elif ext in {".md", ".markdown"} or mime == "text/markdown":
            parser = MarkdownParser()
            parsed = await parser.parse(path)
        else:
            raise ValueError(f"Unsupported document type: {ext} ({mime})")

        logger.info(
            "ingestion.parse.success",
            extra={
                "file_path": str(path),
                "pages": len(parsed.pages),
            },
        )
        return parsed

    async def run(self, document_id) -> None:
        """Run the full ingestion pipeline for a given document id.

        Idempotence:
        - If document is already 'ready', the pipeline exits early.
        - Existing Qdrant points are overwritten via upsert by `upsert_document_chunks`.
        """
        logger.info("ingestion.run.start", extra={"document_id": str(document_id)})

        try:
            doc = await self.load_document(document_id)
        except DocumentNotFoundError as exc:
            logger.warning(
                "ingestion.run.document_missing",
                extra={"document_id": str(document_id), "error": str(exc)},
            )
            return

        # Idempotence: skip if already fully ingested
        if doc.status == "ready":
            logger.info(
                "ingestion.run.skip_already_ready",
                extra={"document_id": str(doc.id)},
            )
            return

        await self.mark_processing(doc)

        try:
            # Stage: load file
            file_path = self._load_document_file(doc)

            # Stage: parse
            parsed = await self._parse_file(file_path, doc.content_type)

            # Stage: chunk
            logger.info("ingestion.chunk.start", extra={"document_id": str(doc.id)})
            chunks = chunk_document(parsed)
            if not chunks:
                raise IngestionError("Parsed document produced no chunks")
            document_chunks: list[DocumentChunk] = []
            for c in chunks:
                token_count = len(c.text.split())
                document_chunks.append(
                    DocumentChunk(
                        document_id=doc.id,
                        page=c.page,
                        section=c.section,
                        chunk_index=c.chunk_index,
                        text=c.text,
                        token_count=token_count,
                    )
                )

            self.db.add_all(document_chunks)
            await self.db.flush()
            
            texts: List[str] = [c.text for c in chunks]
            pages: List[int] = [c.page for c in chunks]
            sections: List[Optional[str]] = [c.section for c in chunks]

            logger.info(
                "ingestion.chunk.success",
                extra={"document_id": str(doc.id), "chunk_count": len(chunks)},
            )

            # Stage: embedding
            logger.info(
                "ingestion.embed.start",
                extra={"document_id": str(doc.id), "text_count": len(texts)},
            )
            model = get_embedding_model()
            dim = model.get_sentence_embedding_dimension()

            # Stage: ensure collection
            logger.info(
                "ingestion.collection.ensure.start",
                extra={"collection_name": self.collection_name, "vector_size": dim},
            )
            ensure_collection(collection_name=self.collection_name, vector_size=dim)
            logger.info(
                "ingestion.collection.ensure.success",
                extra={"collection_name": self.collection_name},
            )

            vectors = embed_texts(texts)
            logger.info(
                "ingestion.embed.success",
                extra={
                    "document_id": str(doc.id),
                    "vector_count": len(vectors),
                    "embedding_dim": dim,
                },
            )

            # Stage: index
            logger.info(
                "ingestion.index.start",
                extra={
                    "document_id": str(doc.id),
                    "collection_name": self.collection_name,
                },
            )
            count = upsert_document_chunks(
                collection_name=self.collection_name,
                document_id=doc.id,
                texts=texts,
                vectors=vectors,
                pages=pages,
                sections=sections,
            )
            logger.info(
                "ingestion.index.success",
                extra={
                    "document_id": str(doc.id),
                    "collection_name": self.collection_name,
                    "indexed_chunks": count,
                },
            )

            await self.mark_ready(
                doc,
                vector_collection=self.collection_name,
                vector_count=count,
                extra_metadata={"chunk_count": count},
            )

        except Exception as exc:  # noqa: BLE001
            # Catch any unexpected error, mark document failed, and log.
            await self.mark_failed(doc, str(exc))
            logger.exception(
                "ingestion.run.error",
                extra={"document_id": str(doc.id)},
            )

        logger.info("ingestion.run.finish", extra={"document_id": str(document_id)})