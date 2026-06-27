# DocuMind Architecture

## Overview

DocuMind is a RAG (Retrieval-Augmented Generation) application with a layered backend architecture. The backend follows a clean separation of concerns: database models → services → API routes, with dedicated abstractions for the retrieval pipeline.

## Directory Layout

```
backend/
  app/
    api/v1/          # HTTP routes (auth, documents, collections, qa)
    core/            # JWT security, OAuth helpers
    db/              # Async SQLAlchemy engine, session, models
    rag/             # Domain-specific RAG abstractions
      parsers/       # PDF, DOCX, TXT, MD parsers
      pipeline/      # Chunking pipeline
      retrieval/     # BASE + HybridRetriever + BGEReranker
      embeddings.py  # Embedding model wrapper
      qdrant_client.py
    services/        # Business logic (auth, document, ingestion, search, rag_pipeline)
    schemas/         # Pydantic request/response models
  tests/             # Unit/integration tests
  alembic/           # Database migrations
```

## Search Architecture

The central retrieval abstraction is `SearchService`. It orchestrates search without knowing about LLMs, prompts, or QA.

```
                     ┌──────────────────────┐
                     │     SearchService     │
                     │   (orchestrator)      │
                     └───────┬──────┬───────┘
                             │      │
                    ┌────────▼┐ ┌───▼────────┐
                    │  Base   │ │   Base     │
                    │Retriever│ │  Reranker  │
                    │ (ABC)   │ │  (ABC)     │
                    └───┬─────┘ └────┬──────┘
                        │            │
              ┌─────────▼──┐   ┌─────▼─────┐
              │  Hybrid    │   │     BGE    │
              │  Retriever │   │  Reranker  │
              │  (Qdrant)  │   │ (CrossEnc) │
              └────────────┘   └───────────┘
```

### SearchService Responsibilities

- **Validate** input (reject empty queries)
- **Invoke** the configured retriever
- **Invoke** the configured reranker (skip if no chunks retrieved)
- **Return** `list[RetrievedChunk]` (never builds prompts or calls LLMs)
- **Log** retrieval latency, reranking latency, total latency, chunk counts

### Dependency Injection

`SearchService` receives two abstractions via constructor injection:

```python
service = SearchService(
    retriever=HybridRetriever(),   # implements BaseRetriever
    reranker=BGEReranker(),        # implements BaseReranker
)
```

Both are swappable without modifying `SearchService`. Future implementations may include `VectorRetriever`, `BM25Retriever`, `ElasticRetriever`, `ColBERTRetriever`, `CohereReranker`, or `NoOpReranker`.

## Retrieval Lifecycle

```
1. search(query, user_id, collection_id, document_ids, top_k)
       │
       ▼
2. Validate query (non-empty)
       │
       ▼
3. HybridRetriever.retrieve(query, user_id, collection_id, document_ids, top_k)
       │  - Embeds query using BAAI/bge-large-en-v1.5
       │  - Searches Qdrant with payload filters
       │  - Returns oversampled list[RetrievedChunk]
       ▼
4. BGEReranker.rerank(query, chunks, top_k)
       │  - Cross-encoder rescores each chunk
       │  - Returns top_k re-ranked chunks
       ▼
5. Return reranked list[RetrievedChunk]
```

## Configuration

All retrieval parameters are centralized in `config.py`:

| Setting | Default | Description |
|---|---|---|
| `qdrant_url` | `http://localhost:6333` | Qdrant server URL |
| `qdrant_collection_name` | `documents_bge_large` | Default Qdrant collection |
| `embedding_model_name` | `BAAI/bge-large-en-v1.5` | Query embedding model |
| `reranker_model_name` | `BAAI/bge-reranker-large` | Cross-encoder reranker |
| `vector_top_k` | `10` | Dense retrieval oversample |
| `bm25_top_k` | `10` | Sparse retrieval (future) |
| `rerank_top_k` | `5` | Final reranked count |
| `rrf_k` | `60` | Fusion constant (future) |
| `search_timeout` | `30` | Qdrant query timeout (s) |

## Domain Exceptions

| Exception | When raised |
|---|---|
| `EmptyQueryError` | Query is empty or whitespace |
| `RetrieverUnavailableError` | Vector store unreachable |
| `RerankerUnavailableError` | Reranker model failed to load/predict |
| `SearchTimeoutError` | Search exceeded timeout |
| `SearchError` | General search failure |

## Request Flow: QA Pipeline

```
Client POST /api/v1/qa/ask
       │
       ▼
qa.py → run_qa_pipeline()
       │
       ▼
SearchService.search()       ← Uses HybridRetriever + BGEReranker
       │
       ▼
result → prompt builder → OpenRouter → answer
```

The QA pipeline consumes `SearchService` but `SearchService` has no dependency on QA.

## Remaining Technical Debt

- User ID is not stored in Qdrant payload — `owner_id` filter is defined but won't match until added at upsert time
- Ingestion is in-process (BackgroundTasks), no durable worker
- No vector cleanup on document delete
- No hybrid search (only dense leg active)