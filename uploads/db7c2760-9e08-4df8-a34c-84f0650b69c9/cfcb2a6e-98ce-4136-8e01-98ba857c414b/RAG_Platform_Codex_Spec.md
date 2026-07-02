# Academic Document Intelligence Platform — Full Codex Implementation Spec
> **Senior AI Architect Review | RAG v1 | Codex-Ready**
> Version: 1.0 | Stack: FastAPI · React · Qdrant · PostgreSQL · ShadCN · Docker

---

## TABLE OF CONTENTS

1. [Project Summary](#1-project-summary)
2. [Full Project Structure](#2-full-project-structure)
3. [API Endpoints — Complete Reference](#3-api-endpoints--complete-reference)
4. [RAG Pipeline Architecture](#4-rag-pipeline-architecture)
5. [Master Prompts](#5-master-prompts)
6. [OAuth Implementation](#6-oauth-implementation)
7. [Backend Implementation Guide](#7-backend-implementation-guide)
8. [Frontend Implementation Guide — ShadCN + Motion](#8-frontend-implementation-guide--shadcn--motion)
9. [Docker & Containerization](#9-docker--containerization)
10. [Environment Variables](#10-environment-variables)
11. [Database Schema](#11-database-schema)
12. [Codex Feed Summary](#12-codex-feed-summary)

---

## 1. PROJECT SUMMARY

| Attribute | Value |
|---|---|
| **Name** | Academic RAG Platform |
| **Goal** | Upload docs → ask questions → get grounded answers with citations |
| **Primary Use** | Academic / knowledge-based learning |
| **V1 Scope** | Hybrid search, reranking, MCQ, citations, OAuth, Docker |
| **Out of V1 Scope** | Agentic RAG, Graph RAG, Multi-Agent, RAPTOR, ColBERT |

**Architecture Pattern:** Upload → Parse → Chunk → Embed → Index → Query → Retrieve → Rerank → Generate → Cite

---

## 2. FULL PROJECT STRUCTURE

```
academic-rag-platform/
│
├── docker-compose.yml                  # Dev orchestration
├── docker-compose.prod.yml             # Prod orchestration
├── .env.example                        # Environment template
├── .gitignore
├── README.md
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   │       └── 001_initial_schema.py
│   │
│   └── app/
│       ├── main.py                     # FastAPI app entry, CORS, routers
│       ├── config.py                   # Pydantic settings from .env
│       ├── dependencies.py             # Shared DI: DB session, current user
│       │
│       ├── api/
│       │   └── v1/
│       │       ├── __init__.py
│       │       ├── router.py           # Aggregates all routers
│       │       ├── auth.py             # OAuth + JWT endpoints
│       │       ├── documents.py        # Upload, list, delete, status
│       │       ├── qa.py               # Ask, MCQ, history
│       │       ├── collections.py      # Workspace / collection management
│       │       └── health.py           # Health + readiness
│       │
│       ├── core/
│       │   ├── __init__.py
│       │   ├── security.py             # JWT create/verify, password hash
│       │   ├── oauth.py                # Google + GitHub OAuth handlers
│       │   └── exceptions.py           # Custom HTTP exceptions
│       │
│       ├── db/
│       │   ├── __init__.py
│       │   ├── base.py                 # SQLAlchemy Base
│       │   ├── session.py              # AsyncSession factory
│       │   └── models/
│       │       ├── __init__.py
│       │       ├── user.py             # User model
│       │       ├── document.py         # Document + Chunk models
│       │       ├── collection.py       # Collection model
│       │       └── qa_session.py       # QA session + message history
│       │
│       ├── schemas/
│       │   ├── __init__.py
│       │   ├── auth.py                 # Token, UserOut, OAuthUser
│       │   ├── document.py             # DocumentIn, DocumentOut, ChunkOut
│       │   ├── qa.py                   # QuestionIn, MCQIn, AnswerOut
│       │   └── collection.py           # CollectionIn, CollectionOut
│       │
│       ├── services/
│       │   ├── __init__.py
│       │   ├── document_service.py     # Orchestrates upload → parse → index
│       │   ├── qa_service.py           # Orchestrates retrieve → rerank → generate
│       │   ├── collection_service.py   # Collection CRUD
│       │   └── user_service.py         # User CRUD
│       │
│       ├── rag/
│       │   ├── __init__.py
│       │   │
│       │   ├── parsers/
│       │   │   ├── __init__.py
│       │   │   ├── base_parser.py      # Abstract parser interface
│       │   │   ├── pdf_parser.py       # PyMuPDF: text + page + section
│       │   │   ├── docx_parser.py      # python-docx: paragraphs + headings
│       │   │   └── txt_parser.py       # Plain text + markdown
│       │   │
│       │   ├── pipeline/
│       │   │   ├── __init__.py
│       │   │   ├── ingestion.py        # Full ingestion orchestrator
│       │   │   ├── chunker.py          # Semantic + sliding window chunker
│       │   │   ├── embedder.py         # BAAI/bge-large-en-v1.5 wrapper
│       │   │   └── indexer.py          # Qdrant upsert with metadata
│       │   │
│       │   ├── retrieval/
│       │   │   ├── __init__.py
│       │   │   ├── vector_retriever.py # Qdrant dense search
│       │   │   ├── bm25_retriever.py   # BM25 via rank_bm25
│       │   │   ├── hybrid_retriever.py # Calls both, fuses with RRF
│       │   │   └── reranker.py         # BGE reranker cross-encoder
│       │   │
│       │   ├── generation/
│       │   │   ├── __init__.py
│       │   │   ├── llm_router.py       # Route to OpenAI / Claude / Gemini
│       │   │   ├── answer_generator.py # Open-ended answer with citations
│       │   │   ├── mcq_evaluator.py    # MCQ option scoring + selection
│       │   │   └── citation_builder.py # Build structured source citations
│       │   │
│       │   └── prompts/
│       │       ├── __init__.py
│       │       ├── system_prompts.py   # Base system prompt
│       │       ├── qa_prompts.py       # Open-ended QA prompt templates
│       │       └── mcq_prompts.py      # MCQ evaluation prompt templates
│       │
│       └── utils/
│           ├── __init__.py
│           ├── file_utils.py           # Temp file handling, MIME check
│           └── text_utils.py           # Cleaning, normalization
│
├── frontend/
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   ├── components.json                 # ShadCN config
│   ├── public/
│   │   └── favicon.ico
│   │
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── index.css                   # Tailwind + CSS vars
│       │
│       ├── api/
│       │   ├── client.ts               # Axios instance + interceptors
│       │   ├── auth.ts                 # Auth API calls
│       │   ├── documents.ts            # Document API calls
│       │   ├── qa.ts                   # QA API calls
│       │   └── collections.ts          # Collection API calls
│       │
│       ├── auth/
│       │   ├── AuthProvider.tsx        # React context for auth state
│       │   ├── ProtectedRoute.tsx      # Redirect if not authed
│       │   └── OAuthCallback.tsx       # Handle /auth/callback redirect
│       │
│       ├── components/
│       │   ├── ui/                     # ShadCN auto-generated components
│       │   │   ├── button.tsx
│       │   │   ├── card.tsx
│       │   │   ├── dialog.tsx
│       │   │   ├── input.tsx
│       │   │   ├── badge.tsx
│       │   │   ├── progress.tsx
│       │   │   ├── separator.tsx
│       │   │   ├── scroll-area.tsx
│       │   │   ├── toast.tsx
│       │   │   ├── tooltip.tsx
│       │   │   └── skeleton.tsx
│       │   │
│       │   ├── layout/
│       │   │   ├── AppLayout.tsx       # Shell: sidebar + header + outlet
│       │   │   ├── Sidebar.tsx         # Nav with framer-motion collapse
│       │   │   └── Header.tsx          # User avatar + breadcrumb
│       │   │
│       │   ├── documents/
│       │   │   ├── DocumentUploader.tsx   # Drag & drop with motion
│       │   │   ├── DocumentCard.tsx       # Card with status badge
│       │   │   ├── DocumentList.tsx       # Animated list
│       │   │   └── ProcessingStatus.tsx   # Progress indicator
│       │   │
│       │   ├── qa/
│       │   │   ├── QuestionInput.tsx      # Open-ended input
│       │   │   ├── MCQInput.tsx           # Option A/B/C/D input
│       │   │   ├── AnswerCard.tsx         # Answer with animate-in
│       │   │   ├── CitationCard.tsx       # Source + snippet + score
│       │   │   ├── ConfidenceBadge.tsx    # high/medium/low badge
│       │   │   └── ChatHistory.tsx        # Scrollable session history
│       │   │
│       │   └── common/
│       │       ├── AnimatedContainer.tsx  # Framer-motion wrapper
│       │       ├── PageTransition.tsx     # Route transition
│       │       └── EmptyState.tsx         # Empty document / no results
│       │
│       ├── hooks/
│       │   ├── useAuth.ts
│       │   ├── useDocuments.ts
│       │   ├── useQA.ts
│       │   └── useCollections.ts
│       │
│       ├── pages/
│       │   ├── Login.tsx               # OAuth login page
│       │   ├── Dashboard.tsx           # Stats overview
│       │   ├── Documents.tsx           # Upload + manage
│       │   ├── QASession.tsx           # Ask questions
│       │   └── Collections.tsx         # Workspaces
│       │
│       ├── store/
│       │   ├── authStore.ts            # Zustand auth state
│       │   ├── documentStore.ts        # Zustand doc state
│       │   └── qaStore.ts              # Zustand QA + session state
│       │
│       └── types/
│           ├── auth.ts
│           ├── document.ts
│           └── qa.ts
│
└── infra/
    ├── nginx/
    │   └── nginx.conf                  # Reverse proxy config
    └── postgres/
        └── init.sql                    # DB initialization
```

---

## 3. API ENDPOINTS — COMPLETE REFERENCE

### Swagger / Docs URLs

| Interface | URL |
|---|---|
| **Swagger UI** | `http://localhost:8000/docs` |
| **ReDoc** | `http://localhost:8000/redoc` |
| **OpenAPI JSON** | `http://localhost:8000/openapi.json` |

---

### 3.1 Health

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/health` | None | Liveness check |
| GET | `/api/v1/health/ready` | None | Readiness: DB + Qdrant + Embedder |

**GET /health — Response:**
```json
{ "status": "ok", "version": "1.0.0", "timestamp": "2025-01-01T00:00:00Z" }
```

**GET /api/v1/health/ready — Response:**
```json
{
  "status": "ready",
  "checks": {
    "postgres": "ok",
    "qdrant": "ok",
    "embedder": "ok"
  }
}
```

---

### 3.2 Authentication (OAuth 2.0 + JWT)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/auth/google/login` | None | Redirect to Google OAuth consent |
| GET | `/api/v1/auth/google/callback` | None | Google OAuth callback handler |
| GET | `/api/v1/auth/github/login` | None | Redirect to GitHub OAuth consent |
| GET | `/api/v1/auth/github/callback` | None | GitHub OAuth callback handler |
| POST | `/api/v1/auth/refresh` | Bearer | Refresh access token |
| POST | `/api/v1/auth/logout` | Bearer | Revoke token / clear session |
| GET | `/api/v1/auth/me` | Bearer | Get current authenticated user |

**GET /api/v1/auth/me — Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "User Name",
  "avatar_url": "https://...",
  "provider": "google",
  "created_at": "2025-01-01T00:00:00Z"
}
```

**POST /api/v1/auth/refresh — Request:**
```json
{ "refresh_token": "eyJ..." }
```

**POST /api/v1/auth/refresh — Response:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

---

### 3.3 Documents

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/v1/documents/upload` | Bearer | Upload one or more documents |
| GET | `/api/v1/documents` | Bearer | List all user documents |
| GET | `/api/v1/documents/{doc_id}` | Bearer | Get document metadata |
| GET | `/api/v1/documents/{doc_id}/status` | Bearer | Get processing pipeline status |
| GET | `/api/v1/documents/{doc_id}/chunks` | Bearer | Get all text chunks for a doc |
| DELETE | `/api/v1/documents/{doc_id}` | Bearer | Delete document + vectors |
| DELETE | `/api/v1/documents` | Bearer | Bulk delete (body: list of IDs) |

**POST /api/v1/documents/upload — Request (multipart/form-data):**
```
files: [file1.pdf, file2.docx]
collection_id: "uuid" (optional)
```

**POST /api/v1/documents/upload — Response:**
```json
{
  "uploaded": [
    {
      "id": "uuid",
      "filename": "Operating Systems.pdf",
      "size_bytes": 2048000,
      "mime_type": "application/pdf",
      "status": "processing",
      "collection_id": "uuid",
      "created_at": "2025-01-01T00:00:00Z"
    }
  ],
  "failed": []
}
```

**GET /api/v1/documents/{doc_id}/status — Response:**
```json
{
  "id": "uuid",
  "filename": "Operating Systems.pdf",
  "status": "completed",
  "pipeline": {
    "parsing": "completed",
    "chunking": "completed",
    "embedding": "completed",
    "indexing": "completed"
  },
  "chunk_count": 142,
  "page_count": 312,
  "completed_at": "2025-01-01T00:05:00Z"
}
```

**Document status enum:** `pending | processing | completed | failed`

---

### 3.4 Collections

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/v1/collections` | Bearer | Create new collection/workspace |
| GET | `/api/v1/collections` | Bearer | List all user collections |
| GET | `/api/v1/collections/{col_id}` | Bearer | Get collection + doc list |
| PATCH | `/api/v1/collections/{col_id}` | Bearer | Update name/description |
| DELETE | `/api/v1/collections/{col_id}` | Bearer | Delete collection (docs optional) |
| POST | `/api/v1/collections/{col_id}/documents` | Bearer | Add existing doc to collection |
| DELETE | `/api/v1/collections/{col_id}/documents/{doc_id}` | Bearer | Remove doc from collection |

**POST /api/v1/collections — Request:**
```json
{
  "name": "Operating Systems Study",
  "description": "OS exam prep materials"
}
```

**POST /api/v1/collections — Response:**
```json
{
  "id": "uuid",
  "name": "Operating Systems Study",
  "description": "OS exam prep materials",
  "document_count": 0,
  "created_at": "2025-01-01T00:00:00Z"
}
```

---

### 3.5 Q&A

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/v1/qa/ask` | Bearer | Open-ended question |
| POST | `/api/v1/qa/mcq` | Bearer | MCQ question with options |
| GET | `/api/v1/qa/sessions` | Bearer | List all QA sessions |
| POST | `/api/v1/qa/sessions` | Bearer | Create new QA session |
| GET | `/api/v1/qa/sessions/{session_id}` | Bearer | Get full session history |
| DELETE | `/api/v1/qa/sessions/{session_id}` | Bearer | Delete session |
| GET | `/api/v1/qa/sessions/{session_id}/messages` | Bearer | Paginated messages |

**POST /api/v1/qa/ask — Request:**
```json
{
  "question": "What is demand paging?",
  "session_id": "uuid",
  "document_ids": ["uuid1", "uuid2"],
  "collection_id": "uuid",
  "llm_provider": "openai",
  "top_k": 5
}
```

**POST /api/v1/qa/ask — Response:**
```json
{
  "message_id": "uuid",
  "question": "What is demand paging?",
  "answer": "Demand paging is a memory management technique where pages are loaded into RAM only when they are actually accessed, rather than loading the entire program at startup.",
  "sources": [
    {
      "document": "Operating Systems.pdf",
      "document_id": "uuid",
      "page": 128,
      "section": "Chapter 9: Virtual Memory",
      "snippet": "Demand paging is a technique where pages are brought into memory only when required by the running process...",
      "score": 0.93
    }
  ],
  "confidence": "high",
  "retrieval_metadata": {
    "chunks_retrieved": 10,
    "chunks_after_rerank": 5,
    "retrieval_strategy": "hybrid_rrf"
  },
  "created_at": "2025-01-01T00:00:00Z"
}
```

**POST /api/v1/qa/mcq — Request:**
```json
{
  "question": "What is demand paging?",
  "options": {
    "A": "A technique where all pages are loaded into memory at once",
    "B": "A method where pages are loaded only when required",
    "C": "A scheduling algorithm",
    "D": "A disk management technique"
  },
  "session_id": "uuid",
  "document_ids": ["uuid1"],
  "collection_id": "uuid",
  "llm_provider": "openai"
}
```

**POST /api/v1/qa/mcq — Response:**
```json
{
  "message_id": "uuid",
  "question": "What is demand paging?",
  "options": {
    "A": "A technique where all pages are loaded into memory at once",
    "B": "A method where pages are loaded only when required",
    "C": "A scheduling algorithm",
    "D": "A disk management technique"
  },
  "selected_option": "B",
  "answer": "A method where pages are loaded only when required.",
  "justification": "The document explicitly states that demand paging brings pages into memory only when accessed by the process, not preloaded. Options A is the opposite, C and D describe unrelated concepts.",
  "option_scores": {
    "A": 0.05,
    "B": 0.93,
    "C": 0.01,
    "D": 0.01
  },
  "sources": [
    {
      "document": "Operating Systems.pdf",
      "document_id": "uuid",
      "page": 128,
      "section": "Chapter 9: Virtual Memory",
      "snippet": "Demand paging is a technique where pages are brought into memory only when required...",
      "score": 0.93
    }
  ],
  "confidence": "high",
  "created_at": "2025-01-01T00:00:00Z"
}
```

**Confidence enum:** `high (>0.85) | medium (0.60–0.85) | low (<0.60) | not_found`

---

## 4. RAG PIPELINE ARCHITECTURE

### 4.1 Document Ingestion Pipeline

```
[File Upload API]
        │
        ▼
[File Validation]
  - MIME check: PDF / DOCX / TXT / MD
  - Max size: 50MB
  - Virus scan placeholder
        │
        ▼
[Parser Selection]  ──→  PDF  → PyMuPDF (fitz)
  (by MIME type)   ──→  DOCX → python-docx
                   ──→  TXT  → direct read
                         │
                         ▼
                  [Extracted Text + Metadata]
                    - raw_text
                    - page_number
                    - section_title (if available)
                    - document_name
                         │
                         ▼
                    [Chunker]
                   Semantic chunking:
                   - target_chunk_size: 512 tokens
                   - overlap: 64 tokens
                   - respect paragraph boundaries
                   - preserve section context in metadata
                         │
                         ▼
                   [Embedder]
                 BAAI/bge-large-en-v1.5
                 - batch_size: 32
                 - normalize_embeddings: True
                 - dim: 1024
                         │
                         ▼
                   [Qdrant Indexer]
                 Collection: per-user namespace
                 Payload per vector:
                   {
                     text, doc_id, doc_name,
                     page, section, chunk_index,
                     user_id, collection_id
                   }
                         │
                         ▼
                  [PostgreSQL Update]
                  document.status = "completed"
                  document.chunk_count = N
```

### 4.2 Query & Retrieval Pipeline

```
[User Question / MCQ]
        │
        ▼
[Query Type Detection]
  - Has "A.", "B.", "C.", "D." → MCQ
  - Else → Open-Ended
        │
        ▼
[Query Embedding]
  BAAI/bge-large-en-v1.5
  query_instruction: "Represent this question for searching relevant passages:"
        │
        ├──────────────────────┐
        ▼                      ▼
[Vector Search]          [BM25 Search]
  Qdrant dense             rank_bm25 over
  top_k=20                 stored chunks
  filter: user_id          top_k=20
  + doc_ids / coll_id
        │                      │
        └──────────┬───────────┘
                   ▼
        [Reciprocal Rank Fusion]
          RRF score = Σ 1/(k + rank_i)
          k = 60 (standard)
          Combined list top_k=10
                   │
                   ▼
           [BGE Reranker]
          BAAI/bge-reranker-large
          Cross-encoder: (query, chunk) → score
          Re-sorted top_k=5
                   │
                   ▼
        [Context Threshold Check]
          max_score < 0.40 → "not found" path
          Else → pass to LLM
                   │
                   ▼
           [LLM Generation]
          (see Section 5 for prompts)
                   │
                   ▼
        [Citation Builder]
          Map LLM answer segments
          back to source chunks
                   │
                   ▼
        [Confidence Scorer]
          high / medium / low / not_found
                   │
                   ▼
        [Structured Response]
          JSON → API → Frontend
```

### 4.3 Chunking Strategy (chunker.py)

```python
# Chunking parameters — production-tuned
CHUNK_SIZE_TOKENS    = 512   # Balanced for bge-large context window
CHUNK_OVERLAP_TOKENS = 64    # Preserves cross-boundary context
MIN_CHUNK_TOKENS     = 50    # Discard fragments
MAX_CHUNK_TOKENS     = 600   # Hard cap before forced split

# Strategy:
# 1. Split by double newline (paragraphs)
# 2. If paragraph > MAX_CHUNK_TOKENS, split by sentence
# 3. Apply sliding window overlap
# 4. Prepend section_title to each chunk text for context enrichment
# Format: "[SECTION: {section}] {chunk_text}"
```

### 4.4 Metadata Schema (per Qdrant vector)

```json
{
  "id": "uuid-v4",
  "vector": [1024 floats],
  "payload": {
    "text": "Demand paging is a technique...",
    "doc_id": "uuid",
    "doc_name": "Operating Systems.pdf",
    "page": 128,
    "section": "Chapter 9: Virtual Memory",
    "chunk_index": 47,
    "char_start": 2048,
    "char_end": 2560,
    "user_id": "uuid",
    "collection_id": "uuid"
  }
}
```

---

## 5. MASTER PROMPTS

### 5.1 Base System Prompt

```
SYSTEM_PROMPT = """
You are an Academic Document Intelligence Assistant. Your purpose is to answer
questions strictly based on the provided document context.

CORE RULES:
1. Answer ONLY from the provided [CONTEXT] below. Do not use any external knowledge.
2. If the answer is not found in the context, respond EXACTLY:
   "I could not find this in the provided documents. Can you share the relevant document?"
3. Never hallucinate, fabricate, or infer beyond what the context explicitly states.
4. Always cite the source document, page number, and section in your answer.
5. Be precise, clear, and academically appropriate in tone.
6. If the context partially answers the question, share what is found and explicitly
   state what is missing.

CITATION FORMAT:
When referencing a source, always include:
- Document name
- Page number (if available)
- Section/Chapter (if available)
- A brief verbatim snippet (max 30 words)

You are a precise academic assistant, not a general-purpose chatbot.
"""
```

---

### 5.2 Open-Ended QA Prompt

```
QA_PROMPT_TEMPLATE = """
{SYSTEM_PROMPT}

[RETRIEVED CONTEXT]
{context_blocks}

[USER QUESTION]
{question}

[INSTRUCTIONS]
Using ONLY the retrieved context above, provide a comprehensive answer.
Structure your response as follows:

ANSWER:
<Your detailed answer here. Be specific and precise.>

REASONING:
<Brief explanation of how you derived this answer from the context.>

SOURCES USED:
<List the specific document(s), page(s), and section(s) you drew from.>

If the context does not contain enough information to answer, say:
"I could not find this in the provided documents. Can you share the relevant document?"

Do NOT speculate. Do NOT use knowledge outside the provided context.
"""
```

**Context block format injected into the prompt:**
```
--- Source 1 ---
Document: Operating Systems.pdf
Page: 128
Section: Chapter 9: Virtual Memory
Relevance Score: 0.93
Content: Demand paging is a technique where pages are brought into memory
only when required by the running process...

--- Source 2 ---
Document: Operating Systems.pdf
Page: 130
Section: Chapter 9: Virtual Memory
Relevance Score: 0.87
Content: The page fault handler is invoked when a process accesses a page
not currently in physical memory...
```

---

### 5.3 MCQ Evaluation Prompt

```
MCQ_PROMPT_TEMPLATE = """
{SYSTEM_PROMPT}

[RETRIEVED CONTEXT]
{context_blocks}

[MCQ QUESTION]
{question}

[OPTIONS]
A. {option_a}
B. {option_b}
C. {option_c}
D. {option_d}

[INSTRUCTIONS]
You must evaluate each option strictly against the retrieved context above.

For each option:
1. Determine if it is supported, contradicted, or unrelated to the context.
2. Assign a confidence score from 0.0 to 1.0 for each option.

Then select the single best answer.

Respond in this EXACT JSON format:
{{
  "selected_option": "<A|B|C|D>",
  "answer": "<text of selected option>",
  "justification": "<Why this option is correct based on context, and why others are wrong>",
  "option_scores": {{
    "A": <float 0-1>,
    "B": <float 0-1>,
    "C": <float 0-1>,
    "D": <float 0-1>
  }},
  "evidence_quote": "<Direct verbatim quote from context supporting the answer, max 50 words>",
  "confidence": "<high|medium|low|not_found>"
}}

If none of the options are supported by the context, set:
"selected_option": "not_found",
"confidence": "not_found",
"justification": "I could not find this in the provided documents..."

Do NOT guess. Base every score on the context only.
"""
```

---

### 5.4 Confidence Scoring Logic

```python
# confidence_builder.py
# Applied AFTER LLM generation, before returning to client

def compute_confidence(top_reranker_score: float, answer_has_quote: bool) -> str:
    """
    Confidence is derived from retrieval quality, not LLM self-report.
    LLM self-reported confidence is used as a secondary signal only.
    """
    if top_reranker_score >= 0.85 and answer_has_quote:
        return "high"
    elif top_reranker_score >= 0.60:
        return "medium"
    elif top_reranker_score >= 0.40:
        return "low"
    else:
        return "not_found"
```

---

### 5.5 Query Type Detection Prompt

```
QUERY_CLASSIFIER_PROMPT = """
Classify the following input as either "open_ended" or "mcq".

MCQ criteria: contains answer options labeled A/B/C/D or 1/2/3/4,
or the structure "which of the following", or a question followed by
distinct answer choices.

Open-ended: any other question or statement.

Respond with ONLY one word: "open_ended" or "mcq"

Input: {query}
"""
```

---

### 5.6 Not-Found Response

```python
NOT_FOUND_RESPONSE = {
    "answer": "I could not find this in the provided documents. "
              "Can you share the relevant document?",
    "sources": [],
    "confidence": "not_found",
    "retrieval_metadata": {
        "chunks_retrieved": 0,
        "retrieval_strategy": "hybrid_rrf"
    }
}
```

---

## 6. OAUTH IMPLEMENTATION

### 6.1 Dependencies (requirements.txt additions)

```
authlib==1.3.0
httpx==0.27.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
```

### 6.2 OAuth Providers Config (config.py)

```python
class Settings(BaseSettings):
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Google OAuth
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/google/callback"

    # GitHub OAuth
    GITHUB_CLIENT_ID: str
    GITHUB_CLIENT_SECRET: str
    GITHUB_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/github/callback"

    # Frontend URL (for post-auth redirect)
    FRONTEND_URL: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
```

### 6.3 OAuth Router (api/v1/auth.py)

```python
from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from app.core.security import create_access_token, create_refresh_token
from app.services.user_service import get_or_create_user

router = APIRouter(prefix="/auth", tags=["auth"])

oauth = OAuth()
oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)
oauth.register(
    name="github",
    client_id=settings.GITHUB_CLIENT_ID,
    client_secret=settings.GITHUB_CLIENT_SECRET,
    access_token_url="https://github.com/login/oauth/access_token",
    authorize_url="https://github.com/login/oauth/authorize",
    api_base_url="https://api.github.com/",
    client_kwargs={"scope": "read:user user:email"},
)

@router.get("/google/login")
async def google_login(request: Request):
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/google/callback")
async def google_callback(request: Request, db=Depends(get_db)):
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get("userinfo")
    user = await get_or_create_user(db, email=user_info["email"],
                                        name=user_info["name"],
                                        avatar_url=user_info.get("picture"),
                                        provider="google")
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    # Redirect to frontend with tokens as query params (or set cookie)
    redirect_url = f"{settings.FRONTEND_URL}/auth/callback"
    redirect_url += f"?access_token={access_token}&refresh_token={refresh_token}"
    return RedirectResponse(redirect_url)

@router.get("/github/login")
async def github_login(request: Request):
    return await oauth.github.authorize_redirect(request, settings.GITHUB_REDIRECT_URI)

@router.get("/github/callback")
async def github_callback(request: Request, db=Depends(get_db)):
    token = await oauth.github.authorize_access_token(request)
    resp = await oauth.github.get("user", token=token)
    profile = resp.json()
    email_resp = await oauth.github.get("user/emails", token=token)
    primary_email = next(
        (e["email"] for e in email_resp.json() if e.get("primary")), None
    )
    user = await get_or_create_user(db, email=primary_email,
                                        name=profile.get("name") or profile["login"],
                                        avatar_url=profile.get("avatar_url"),
                                        provider="github")
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    redirect_url = (f"{settings.FRONTEND_URL}/auth/callback"
                    f"?access_token={access_token}&refresh_token={refresh_token}")
    return RedirectResponse(redirect_url)

@router.get("/me")
async def get_me(current_user=Depends(get_current_user)):
    return current_user

@router.post("/refresh")
async def refresh_token(body: RefreshTokenRequest, db=Depends(get_db)):
    payload = verify_token(body.refresh_token)
    user = await get_user_by_id(db, payload["sub"])
    access_token = create_access_token({"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer", "expires_in": 3600}

@router.post("/logout")
async def logout(current_user=Depends(get_current_user)):
    # Stateless JWT: client discards tokens
    # For refresh token invalidation, add a token blacklist (Redis recommended)
    return {"message": "Logged out successfully"}
```

### 6.4 JWT Security (core/security.py)

```python
from datetime import datetime, timedelta
from jose import JWTError, jwt

def create_access_token(data: dict) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({**data, "exp": expire, "type": "access"},
                      settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_refresh_token(data: dict) -> str:
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return jwt.encode({**data, "exp": expire, "type": "refresh"},
                      settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def verify_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
```

### 6.5 Frontend — OAuth Callback Handler (auth/OAuthCallback.tsx)

```tsx
import { useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { useAuthStore } from "@/store/authStore"

export function OAuthCallback() {
  const navigate = useNavigate()
  const { setTokens } = useAuthStore()

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const accessToken = params.get("access_token")
    const refreshToken = params.get("refresh_token")

    if (accessToken && refreshToken) {
      setTokens({ accessToken, refreshToken })
      navigate("/dashboard", { replace: true })
    } else {
      navigate("/login?error=oauth_failed", { replace: true })
    }
  }, [])

  return (
    <div className="flex h-screen items-center justify-center">
      <p className="text-muted-foreground">Signing you in...</p>
    </div>
  )
}
```

---

## 7. BACKEND IMPLEMENTATION GUIDE

### 7.1 main.py

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.api.v1.router import api_router
from app.config import settings

app = FastAPI(
    title="Academic RAG Platform",
    description="RAG-based document Q&A for academic use",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}
```

### 7.2 RAG Ingestion (rag/pipeline/ingestion.py)

```python
import asyncio
from app.rag.parsers import get_parser
from app.rag.pipeline.chunker import SemanticChunker
from app.rag.pipeline.embedder import BGEEmbedder
from app.rag.pipeline.indexer import QdrantIndexer
from app.db.models.document import Document
from app.db.session import AsyncSessionLocal

class IngestionPipeline:
    def __init__(self):
        self.chunker  = SemanticChunker()
        self.embedder = BGEEmbedder()
        self.indexer  = QdrantIndexer()

    async def run(self, doc_id: str, file_path: str,
                  mime_type: str, user_id: str, collection_id: str | None):
        async with AsyncSessionLocal() as db:
            doc = await db.get(Document, doc_id)
            try:
                doc.status = "processing"
                await db.commit()

                # 1. Parse
                parser  = get_parser(mime_type)
                pages   = parser.parse(file_path)         # List[PageContent]

                # 2. Chunk
                chunks  = self.chunker.chunk(pages)       # List[Chunk]

                # 3. Embed
                texts   = [c.text for c in chunks]
                vectors = self.embedder.encode(texts)     # np.ndarray

                # 4. Index
                await self.indexer.upsert(
                    chunks=chunks,
                    vectors=vectors,
                    doc_id=doc_id,
                    doc_name=doc.filename,
                    user_id=user_id,
                    collection_id=collection_id
                )

                doc.status      = "completed"
                doc.chunk_count = len(chunks)
                await db.commit()

            except Exception as e:
                doc.status       = "failed"
                doc.error_message = str(e)
                await db.commit()
                raise
```

### 7.3 Hybrid Retriever (rag/retrieval/hybrid_retriever.py)

```python
from app.rag.retrieval.vector_retriever import VectorRetriever
from app.rag.retrieval.bm25_retriever import BM25Retriever
from app.rag.retrieval.reranker import BGEReranker

class HybridRetriever:
    def __init__(self):
        self.vector = VectorRetriever()
        self.bm25   = BM25Retriever()
        self.reranker = BGEReranker()
        self.RRF_K  = 60

    def rrf_fusion(self, vector_results, bm25_results, top_k=10):
        scores = {}
        for rank, hit in enumerate(vector_results):
            scores.setdefault(hit.id, 0)
            scores[hit.id] += 1 / (self.RRF_K + rank + 1)
        for rank, hit in enumerate(bm25_results):
            scores.setdefault(hit.id, 0)
            scores[hit.id] += 1 / (self.RRF_K + rank + 1)
        sorted_ids = sorted(scores, key=lambda x: scores[x], reverse=True)
        return sorted_ids[:top_k]

    async def retrieve(self, query: str, user_id: str,
                       doc_ids: list[str] | None = None,
                       collection_id: str | None = None,
                       top_k: int = 5) -> list[dict]:
        # Step 1: Parallel retrieval
        vec_hits  = await self.vector.search(query, user_id, doc_ids, collection_id, k=20)
        bm25_hits = self.bm25.search(query, user_id, doc_ids, collection_id, k=20)

        # Step 2: RRF fusion
        fused_ids = self.rrf_fusion(vec_hits, bm25_hits, top_k=10)

        # Step 3: Rerank
        chunk_map = {h.id: h for h in vec_hits + bm25_hits}
        candidates = [chunk_map[id] for id in fused_ids if id in chunk_map]
        reranked   = self.reranker.rerank(query, candidates, top_k=top_k)

        return reranked
```

### 7.4 LLM Router (rag/generation/llm_router.py)

```python
from openai import AsyncOpenAI
import anthropic
import google.generativeai as genai
from app.config import settings

class LLMRouter:
    def __init__(self):
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.claude_client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        genai.configure(api_key=settings.GEMINI_API_KEY)

    async def complete(self, provider: str, system: str,
                       user: str, max_tokens: int = 1024) -> str:
        if provider == "openai":
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user",   "content": user}
                ],
                max_tokens=max_tokens,
                temperature=0.1        # Low temp for factual grounding
            )
            return response.choices[0].message.content

        elif provider == "claude":
            response = await self.claude_client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": user}]
            )
            return response.content[0].text

        elif provider == "gemini":
            model = genai.GenerativeModel("gemini-1.5-pro")
            response = model.generate_content(f"{system}\n\n{user}")
            return response.text

        raise ValueError(f"Unknown LLM provider: {provider}")
```

---

## 8. FRONTEND IMPLEMENTATION GUIDE — ShadCN + MOTION

### 8.1 ShadCN Setup (components.json)

```json
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "default",
  "rsc": false,
  "tsx": true,
  "tailwind": {
    "config": "tailwind.config.ts",
    "css": "src/index.css",
    "baseColor": "slate",
    "cssVariables": true
  },
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils"
  }
}
```

### 8.2 ShadCN Components to Install

```bash
npx shadcn-ui@latest init
npx shadcn-ui@latest add button card dialog input badge progress
npx shadcn-ui@latest add separator scroll-area toast tooltip skeleton
npx shadcn-ui@latest add tabs sheet dropdown-menu avatar
```

### 8.3 Additional Frontend Dependencies

```json
{
  "dependencies": {
    "@tanstack/react-query": "^5.0.0",
    "axios": "^1.6.0",
    "framer-motion": "^11.0.0",
    "zustand": "^4.5.0",
    "react-dropzone": "^14.0.0",
    "react-router-dom": "^6.22.0",
    "lucide-react": "^0.400.0",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.2.0"
  }
}
```

### 8.4 Global CSS Variables (index.css)

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --card: 0 0% 100%;
    --card-foreground: 222.2 84% 4.9%;
    --primary: 221.2 83.2% 53.3%;       /* Electric indigo */
    --primary-foreground: 210 40% 98%;
    --secondary: 210 40% 96.1%;
    --secondary-foreground: 222.2 47.4% 11.2%;
    --muted: 210 40% 96.1%;
    --muted-foreground: 215.4 16.3% 46.9%;
    --accent: 262 83% 58%;               /* Violet accent */
    --accent-foreground: 210 40% 98%;
    --destructive: 0 84.2% 60.2%;
    --border: 214.3 31.8% 91.4%;
    --radius: 0.625rem;
  }

  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    --card: 222.2 84% 4.9%;
    --primary: 217.2 91.2% 59.8%;
    --accent: 262 83% 68%;
  }
}
```

### 8.5 Framer Motion — Page Transition (components/common/PageTransition.tsx)

```tsx
import { motion, AnimatePresence } from "framer-motion"
import { useLocation } from "react-router-dom"

const pageVariants = {
  initial: { opacity: 0, y: 12 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.28, ease: "easeOut" } },
  exit:    { opacity: 0, y: -8,  transition: { duration: 0.20 } },
}

export function PageTransition({ children }: { children: React.ReactNode }) {
  const location = useLocation()
  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={location.pathname}
        variants={pageVariants}
        initial="initial"
        animate="animate"
        exit="exit"
        className="h-full w-full"
      >
        {children}
      </motion.div>
    </AnimatePresence>
  )
}
```

### 8.6 Document Uploader with Drag-and-Drop + Motion

```tsx
import { useCallback, useState } from "react"
import { useDropzone } from "react-dropzone"
import { motion, AnimatePresence } from "framer-motion"
import { Upload, FileText, CheckCircle2, XCircle } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { useDocuments } from "@/hooks/useDocuments"

const ACCEPTED_TYPES = {
  "application/pdf": [".pdf"],
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
  "text/plain": [".txt"],
  "text/markdown": [".md"],
}

export function DocumentUploader({ collectionId }: { collectionId?: string }) {
  const { uploadDocuments, isUploading } = useDocuments()
  const [uploadProgress, setUploadProgress] = useState<Record<string, number>>({})

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    await uploadDocuments(acceptedFiles, collectionId)
  }, [collectionId])

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: ACCEPTED_TYPES,
    maxSize: 50 * 1024 * 1024,  // 50MB
    multiple: true,
  })

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.97 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
    >
      <div
        {...getRootProps()}
        className={cn(
          "relative border-2 border-dashed rounded-xl p-10 text-center cursor-pointer",
          "transition-all duration-200 ease-out",
          isDragActive && !isDragReject
            ? "border-primary bg-primary/5 scale-[1.01]"
            : "border-border hover:border-primary/50 hover:bg-muted/40",
          isDragReject && "border-destructive bg-destructive/5"
        )}
      >
        <input {...getInputProps()} />
        <motion.div
          animate={isDragActive ? { scale: 1.08, y: -4 } : { scale: 1, y: 0 }}
          transition={{ type: "spring", stiffness: 300, damping: 20 }}
          className="flex flex-col items-center gap-3"
        >
          <div className="rounded-full bg-primary/10 p-4">
            <Upload className="h-8 w-8 text-primary" />
          </div>
          <div>
            <p className="text-base font-medium">
              {isDragActive ? "Release to upload" : "Drop documents here"}
            </p>
            <p className="text-sm text-muted-foreground mt-1">
              PDF, DOCX, TXT, Markdown — up to 50MB each
            </p>
          </div>
          <Button variant="outline" size="sm" className="mt-2">
            Browse files
          </Button>
        </motion.div>
      </div>
    </motion.div>
  )
}
```

### 8.7 AnswerCard with Stagger Animation

```tsx
import { motion } from "framer-motion"
import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { BookOpen, FileText, ChevronRight } from "lucide-react"
import type { QAResponse } from "@/types/qa"

const containerVariants = {
  hidden: {},
  show: { transition: { staggerChildren: 0.08 } },
}
const itemVariants = {
  hidden: { opacity: 0, y: 10 },
  show:   { opacity: 1, y: 0,  transition: { duration: 0.28 } },
}

export function AnswerCard({ response }: { response: QAResponse }) {
  const confidenceColor = {
    high:      "bg-green-100 text-green-800  dark:bg-green-900 dark:text-green-200",
    medium:    "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
    low:       "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
    not_found: "bg-red-100 text-red-800   dark:bg-red-900 dark:text-red-200",
  }[response.confidence]

  return (
    <motion.div variants={containerVariants} initial="hidden" animate="show">
      {/* Answer */}
      <motion.div variants={itemVariants}>
        <Card className="mb-4 border-l-4 border-l-primary">
          <CardHeader className="pb-2 flex-row items-center justify-between">
            <div className="flex items-center gap-2">
              <BookOpen className="h-4 w-4 text-primary" />
              <span className="text-sm font-medium">Answer</span>
            </div>
            <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${confidenceColor}`}>
              {response.confidence}
            </span>
          </CardHeader>
          <CardContent>
            <p className="text-sm leading-relaxed">{response.answer}</p>
          </CardContent>
        </Card>
      </motion.div>

      {/* Citations */}
      {response.sources.length > 0 && (
        <motion.div variants={itemVariants}>
          <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-2">
            Sources
          </p>
          <div className="flex flex-col gap-2">
            {response.sources.map((source, i) => (
              <motion.div key={i} variants={itemVariants}>
                <CitationCard source={source} index={i + 1} />
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}
    </motion.div>
  )
}

function CitationCard({ source, index }: { source: any; index: number }) {
  return (
    <Card className="bg-muted/40 border-none">
      <CardContent className="p-3">
        <div className="flex items-start gap-2">
          <span className="flex-shrink-0 w-5 h-5 rounded-full bg-primary/15 text-primary
                           text-xs flex items-center justify-center font-bold mt-0.5">
            {index}
          </span>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <FileText className="h-3.5 w-3.5 text-muted-foreground flex-shrink-0" />
              <span className="text-xs font-medium truncate">{source.document}</span>
              {source.page && (
                <span className="text-xs text-muted-foreground flex-shrink-0">
                  p.{source.page}
                </span>
              )}
              <span className="ml-auto text-xs text-muted-foreground flex-shrink-0">
                {Math.round(source.score * 100)}% match
              </span>
            </div>
            {source.section && (
              <p className="text-xs text-muted-foreground mb-1">{source.section}</p>
            )}
            <p className="text-xs text-foreground/80 italic leading-relaxed line-clamp-3">
              "{source.snippet}"
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
```

### 8.8 Sidebar with Collapse Animation

```tsx
import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { NavLink } from "react-router-dom"
import { LayoutDashboard, Files, MessageSquare, Library,
         ChevronLeft, ChevronRight } from "lucide-react"
import { cn } from "@/lib/utils"

const NAV_ITEMS = [
  { href: "/dashboard",   icon: LayoutDashboard, label: "Dashboard"   },
  { href: "/documents",   icon: Files,            label: "Documents"   },
  { href: "/ask",         icon: MessageSquare,    label: "Ask"         },
  { href: "/collections", icon: Library,          label: "Collections" },
]

export function Sidebar() {
  const [collapsed, setCollapsed] = useState(false)

  return (
    <motion.aside
      animate={{ width: collapsed ? 64 : 220 }}
      transition={{ type: "spring", stiffness: 300, damping: 30 }}
      className="relative flex flex-col h-screen border-r bg-card py-4 overflow-hidden"
    >
      {/* Logo */}
      <div className="px-4 mb-6 flex items-center gap-2 overflow-hidden">
        <div className="flex-shrink-0 w-7 h-7 rounded-lg bg-primary flex items-center
                        justify-center text-white text-xs font-bold">
          AI
        </div>
        <AnimatePresence>
          {!collapsed && (
            <motion.span
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -8 }}
              className="text-sm font-semibold whitespace-nowrap"
            >
              DocIntel
            </motion.span>
          )}
        </AnimatePresence>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-2 space-y-1">
        {NAV_ITEMS.map(({ href, icon: Icon, label }) => (
          <NavLink key={href} to={href}>
            {({ isActive }) => (
              <div className={cn(
                "flex items-center gap-3 px-2 py-2.5 rounded-lg text-sm font-medium",
                "transition-colors duration-150",
                isActive
                  ? "bg-primary/10 text-primary"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground"
              )}>
                <Icon className="flex-shrink-0 h-4 w-4" />
                <AnimatePresence>
                  {!collapsed && (
                    <motion.span
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      className="whitespace-nowrap"
                    >
                      {label}
                    </motion.span>
                  )}
                </AnimatePresence>
              </div>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Collapse Toggle */}
      <button
        onClick={() => setCollapsed(c => !c)}
        className="absolute -right-3 top-1/2 -translate-y-1/2 w-6 h-6 rounded-full
                   border bg-background shadow-sm flex items-center justify-center
                   hover:bg-muted transition-colors z-10"
      >
        {collapsed
          ? <ChevronRight className="h-3 w-3" />
          : <ChevronLeft  className="h-3 w-3" />}
      </button>
    </motion.aside>
  )
}
```

---

## 9. DOCKER & CONTAINERIZATION

### 9.1 Backend Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# System dependencies for PyMuPDF
RUN apt-get update && apt-get install -y \
    libmupdf-dev \
    libfreetype6-dev \
    libjpeg-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run alembic migrations, then start server
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
```

### 9.2 Frontend Dockerfile

```dockerfile
# Build stage
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Serve stage
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 9.3 Frontend nginx.conf

```nginx
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;

    # SPA routing — send all non-file requests to index.html
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Proxy API to backend
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Proxy docs/swagger
    location /docs {
        proxy_pass http://backend:8000/docs;
    }

    gzip on;
    gzip_types text/plain text/css application/json application/javascript;
}
```

### 9.4 docker-compose.yml (Development)

```yaml
version: "3.9"

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://raguser:ragpass@postgres:5432/ragdb
      - QDRANT_HOST=qdrant
      - QDRANT_PORT=6333
    env_file:
      - .env
    volumes:
      - ./backend:/app          # Hot reload in dev
      - uploads_data:/app/uploads
    depends_on:
      postgres:
        condition: service_healthy
      qdrant:
        condition: service_started
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "5173:80"
    depends_on:
      - backend

  postgres:
    image: postgres:16-alpine
    restart: unless-stopped
    environment:
      POSTGRES_USER: raguser
      POSTGRES_PASSWORD: ragpass
      POSTGRES_DB: ragdb
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./infra/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U raguser -d ragdb"]
      interval: 5s
      timeout: 5s
      retries: 5

  qdrant:
    image: qdrant/qdrant:v1.9.0
    restart: unless-stopped
    ports:
      - "6333:6333"
      - "6334:6334"     # gRPC
    volumes:
      - qdrant_data:/qdrant/storage
    environment:
      QDRANT__SERVICE__GRPC_PORT: 6334

volumes:
  postgres_data:
  qdrant_data:
  uploads_data:
```

### 9.5 docker-compose.prod.yml

```yaml
version: "3.9"

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./infra/nginx/nginx.conf:/etc/nginx/conf.d/default.conf
      - ./infra/nginx/certs:/etc/nginx/certs
    depends_on:
      - backend
      - frontend

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    restart: unless-stopped
    env_file: .env.prod
    volumes:
      - uploads_data:/app/uploads
    depends_on:
      - postgres
      - qdrant

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    restart: unless-stopped

  postgres:
    image: postgres:16-alpine
    restart: unless-stopped
    env_file: .env.prod
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $POSTGRES_USER -d $POSTGRES_DB"]
      interval: 10s
      timeout: 5s
      retries: 5

  qdrant:
    image: qdrant/qdrant:v1.9.0
    restart: unless-stopped
    volumes:
      - qdrant_data:/qdrant/storage

volumes:
  postgres_data:
  qdrant_data:
  uploads_data:
```

---

## 10. ENVIRONMENT VARIABLES

### .env.example

```bash
# ─── Application ───────────────────────────────
SECRET_KEY=your-256-bit-secret-key-here
ENVIRONMENT=development
FRONTEND_URL=http://localhost:5173

# ─── Database ──────────────────────────────────
DATABASE_URL=postgresql+asyncpg://raguser:ragpass@postgres:5432/ragdb
POSTGRES_USER=raguser
POSTGRES_PASSWORD=ragpass
POSTGRES_DB=ragdb

# ─── Qdrant ────────────────────────────────────
QDRANT_HOST=qdrant
QDRANT_PORT=6333
QDRANT_COLLECTION_PREFIX=rag_docs

# ─── Embedding Model ───────────────────────────
EMBEDDING_MODEL=BAAI/bge-large-en-v1.5
RERANKER_MODEL=BAAI/bge-reranker-large
EMBEDDING_BATCH_SIZE=32
EMBEDDING_DEVICE=cpu           # or "cuda" for GPU

# ─── LLM Providers ────────────────────────────
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=AIza...
DEFAULT_LLM_PROVIDER=openai

# ─── OAuth — Google ───────────────────────────
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-...
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback

# ─── OAuth — GitHub ───────────────────────────
GITHUB_CLIENT_ID=Iv1.xxx
GITHUB_CLIENT_SECRET=xxx
GITHUB_REDIRECT_URI=http://localhost:8000/api/v1/auth/github/callback

# ─── JWT ──────────────────────────────────────
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# ─── Upload Limits ────────────────────────────
MAX_UPLOAD_SIZE_MB=50
ALLOWED_EXTENSIONS=pdf,docx,txt,md

# ─── RAG Settings ─────────────────────────────
CHUNK_SIZE_TOKENS=512
CHUNK_OVERLAP_TOKENS=64
RETRIEVAL_TOP_K=5
RETRIEVAL_FETCH_K=20
RRF_K=60
RERANKER_TOP_K=5
MIN_CONFIDENCE_SCORE=0.40
```

---

## 11. DATABASE SCHEMA

### PostgreSQL Tables (Alembic migration)

```sql
-- Users
CREATE TABLE users (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email         VARCHAR(255) UNIQUE NOT NULL,
    name          VARCHAR(255),
    avatar_url    TEXT,
    provider      VARCHAR(50) NOT NULL,   -- 'google' | 'github'
    is_active     BOOLEAN DEFAULT TRUE,
    created_at    TIMESTAMPTZ DEFAULT NOW(),
    updated_at    TIMESTAMPTZ DEFAULT NOW()
);

-- Collections / Workspaces
CREATE TABLE collections (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id       UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name          VARCHAR(255) NOT NULL,
    description   TEXT,
    created_at    TIMESTAMPTZ DEFAULT NOW(),
    updated_at    TIMESTAMPTZ DEFAULT NOW()
);

-- Documents
CREATE TABLE documents (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id       UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    collection_id UUID REFERENCES collections(id) ON DELETE SET NULL,
    filename      VARCHAR(255) NOT NULL,
    original_name VARCHAR(255) NOT NULL,
    mime_type     VARCHAR(100) NOT NULL,
    size_bytes    BIGINT NOT NULL,
    file_path     TEXT NOT NULL,
    status        VARCHAR(50) DEFAULT 'pending',   -- pending|processing|completed|failed
    error_message TEXT,
    page_count    INTEGER,
    chunk_count   INTEGER,
    created_at    TIMESTAMPTZ DEFAULT NOW(),
    updated_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_documents_user_id ON documents(user_id);
CREATE INDEX idx_documents_status  ON documents(status);

-- QA Sessions
CREATE TABLE qa_sessions (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id       UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    collection_id UUID REFERENCES collections(id) ON DELETE SET NULL,
    title         VARCHAR(500),
    created_at    TIMESTAMPTZ DEFAULT NOW(),
    updated_at    TIMESTAMPTZ DEFAULT NOW()
);

-- QA Messages
CREATE TABLE qa_messages (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id       UUID NOT NULL REFERENCES qa_sessions(id) ON DELETE CASCADE,
    role             VARCHAR(20) NOT NULL,          -- 'user' | 'assistant'
    content          TEXT NOT NULL,
    message_type     VARCHAR(20) DEFAULT 'open_ended', -- 'open_ended' | 'mcq'
    sources          JSONB DEFAULT '[]',
    confidence       VARCHAR(20),
    retrieval_meta   JSONB DEFAULT '{}',
    llm_provider     VARCHAR(50),
    created_at       TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_qa_messages_session ON qa_messages(session_id);

-- Session ↔ Document (many-to-many)
CREATE TABLE session_documents (
    session_id  UUID REFERENCES qa_sessions(id)  ON DELETE CASCADE,
    document_id UUID REFERENCES documents(id)     ON DELETE CASCADE,
    PRIMARY KEY (session_id, document_id)
);
```

---

## 12. CODEX FEED SUMMARY

> This section is a condensed directive for feeding to OpenAI Codex / GitHub Copilot Workspace.

---

### CODEX DIRECTIVE — Academic RAG Platform

**You are implementing a production-grade RAG (Retrieval-Augmented Generation) document Q&A platform.**

#### Stack
- **Backend:** Python 3.11, FastAPI, SQLAlchemy async, Alembic, Qdrant, PostgreSQL
- **Frontend:** React 18, TypeScript, Vite, ShadCN/UI, Framer Motion, Zustand, React Query, Axios
- **RAG:** BAAI/bge-large-en-v1.5 (embeddings), BAAI/bge-reranker-large (reranker), Hybrid BM25 + Vector + RRF
- **Auth:** OAuth 2.0 (Google + GitHub) via Authlib, JWT access + refresh tokens
- **Infra:** Docker, Docker Compose, Nginx reverse proxy

#### Critical Constraints
1. All answers must be grounded ONLY in uploaded documents — no external knowledge
2. Every answer must include source citations: `{document, page, section, snippet, score}`
3. If context score < 0.40, return the "not found" response — never hallucinate
4. MCQ responses must include per-option scores and justification JSON
5. Confidence levels: `high (>0.85) | medium (0.60–0.85) | low (<0.60) | not_found`
6. LLM temperature = 0.1 for factual grounding
7. OAuth callback: redirect to frontend `/auth/callback?access_token=X&refresh_token=Y`

#### API Base URL
- Dev: `http://localhost:8000/api/v1`
- Swagger: `http://localhost:8000/docs`

#### Key Endpoints to Implement First (Priority Order)
1. `POST /api/v1/auth/google/login` + `GET /api/v1/auth/google/callback`
2. `GET /api/v1/auth/me` (Bearer JWT)
3. `POST /api/v1/documents/upload` (multipart, triggers async ingestion)
4. `GET /api/v1/documents/{doc_id}/status`
5. `POST /api/v1/qa/ask` (open-ended with citations)
6. `POST /api/v1/qa/mcq` (option scoring + justification)

#### RAG Pipeline Execution Order
```
upload → validate → parse(PyMuPDF/python-docx) → chunk(512tok/64overlap)
       → embed(bge-large) → upsert(qdrant) → update_status(postgres)

query  → embed → parallel(qdrant_vector + bm25) → rrf_fusion(k=60)
       → rerank(bge-reranker) → threshold_check(0.40) → llm(temp=0.1)
       → citation_build → confidence_score → json_response
```

#### Master Prompt Injection Pattern
```python
# Build context string from reranked chunks
context = "\n\n".join([
    f"--- Source {i+1} ---\n"
    f"Document: {c.doc_name}\nPage: {c.page}\nSection: {c.section}\n"
    f"Relevance: {c.score:.2f}\nContent: {c.text}"
    for i, c in enumerate(reranked_chunks)
])
# Inject into QA_PROMPT_TEMPLATE or MCQ_PROMPT_TEMPLATE
prompt = QA_PROMPT_TEMPLATE.format(
    system_prompt=SYSTEM_PROMPT,
    context_blocks=context,
    question=user_question
)
```

#### Frontend Route Map
```
/                   → redirect → /dashboard
/login              → Login.tsx (Google + GitHub OAuth buttons)
/auth/callback      → OAuthCallback.tsx (consume tokens, redirect)
/dashboard          → Dashboard.tsx (stats, recent activity)
/documents          → Documents.tsx (upload + list + status)
/ask                → QASession.tsx (question input + answer + citations)
/collections        → Collections.tsx (workspace management)
```

#### Motion Design Rules
- Page transitions: `opacity 0→1, y 12→0, 280ms easeOut`
- List items: stagger children `80ms` apart
- Upload dropzone: `scale 1→1.01` on drag active
- Sidebar collapse: `spring, stiffness 300, damping 30`
- Answer card: stagger `answer → sources` with `80ms` delay

#### Docker Commands
```bash
# Development
docker-compose up --build

# Production
docker-compose -f docker-compose.prod.yml up -d --build

# Migrations only
docker-compose exec backend alembic upgrade head

# Access Swagger
open http://localhost:8000/docs
```

#### Not implemented in V1 (defer to V2/V3)
- Agentic RAG, Graph RAG, Knowledge Graphs
- Query routing / semantic routing
- Multi-agent systems, RAPTOR, ColBERT
- Redis token blacklist (use stateless JWT for V1)
- Celery async workers (use FastAPI BackgroundTasks for V1)
- Multi-tenancy / team collaboration

---

*End of Spec — Feed this document to Codex in full for best results.*
