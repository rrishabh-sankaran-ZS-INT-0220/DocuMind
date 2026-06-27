# DocuMind

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for a detailed description of the system architecture, including the retrieval pipeline (SearchService → HybridRetriever → BGEReranker), dependency injection, configuration, and domain exceptions.

The QA pipeline uses `SearchService` internally, but `SearchService` has no dependency on LLMs or prompt building.


AI-powered RAG pipeline for querying PDFs, Word documents, and text files with document-grounded and LLM-assisted responses.

## Backend (FastAPI) Status

**Current scope:** Backend skeleton based on the Academic RAG Platform spec.

- [x] Create ackend/ layout and pp/ package
- [x] Configure Settings via Pydantic (ackend/app/config.py)
- [x] Set up async SQLAlchemy base + session (ackend/app/db/*)
- [x] Create FastAPI application factory with CORS (ackend/app/main.py)
- [x] Add API v1 router and a /health/ping endpoint (ackend/app/api/v1/*)
- [x] Add auth router skeleton with Google OAuth endpoints (ackend/app/api/v1/auth.py)
- [x] Add core JWT + password utilities (ackend/app/core/security.py)
- [x] Add basic OAuth helpers and enums (ackend/app/core/oauth.py)
- [x] Implement core DB models (User, Collection, Document, QASession, QAMessage) with UUID PKs (ackend/app/db/models/*)
- [x] Set up Alembic config and initial migration (ackend/alembic/*)
- [x] Add unit tests to validate table creation (ackend/tests/test_models.py)
- [x] Implement document management API skeleton (ackend/app/api/v1/documents.py)
- [x] Implement document storage and validation service (ackend/app/services/document_service.py)
- [x] Implement document parsers for PDF, DOCX, TXT, MD (ackend/app/rag/parsers/*)
- [x] Add parser tests with sample documents (ackend/tests/test_parsers.py)
- [x] Implement semantic chunker with overlap (ackend/app/rag/pipeline/chunker.py)
- [x] Add chunker tests (ackend/tests/test_chunker.py)
- [ ] Wire Authlib and full OAuth login/redirect flow

- [x] Implement SearchService with BaseRetriever/BaseReranker abstractions
- [x] Implement HybridRetriever
- [x] Implement BGEReranker
- [x] Add search service tests
- [x] Create ARCHITECTURE.md documenting retrieval lifecycle

- [ ] Implement /auth/me with real user model + DB
- [ ] Implement full document ingestion and RAG pipeline services
- [ ] Implement QA endpoints (qa.py) wired to RAG pipeline
- [ ] Implement collections management (collections.py)
- [ ] Integrate Qdrant + hybrid search + reranking

## Document Parsing & Chunking

Parsers live under ackend/app/rag/parsers/ and produce ParsedDocument/ParsedPage objects.

Chunking lives under ackend/app/rag/pipeline/chunker.py.

### Chunking Rules

- Default max tokens per chunk: 512.
- Overlap between chunks: 64 tokens.
- Chunks never cross page boundaries.
- Page number and section title from ParsedPage are preserved on each Chunk.
- Tiny trailing fragments smaller than the overlap are merged into the previous chunk to avoid very small chunks.

### Chunk Data Structure

- Chunk
  - 	ext: chunk text content.
  - page: page number from the source ParsedPage.
  - section: section title from the source ParsedPage (or None).
  - chunk_index: global index across the document.

Tests for chunking behavior are in ackend/tests/test_chunker.py.

## Document Management API

Document endpoints live under ackend/app/api/v1/documents.py and are mounted at /api/v1/documents.

(See previous section in this README for full details.)

## Migrations (Alembic)

`ash
cd backend
alembic upgrade head
`

## Testing

`ash
cd backend
pytest
`

## Running the Backend

`ash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn backend.app.main:app --reload
`

This README will be updated periodically as backend milestones are completed.
