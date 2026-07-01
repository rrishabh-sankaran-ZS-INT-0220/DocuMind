# Complete Project Blueprint

## 1. Executive Summary

DocuMind is a full-stack, document-first Retrieval-Augmented Generation (RAG) application. Its purpose is to let users upload documents, ingest them into a searchable knowledge layer, and ask grounded questions about their content without needing to manually build a retrieval pipeline.

In simple terms, the product behaves like a private, document-aware AI assistant. A user uploads PDFs, Word documents, plain text files, or markdown files; the backend parses and chunks them; embeddings are generated; those vectors are indexed in Qdrant; and later the system retrieves relevant chunks to answer questions using an LLM through OpenRouter. The application is built as a modular monolith: one backend application, one relational database, one vector database, and one Next.js frontend.

The main users are individual knowledge workers, researchers, students, and teams who want to query their own documents safely and conversationally. The core features are:

- User authentication with Google OAuth and optional development login
- Document upload and storage
- Automatic parsing and chunking
- Embedding generation and vector indexing
- Semantic retrieval with reranking
- Question answering and multiple-choice evaluation
- Collection organization and QA session history

The biggest subsystems are:

- The FastAPI backend API layer
- The SQLAlchemy persistence layer for users, documents, collections, and QA sessions
- The RAG ingestion pipeline for parsing, chunking, embedding, and vector indexing
- The retrieval and reranking subsystem for search
- The prompt-builder and LLM integration layer for answer generation
- The Next.js frontend for chat, authentication, uploads, and session management

---

## 2. Technology Stack

### Programming languages
- Python for the backend and AI pipeline
- TypeScript for the frontend
- SQL for migrations and database schema

### Frameworks and runtimes
- FastAPI for the HTTP API
- Next.js 16 for the frontend application shell
- React 19 for UI components
- Uvicorn as the ASGI server

### Package managers and build tools
- pip for Python dependencies
- npm for frontend dependencies
- ESLint and TypeScript for frontend quality checks
- pytest for backend tests

### UI libraries and styling
- Tailwind CSS for utility-first styling
- Radix UI primitives for dialogs, dropdown menus, and tooltips
- Framer Motion for UI animation
- Lucide React for icons
- Custom component system under the frontend component folders

### State management
- React local state for page and chat state
- React Context for authentication state
- Axios-based API client for network requests

### Backend frameworks
- FastAPI with dependency injection
- Pydantic models for request and response validation
- SQLAlchemy 2.x async ORM
- Alembic for migrations

### Database technologies
- PostgreSQL for relational data
- Qdrant as the vector store for semantic retrieval
- Local filesystem storage for uploaded files

### Authentication mechanisms
- JWT-based session authentication for API calls
- Google OAuth for third-party login
- Optional dev login for local development

### API technologies
- REST APIs over HTTP
- JSON request/response bodies
- Multipart uploads for document files
- CORS enabled for frontend access

### Testing frameworks
- pytest
- pytest-asyncio

### Deployment and infrastructure
- Local-first development setup
- Docker-friendly Qdrant deployment
- No production cloud deployment stack is wired yet

### Logging and monitoring
- Python logging throughout the backend
- No centralized APM or observability stack configured yet

### Important third-party SDKs
- Authlib for OAuth flows
- httpx for HTTP calls
- qdrant-client for vector DB access
- sentence-transformers for embeddings and reranking support
- python-jose and passlib for JWT and password hashing support

Why each is used and where it matters:

- FastAPI: exposes the application routes and uses dependency injection cleanly. Core usage is in backend/app/api/v1 and backend/app/main.py.
- SQLAlchemy: manages persistence and models for users, documents, sessions, and collections. Main usage is in backend/app/db.
- Pydantic: validates requests and serializes responses. Main usage is in backend/app/schemas.
- Qdrant: stores vector embeddings and metadata for retrieval. Main usage is in backend/app/rag/qdrant_client.py and backend/app/rag/retrieval/hybrid_retriever.py.
- Sentence Transformers: generates embeddings. Main usage is in backend/app/rag/embeddings.py.
- OpenRouter: provides LLM completions for generative question-answering. Main usage is in backend/app/services/openrouter_service.py.
- Next.js/React: render the chat experience and authentication flows. Main usage is in frontend/src/app and frontend/src/components.

---

## 3. High-Level Architecture

The system is best described as a modular monolith with clear layering.

Architecture style:
- Modular monolith rather than microservices
- Layered architecture with API, service, persistence, and retrieval layers
- Dependency-injected service abstractions for search and LLM usage

The request flow is:

1. The browser sends a request to the Next.js frontend.
2. The frontend calls the FastAPI backend over REST.
3. The API layer routes the request to an endpoint handler.
4. The handler calls a service layer function.
5. The service layer performs validation, business logic, and persistence operations.
6. For document ingestion, parsing/chunking/embedding/vector indexing occurs.
7. For QA, retrieval and reranking happen first, then an LLM prompt is built and sent to OpenRouter.
8. The response is serialized back through Pydantic and returned to the UI.

Data flow:
- Relational data lives in PostgreSQL.
- Uploaded files live on disk in an uploads tree.
- Vector data lives in Qdrant.
- Authentication tokens move between browser and backend through JWT.

UI-to-backend communication:
- The frontend uses an Axios client configured with the backend base URL.
- Authenticated requests attach a bearer token through the auth context.

Backend-to-database communication:
- Async SQLAlchemy sessions are created through backend/app/db/session.py.
- Each API endpoint depends on get_db to get a session.

Where business logic lives:
- In the services folder, especially document_service.py, rag_pipeline.py, search_service.py, auth_service.py, ingestion.py, and openrouter_service.py.

Where validation occurs:
- Route handlers use FastAPI/Pydantic validation for request payloads.
- Service methods enforce domain rules such as non-empty queries and supported file types.

Where authentication occurs:
- In backend/app/dependencies.py through get_current_user.
- In backend/app/api/v1/auth.py for login and callback handling.

Where authorization occurs:
- Primarily through ownership filters in the database queries.
- Each resource query scopes by current user ID to prevent cross-user access.

How errors propagate:
- API endpoints translate domain exceptions into HTTP responses.
- The ingestion pipeline updates the document status to failed with an error message if processing fails.
- LLM failures are handled gracefully and return a fallback answer or empty results.

Typical request lifecycle:

Browser
↓
Next.js page/component
↓
Axios API client
↓
FastAPI route
↓
Dependency injection (auth + DB)
↓
Service layer
↓
Database or vector store
↓
Response model
↓
Frontend UI update

```text
Browser
  ↓
Frontend (Next.js / React)
  ↓
FastAPI API Layer
  ↓
Services / Business Logic
  ↓
PostgreSQL / Qdrant / File System
  ↓
Response
```

---

## 4. Project Folder Structure

```text
backend/
  app/
    api/v1/
    core/
    db/
      models/
    llm/
    prompts/
    rag/
      parsers/
      pipeline/
      retrieval/
    schemas/
    services/
    config.py
    dependencies.py
    main.py
  alembic/
  tests/
frontend/
  public/
  src/
    app/
    components/
    context/
    hooks/
    lib/
    constants/
```

### Folder responsibilities
- backend/app/api/v1: HTTP endpoints for auth, documents, collections, QA, and health.
- backend/app/core: security, JWT, and OAuth helpers.
- backend/app/db: async database session management and ORM models.
- backend/app/db/models: relational entities such as User, Document, Collection, and QA session models.
- backend/app/rag: all retrieval-augmented generation logic, including parsers, chunking, embeddings, vector store access, and retrieval abstractions.
- backend/app/prompts: prompt templates and prompt building logic.
- backend/app/services: orchestration services that coordinate business flows.
- backend/app/schemas: Pydantic request and response schemas.
- backend/tests: backend unit and integration test coverage.
- frontend/src/app: app-router pages such as login, callback, home, and auth views.
- frontend/src/components: reusable UI building blocks for chat, layout, and messages.
- frontend/src/context: React context providers such as auth-context.
- frontend/src/lib: shared API client and utility logic.

Developers should place new code in the most specific layer that matches its responsibility:
- HTTP concerns in API routes
- Business logic in services
- Persistence concerns in db/models and db/session
- RAG logic in rag
- UI logic in components and app routes

---

## 5. Entry Points

### Backend entry points
- backend/app/main.py is the app factory and creates the FastAPI application.
- backend/app/api/v1/router.py mounts all API routers.
- backend/app/db/session.py initializes the async SQLAlchemy engine and session factory.
- backend/app/config.py loads settings from the environment and project .env file.

Startup behavior:
1. The module imports settings and creates the FastAPI app via create_app().
2. CORS middleware is registered.
3. The API router is mounted under the configured prefix /api/v1.
4. The app object is exported as app for ASGI startup.

Dependency initialization:
- Settings are loaded through pydantic-settings.
- The database engine is created once at import time.
- The session factory is created once at import time.
- Authentication dependencies are resolved per request.

### Frontend entry points
- frontend/src/app/layout.tsx provides the root layout.
- frontend/src/app/page.tsx is the main chat experience page.
- frontend/src/app/login/page.tsx handles the login experience.
- frontend/src/app/auth/callback/page.tsx handles token exchange and redirect after OAuth.

Bootstrap flow:
- The app renders a provider tree that includes auth state.
- The home page uses the auth context to decide whether to render chat or redirect to login.

---

## 6. Module-by-Module Breakdown

### Authentication module
Purpose:
- Authenticate users, issue tokens, and support Google OAuth.

Responsibilities:
- Build Google OAuth redirect URLs
- Exchange an auth code for user info
- Create or update local user records
- Issue access and refresh tokens
- Resolve the current user from a bearer token

Key files:
- backend/app/api/v1/auth.py
- backend/app/services/auth_service.py
- backend/app/core/oauth.py
- backend/app/core/security.py
- backend/app/dependencies.py

Related models:
- User

Sequence:
1. Browser hits /auth/google/login.
2. Backend returns a Google authorization URL.
3. Browser redirects to Google.
4. Google redirects back to /auth/google/callback.
5. Backend exchanges the code, stores/updates the user, and issues JWTs.

### Document and ingestion module
Purpose:
- Accept uploaded files, store them, and prepare them for retrieval.

Responsibilities:
- Validate extensions and size
- Persist uploaded files on disk
- Track document status in PostgreSQL
- Parse supported file types
- Chunk content into retrievable segments
- Generate embeddings
- Upsert chunks into Qdrant

Key files:
- backend/app/api/v1/documents.py
- backend/app/services/document_service.py
- backend/app/services/ingestion.py
- backend/app/rag/parsers/*
- backend/app/rag/pipeline/chunker.py
- backend/app/rag/embeddings.py
- backend/app/rag/qdrant_client.py

Related models:
- Document
- Collection

Sequence:
1. Upload route accepts a file.
2. Document row is created in PostgreSQL.
3. File is stored under uploads/<user_id>/<document_id>/.
4. Ingestion runs in the background.
5. Parsers extract text.
6. Chunks are created and embedded.
7. Vectors are written to Qdrant.
8. The document row is marked ready or failed.

### Search and retrieval module
Purpose:
- Retrieve the most relevant chunks for a user query.

Responsibilities:
- Validate search input
- Build metadata filters
- Query Qdrant using embeddings
- Optionally rerank results
- Return a normalized RetrievedChunk list

Key files:
- backend/app/services/search_service.py
- backend/app/rag/retrieval/base.py
- backend/app/rag/retrieval/hybrid_retriever.py
- backend/app/rag/retrieval/bge_reranker.py

Related models:
- Documents and their vector metadata in Qdrant, plus the relational Document model

Sequence:
1. SearchService validates the query.
2. HybridRetriever embeds the query and searches Qdrant.
3. BGEReranker re-scores results.
4. Results are returned as RetrievedChunk objects.

### Question-answering module
Purpose:
- Turn retrieved evidence into a grounded answer or MCQ evaluation.

Responsibilities:
- Build prompts from retrieved chunks
- Call OpenRouter
- Score the answer confidence
- Return citations and metadata

Key files:
- backend/app/services/rag_pipeline.py
- backend/app/prompts/builder.py
- backend/app/services/openrouter_service.py
- backend/app/schemas/qa.py

Related models:
- QASession, QAMessage, session_documents

Sequence:
1. QA route receives a question.
2. The RAG pipeline runs retrieval.
3. PromptBuilder prepares context-rich prompts.
4. OpenRouter returns a completion.
5. The response includes confidence and citations.

### Collection module
Purpose:
- Group documents into user-managed workspaces.

Responsibilities:
- Create, update, and delete collections
- Associate or disassociate documents
- Scope searches by collection if requested

Key files:
- backend/app/api/v1/collections.py
- backend/app/db/models/collection.py

Related models:
- Collection, Document

### QA session module
Purpose:
- Track chat sessions and preserve message history.

Responsibilities:
- Create sessions
- Attach documents to sessions
- Store messages and metadata
- Provide session retrieval endpoints

Key files:
- backend/app/api/v1/qa.py
- backend/app/db/models/qa_session.py

---

## 7. Routing Analysis

### Backend routes

#### Health
- GET /health/ping
  - Controller: backend/app/api/v1/health.py::ping
  - Service: none
  - Middleware: none
  - Auth: public
  - Response: {"status":"ok"}

#### Authentication
- POST /api/v1/auth/google/login
  - Controller: backend/app/api/v1/auth.py::google_login
  - Service: backend/app/services/auth_service.py::build_google_oauth_login_url
  - Auth: public
  - Request: {"provider":"google"}
  - Response: {"authorization_url": "..."}

- GET /api/v1/auth/google/callback
  - Controller: backend/app/api/v1/auth.py::google_callback
  - Service: exchange_code_and_get_userinfo, upsert_oauth_user, issue_tokens_for_user
  - Auth: public
  - Query params: code, state
  - Response: redirect to frontend callback URL with tokens

- POST /api/v1/auth/dev-login
  - Controller: backend/app/api/v1/auth.py::dev_login
  - Service: upsert_oauth_user, issue_tokens_for_user
  - Auth: public only when dev login is enabled
  - Response: auth token payload and user metadata

- GET /api/v1/auth/me
  - Controller: backend/app/api/v1/auth.py::me
  - Service: get_current_user
  - Auth: required
  - Response: current authenticated user schema

#### Documents
- POST /api/v1/documents/upload
  - Controller: backend/app/api/v1/documents.py::upload_document
  - Service: create_document, ingest_document
  - Auth: required
  - Request: multipart file upload
  - Response: DocumentResponse
  - Side effects: writes file to disk and schedules ingestion

- GET /api/v1/documents
  - Controller: list_user_documents
  - Service: list_documents
  - Auth: required
  - Response: list of documents belonging to the current user

- GET /api/v1/documents/{document_id}
  - Controller: get_user_document
  - Service: get_document
  - Auth: required
  - Response: document details

- GET /api/v1/documents/{document_id}/status
  - Controller: get_document_status
  - Service: get_document
  - Auth: required
  - Response: status, error message, vector metadata

- DELETE /api/v1/documents/{document_id}
  - Controller: delete_user_document
  - Service: delete_document
  - Auth: required
  - Side effects: deletes file and vector records

#### Collections
- POST /api/v1/collections
  - Controller: create_collection
  - Service: none; direct persistence
  - Auth: required

- GET /api/v1/collections
  - Controller: list_collections
  - Auth: required

- GET /api/v1/collections/{collection_id}
  - Controller: get_collection
  - Auth: required

- PATCH /api/v1/collections/{collection_id}
  - Controller: update_collection
  - Auth: required

- DELETE /api/v1/collections/{collection_id}
  - Controller: delete_collection
  - Auth: required

- POST /api/v1/collections/{collection_id}/documents/{document_id}
  - Controller: add_document_to_collection
  - Auth: required

- DELETE /api/v1/collections/{collection_id}/documents/{document_id}
  - Controller: remove_document_from_collection
  - Auth: required

#### QA
- POST /api/v1/qa/sessions
  - Controller: create_session
  - Service: none; direct persistence
  - Auth: required

- GET /api/v1/qa/sessions
  - Controller: list_sessions
  - Auth: required

- GET /api/v1/qa/sessions/{session_id}
  - Controller: get_session
  - Auth: required

- DELETE /api/v1/qa/sessions/{session_id}
  - Controller: delete_session
  - Auth: required

- POST /api/v1/qa/ask
  - Controller: ask_question
  - Service: run_qa_pipeline
  - Auth: required
  - Request: QARequest
  - Response: QAResponse

- POST /api/v1/qa/mcq
  - Controller: mcq_question
  - Service: run_mcq_pipeline
  - Auth: required

### Frontend routing structure
- / is the main chat experience
- /login is the authentication landing page
- /auth/callback handles OAuth callback token receipt
- The app uses the Next.js app router rather than a traditional client-side router library

---

## 8. Database Architecture

### Database type
- PostgreSQL, accessed asynchronously through SQLAlchemy

### ORM
- SQLAlchemy 2.x with async session management

### Core entities
- User: authenticates and owns documents, collections, and sessions
- Collection: user-owned grouping for documents
- Document: uploaded document record, ingestion status, and vector metadata
- QASession: a conversation container for questions and answers
- QAMessage: a single message in a QA session
- session_documents: association table linking sessions to documents

### Relationships
- User to Collection: one-to-many
- User to Document: one-to-many
- User to QASession: one-to-many
- Collection to Document: one-to-many
- QASession to QAMessage: one-to-many
- QASession to Document: many-to-many through session_documents

### Constraints and conventions
- Users are unique by email
- Documents belong to exactly one owner
- Collections belong to exactly one owner
- Documents can optionally belong to a collection
- Sessions are scoped by user

### Migrations
- Alembic manages schema evolution in backend/alembic/versions
- Initial migration is backend/alembic/versions/bbee4f653072_initial_migration.py

ER-style summary:

```text
User 1---* Collection
User 1---* Document
User 1---* QASession
Collection 1---* Document
QASession 1---* QAMessage
QASession *---* Document
```

---

## 9. Data Flow

A common operation is asking a question about uploaded documents.

User Action
↓
UI Component (home chat screen)
↓
API Route (/api/v1/qa/ask)
↓
Controller (ask_question)
↓
Service (run_qa_pipeline)
↓
Validation (non-empty question, supported request model)
↓
Retrieval Layer (SearchService → HybridRetriever → BGEReranker)
↓
Database / Vector Store (PostgreSQL for document metadata, Qdrant for chunk vectors)
↓
Prompt Builder
↓
OpenRouter LLM
↓
Response Model (QAResponse with answer, confidence, score, citations)
↓
UI Update (assistant message shown in the chat viewport)

Detailed execution:
1. The user types a question in the chat composer.
2. The frontend posts the question to /api/v1/qa/ask.
3. The controller validates the payload and calls run_qa_pipeline.
4. The pipeline executes SearchService.search.
5. The retriever embeds the question and searches Qdrant with ownership filters.
6. The reranker re-scores the retrieved chunks.
7. The backend loads document titles from PostgreSQL for citation context.
8. PromptBuilder constructs a context-rich prompt from the retrieved chunks.
9. OpenRouter generates an answer.
10. The response is returned to the frontend and rendered in the conversation history.

---

## 10. Business Logic

The most important business rules are:

- Users can only access documents, collections, and sessions that belong to them.
- Uploaded files must have an allowed extension and MIME type.
- Uploaded files must be under the configured size limit.
- Ingestion is asynchronous and updates document status from uploaded → processing → ready/failed.
- Search queries must not be blank.
- RAG answers should be grounded in retrieved evidence; if no evidence exists, the system returns a not_found response.
- QA sessions can optionally be initialized with specific documents.
- Collections can be used to scope retrieval to a subset of a user's documents.

The domain logic is concentrated in services rather than in route handlers, which keeps the API thin.

---

## 11. Core Files

### backend/app/main.py
- Purpose: app factory and FastAPI initialization
- Dependencies: FastAPI, CORS, API router, settings
- Major classes/functions: create_app
- Side effects: registers middleware and routes
- Callers: ASGI startup and the imported app object

### backend/app/config.py
- Purpose: central environment and configuration loading
- Dependencies: pydantic-settings
- Major classes/functions: Settings, get_settings
- Important configuration: app name, JWT secrets, DB connection, Qdrant URL, OpenRouter settings
- Side effects: reads .env via BaseSettings

### backend/app/db/session.py
- Purpose: create and provide async database sessions
- Dependencies: SQLAlchemy async engine and sessionmaker
- Major functions: get_db
- Side effects: opens and closes sessions per request

### backend/app/services/document_service.py
- Purpose: upload file validation and document lifecycle operations
- Dependencies: UploadFile, SQLAlchemy, Qdrant helpers, filesystem
- Major functions: create_document, list_documents, get_document, delete_document, move_document_to_collection
- Side effects: writes files, deletes files, updates Qdrant metadata

### backend/app/services/ingestion.py
- Purpose: orchestrate the full ingestion pipeline
- Dependencies: parser implementations, chunker, embeddings, Qdrant client, document service paths
- Major functions: ingest_document
- Side effects: parses, chunks, embeds, indexes, and updates document status

### backend/app/services/search_service.py
- Purpose: unify retrieval and reranking
- Dependencies: BaseRetriever, BaseReranker
- Major class: SearchService
- Major method: search(query, user_id, collection_id, document_ids, top_k)
- Return value: list of RetrievedChunk objects

### backend/app/services/rag_pipeline.py
- Purpose: execute the high-level QA and MCQ pipelines
- Dependencies: SearchService, PromptBuilder, OpenRouterService, SQLAlchemy
- Major functions: run_qa_pipeline, run_mcq_pipeline
- Side effects: calls retrieval, prompt construction, and LLM generation

### backend/app/rag/qdrant_client.py
- Purpose: encapsulate vector store access
- Dependencies: qdrant-client
- Major functions: ensure_collection, upsert_document_chunks, delete_document_vectors, update_document_collection
- Side effects: writes and deletes vector data in Qdrant

### backend/app/rag/retrieval/hybrid_retriever.py
- Purpose: perform semantic retrieval from Qdrant
- Dependencies: qdrant-client, embeddings
- Major method: retrieve(...)
- Return value: list of RetrievedChunk objects

### backend/app/rag/retrieval/bge_reranker.py
- Purpose: rerank retrieved chunks using a cross-encoder model
- Dependencies: sentence-transformers
- Major method: rerank(...)
- Side effects: loads the reranker model on first use

### backend/app/prompts/builder.py
- Purpose: build prompts from retrieved chunks and questions
- Dependencies: prompt templates and schemas
- Major methods: build_qa_prompt, build_mcq_prompt

### frontend/src/app/page.tsx
- Purpose: main application page for chat and file upload
- Dependencies: auth context, API client, chat UI components
- Side effects: triggers question and upload flows

### frontend/src/context/auth-context.tsx
- Purpose: maintain authentication state and attach bearer headers
- Dependencies: Axios client
- Side effects: localStorage token persistence and redirect on 401

---

## 12. API Documentation

### Public endpoints
- GET /health/ping
  - Auth: none
  - Status: 200
  - Body: {"status":"ok"}

- POST /api/v1/auth/google/login
  - Auth: none
  - Body: {"provider":"google"}
  - Success: 200 with authorization_url

- GET /api/v1/auth/google/callback
  - Auth: none
  - Query: code, state
  - Success: redirect to frontend callback URL

- POST /api/v1/auth/dev-login
  - Auth: none in dev mode
  - Success: 200 with access/refresh tokens and user payload

### Authenticated endpoints
- GET /api/v1/auth/me
  - Auth: bearer token required
  - Success: 200 with current user

- POST /api/v1/documents/upload
  - Auth: bearer token required
  - Body: multipart file
  - Success: 201 with document metadata
  - Errors: 400 for unsupported file or size

- GET /api/v1/documents
  - Auth: bearer token required
  - Success: 200 with list of documents

- GET /api/v1/documents/{document_id}
  - Auth: bearer token required
  - Success: 200 with document details
  - Errors: 404 when not found

- GET /api/v1/documents/{document_id}/status
  - Auth: bearer token required
  - Success: 200 with status and vector metadata

- DELETE /api/v1/documents/{document_id}
  - Auth: bearer token required
  - Success: 204

- POST /api/v1/collections
  - Auth: bearer token required
  - Body: {"name":"..."}
  - Success: 201

- GET /api/v1/collections
  - Auth: bearer token required
  - Success: 200

- PATCH /api/v1/collections/{collection_id}
  - Auth: bearer token required
  - Success: 200

- DELETE /api/v1/collections/{collection_id}
  - Auth: bearer token required
  - Success: 204

- POST /api/v1/collections/{collection_id}/documents/{document_id}
  - Auth: bearer token required
  - Success: 204

- DELETE /api/v1/collections/{collection_id}/documents/{document_id}
  - Auth: bearer token required
  - Success: 204

- POST /api/v1/qa/ask
  - Auth: bearer token required
  - Body: {"question":"...","top_k":10}
  - Success: 200 with answer, confidence, score, sources

- POST /api/v1/qa/mcq
  - Auth: bearer token required
  - Body: {"question":"...","options":[...]}
  - Success: 200 with selected option and sources

- POST /api/v1/qa/sessions
  - Auth: bearer token required
  - Body: {"title":"...","document_ids":[...]}
  - Success: 201

- GET /api/v1/qa/sessions
  - Auth: bearer token required
  - Success: 200

- GET /api/v1/qa/sessions/{session_id}
  - Auth: bearer token required
  - Success: 200 with session and messages

- DELETE /api/v1/qa/sessions/{session_id}
  - Auth: bearer token required
  - Success: 204

---

## 13. Frontend Architecture

The frontend is a Next.js app-router interface focused on chat and authentication. The main UI is organized into:

- App pages under frontend/src/app
- Reusable chat components under frontend/src/components/chat
- Layout components under frontend/src/components/layout
- Shared UI primitives under frontend/src/components/ui

### Component hierarchy
- Home page renders a fixed sidebar and a main chat panel.
- The chat panel composes:
  - EmptyState for first-run experience
  - MainChatArea as the shell
  - MessageViewport for rendered conversation
  - ChatComposer for question input and uploads
  - TypingIndicator for loading state

### Reusable components
- Button primitives and other shared UI controls live under frontend/src/components/ui.
- Sidebar sections are split into logo, nav, search, chats, collections, and footer.

### Hooks and context
- useAuth provides access to auth state and token management.
- useAutoResizeTextarea is available for composer behavior.

### State management
- Authentication is stored in React context and localStorage.
- Chat state lives in the home page component and is passed down to child components.
- There is no Redux or Zustand store in the current UI architecture.

### Forms and validation
- The login page calls the backend auth endpoints.
- The home page uses local validation before submitting a question or upload.
- File upload uses FormData and multipart request handling.

### API integration
- frontend/src/lib/api.ts defines a shared Axios client.
- Auth tokens are attached by interceptor from the auth context.
- The frontend handles 401 responses by clearing the session and redirecting to login.

---

## 14. UI/UX Design System

The current UI uses a custom, dark-themed design system rather than a heavy component library.

- Tailwind CSS is used for layout and spacing.
- Radix primitives provide accessible building blocks for overlays and menus.
- Custom CSS variables and component classes provide styling consistency.
- The app uses a dark palette with a high-contrast chat UI.

Design-system characteristics:
- Color system: a dark gray theme with accent colors for interactive states
- Typography: simple system-based styling with emphasis on readability
- Spacing: utility-class-based spacing and a compact chat-focused layout
- Responsive strategy: the layout adapts to narrow viewports through flex and width adjustments
- Component reuse: chat cards, composer, and sidebar sections are reused with shared styling
- Accessibility: Radix primitives and semantic buttons improve keyboard and screen-reader usability

---

## 15. Authentication & Authorization

### Login flow
1. The user clicks Continue with Google on the login page.
2. The frontend calls /api/v1/auth/google/login.
3. The backend returns a Google authorization URL.
4. The browser redirects to Google.
5. Google returns to /api/v1/auth/google/callback.
6. The backend exchanges the auth code, creates or updates a user row, issues JWTs, and redirects back to the frontend callback page.

### JWT usage
- Access tokens and refresh tokens are issued as JWTs.
- The access token is used in bearer-authenticated API calls.
- The refresh token is retained in local storage and can be used in future refresh flows if implemented.

### OAuth integration
- Google OAuth is implemented through Authlib and OAuth2 endpoints.
- The login flow is configured through settings in backend/app/config.py.

### Authorization model
- Authorization is not role-based yet; it is ownership-based.
- Every protected resource query is filtered by the current user's ID.
- This is the main mechanism that prevents cross-user access.

### Middleware
- CORS middleware is registered in the FastAPI app.
- Dependency-based auth middleware is applied via get_current_user in the routes.

---

## 16. Environment Configuration

Only the required keys are listed below; no secret values are included.

```text
APP_NAME
ENVIRONMENT
SECRET_KEY
REFRESH_SECRET_KEY
GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET
GOOGLE_REDIRECT_URI
DB_USER
DB_PASSWORD
DB_HOST
DB_PORT
DB_NAME
DATABASE_URL
FRONTEND_ORIGIN
QDRANT_URL
QDRANT_API_KEY
QDRANT_COLLECTION_NAME
EMBEDDING_MODEL_NAME
RERANKER_MODEL_NAME
VECTOR_TOP_K
BM25_TOP_K
RERANK_TOP_K
RRF_K
SEARCH_TIMEOUT
OPENROUTER_API_KEY
OPENROUTER_ENDPOINT
OPENROUTER_MODEL
LLM_TIMEOUT
LLM_TEMPERATURE
ENABLE_DEV_LOGIN
DEV_LOGIN_EMAIL
DEV_LOGIN_NAME
```

What each is used for:
- Application name and environment: identify the service instance and runtime mode.
- JWT secrets: sign and validate access and refresh tokens.
- Google OAuth keys: allow Google login and callback exchange.
- Database settings: connect to PostgreSQL.
- Frontend origin: control CORS and redirect URLs.
- Qdrant settings: locate and configure the vector database.
- Embedding and reranker model names: choose the AI models used for retrieval.
- Search tuning settings: control retrieval depth and reranking behavior.
- OpenRouter settings: connect to the LLM provider.
- Dev login settings: enable local developer authentication when needed.

---

## 17. External Integrations

### Google OAuth
- Purpose: user authentication
- Files: backend/app/api/v1/auth.py, backend/app/services/auth_service.py, backend/app/core/oauth.py
- Initialization: configured from environment variables
- Failure handling: returns HTTP errors and a redirect to login on failure

### OpenRouter
- Purpose: LLM generation for grounded answers
- Files: backend/app/services/openrouter_service.py, backend/app/services/rag_pipeline.py
- Initialization: configured from settings and created lazily
- Failure handling: retries once and falls back to a safe error response

### Qdrant
- Purpose: vector storage and semantic retrieval
- Files: backend/app/rag/qdrant_client.py, backend/app/rag/retrieval/hybrid_retriever.py
- Initialization: collection ensured at ingestion time
- Failure handling: search errors are surfaced as retrieval errors

### PostgreSQL
- Purpose: persistent relational data
- Files: backend/app/db/session.py and all model modules
- Initialization: async engine created once at startup
- Failure handling: request-level database errors propagate to FastAPI

### Sentence Transformers
- Purpose: embedding generation
- Files: backend/app/rag/embeddings.py
- Initialization: model is cached with lru_cache
- Failure handling: failures surface as ingestion or retrieval failures

---

## 18. Error Handling Strategy

The project uses a layered error-handling style.

- Route handlers catch domain-level exceptions and return appropriate HTTP status codes.
- Validation errors are handled by Pydantic/FastAPI.
- Ingestion failures are recorded on the document row rather than crashing the system.
- Search and LLM failures produce either empty results or fallback answers.
- The frontend shows user-facing errors for upload and ask failures.

Examples:
- Unsupported file types return 400 from the upload endpoint.
- Missing or invalid tokens return 401 from the auth dependency.
- Missing documents return 404.
- LLM errors return a safe fallback answer rather than an exception to the user.

Logging is present but not yet centralized; most key steps log with Python logging.

---

## 19. Security Analysis

### What is protected well
- JWT-based auth for protected routes
- Ownership-based authorization for user resources
- CORS configuration for browser-based access
- Input validation through Pydantic models
- File extension and size checks for uploads

### Potential concerns
- There is no explicit rate limiting yet.
- OAuth state is currently generated but not persisted or validated against a server-side session, which is a security weakness for production.
- The app relies on local disk storage for uploaded files without a dedicated storage service, which is simple but less robust.
- There is no evidence of CSRF protection because the application is stateless and uses bearer tokens; this is acceptable for a modern API but should be carefully reviewed in production.
- File upload scanning and malware detection are not present.
- Secrets should be kept out of source control and managed through a secure environment system.

---

## 20. Performance Analysis

### Existing performance patterns
- Embedding models are cached with lru_cache.
- SearchService centralizes retrieval and reranking in a predictable pipeline.
- Qdrant is used to avoid scanning the full document corpus on every query.
- The ingestion pipeline is asynchronous and decoupled from request handling through BackgroundTasks.

### Potential bottlenecks
- The ingestion pipeline is still effectively in-process and may block slower operations in a production deployment.
- Large documents may cause heavy parsing and embedding latency.
- Reranking adds extra cost to each search request.
- Local file storage and synchronous model loading may become bottlenecks under heavier traffic.
- No caching layer or queue worker is present yet.

### Improvement opportunities
- Move ingestion to a background worker queue.
- Add caching for repeated retrieval and prompt context.
- Add pagination for large document and session lists.
- Add metrics for latency and token usage.

---

## 21. Testing

The repository includes backend tests in backend/tests.

Key test files:
- backend/tests/test_chunker.py
- backend/tests/test_documents.py
- backend/tests/test_models.py
- backend/tests/test_openrouter_service.py
- backend/tests/test_parsers.py
- backend/tests/test_prompt_builder.py
- backend/tests/test_search_service.py

Testing style:
- Unit tests for chunking, parsing, prompt generation, and retrieval behavior
- Model tests for schema and ORM expectations
- The repository appears to be moving toward behavior-focused tests rather than UI-level tests

Current testing gaps:
- No frontend E2E suite is evident
- No end-to-end API integration suite is evident
- No full-stack test workflow for the OAuth and upload experience

---

## 22. Design Patterns

The project uses several common design patterns:

- Dependency Injection: FastAPI dependencies and injected service abstractions such as SearchService
- Strategy Pattern: retriever and reranker implementations are swapped through abstract interfaces
- Builder Pattern: PromptBuilder constructs provider-agnostic prompts for QA and MCQ tasks
- Repository-like service layer: services abstract persistence and domain workflows rather than putting everything in the routes
- Singleton-like caching: lru_cache is used for embedding and model reuse
- Middleware pattern: CORS and auth dependencies are applied at request boundaries
- Factory pattern: the app factory in backend/app/main.py creates the FastAPI app instance

---

## 23. Complete Dependency Graph

```text
Frontend (Next.js / React)
  ↓
API Layer (FastAPI routes)
  ↓
Services (auth, document, ingestion, retrieval, QA)
  ↓
Persistence and Vector Stores
  ├── PostgreSQL (users, documents, collections, sessions)
  ├── Qdrant (document chunks and embeddings)
  └── File System (uploaded documents)
```

Cross-module dependencies:
- The frontend depends on the backend for auth, document uploads, and QA operations.
- The document ingestion path depends on parsers, chunking, embeddings, and Qdrant.
- The QA path depends on retrieval, prompt building, and OpenRouter.
- The auth path depends on the database for user persistence and JWT/JWKS-style token handling.

---

## 24. End-to-End Execution Walkthrough

The most important high-level feature is asking a question about uploaded documents.

Execution order:
1. The user opens the home chat page.
2. The frontend validates that the user is authenticated.
3. The user submits a question.
4. The frontend POSTs to /api/v1/qa/ask.
5. The FastAPI route validates the request and calls run_qa_pipeline.
6. SearchService searches the vector index for relevant chunks.
7. The retriever queries Qdrant with metadata filters.
8. The reranker improves the ranking.
9. The prompt builder composes the retrieved context into a prompt.
10. OpenRouter generates an answer.
11. The backend returns answer, confidence, score, and sources.
12. The frontend renders the assistant message and citations.

This is the core execution path that makes the system feel like a private, document-aware AI assistant.

---

## 25. Code Quality Assessment

### Strengths
- Clear separation between API, service, schema, and data layers
- Strong use of abstractions for retrieval and reranking
- Good modularity around the RAG pipeline
- Async SQLAlchemy for scalable database access
- A thoughtful domain model for documents, collections, and QA sessions

### Weaknesses
- The ingestion flow is still largely in-process rather than queued
- The architecture is more “well-structured” than “fully production-hardened”
- Some areas still assume local development conventions rather than cloud-native resilience
- OAuth state handling and production security hardening need work
- The app is not yet fully integrated with observability and monitoring pipelines

### Code smells and technical debt
- Some modules mix persistence, orchestration, and transport concerns too closely
- Background tasks are used directly rather than a dedicated worker system
- Search is currently dense-only and not yet fully hybrid
- There is some duplication in model and schema structure across modules

---

## 26. Refactoring Opportunities

### Highest impact
1. Move ingestion to a durable background worker queue.
2. Introduce a more complete observability layer with structured logging, metrics, and tracing.
3. Harden OAuth callback handling by persisting and validating state.
4. Add rate limiting and abuse protection.
5. Introduce storage abstraction so file uploads can move from local disk to cloud object storage.

### Medium impact
1. Add request-level tracing and correlation IDs.
2. Introduce more explicit repository abstractions for richer testability.
3. Add a proper refresh-token flow and revoke strategy.
4. Add pagination and filtering for large result sets.
5. Add a caching layer for repeated retrieval and repeated document lookups.

### Developer experience improvements
1. Add a full local dev compose file for PostgreSQL, Qdrant, and the backend/frontend services.
2. Add a more complete test harness for frontend and API integration.
3. Add a Makefile or task runner for common operations.
4. Add API contract tests to keep frontend and backend aligned.

---

## 27. Developer Onboarding Guide

If a new developer joins today, this is the best way to start:

1. Read the backend/app/main.py and backend/app/api/v1/router.py files first to understand how the app boots.
2. Read backend/app/config.py to understand runtime configuration.
3. Read backend/app/api/v1/documents.py and backend/app/services/ingestion.py to understand the core document workflow.
4. Read backend/app/services/search_service.py and backend/app/rag/retrieval/* to understand retrieval.
5. Read backend/app/services/rag_pipeline.py and backend/app/prompts/builder.py to understand QA generation.
6. Read frontend/src/app/page.tsx and frontend/src/context/auth-context.tsx to understand the UI flow.
7. Run the backend and frontend locally with PostgreSQL and Qdrant available.

Typical workflow:
- Start the backend.
- Start the frontend.
- Sign in using Google or dev login.
- Upload a document.
- Wait for ingestion to complete.
- Ask a question and inspect the returned citations.

Common debugging tips:
- Check the document status endpoint for ingestion problems.
- Verify Qdrant connectivity when searches return no results.
- Verify OpenRouter configuration when answers fail to generate.
- Verify JWT header formatting when requests are rejected as unauthorized.

---

## 28. Overall Mental Model

The mental model for DocuMind is simple: it is a private, document-aware copilot built as a modular monolith.

All the important pieces fit together like this:
- The frontend captures user intent and renders the experience.
- The backend exposes a clean REST API for documents, collections, auth, and QA.
- The document pipeline turns uploaded files into searchable evidence.
- The retrieval pipeline finds the most relevant chunks.
- The LLM layer turns those chunks into an answer with citations.
- PostgreSQL stores business data, Qdrant stores vector evidence, and the filesystem stores raw uploads.

The architecture philosophy is to keep each concern in a clear layer: API, services, data, and retrieval. That separation is the project’s biggest strength and the main reason it is easier to understand and extend than a monolithic script-based prototype.

The critical modules are:
- the ingestion pipeline
- the search service
- the QA pipeline
- the authentication layer
- the document and session persistence models

The biggest architectural strengths are modularity, clear layering, and the presence of explicit abstractions for retrieval and prompt building. The biggest areas for future improvement are production hardening, asynchronous job processing, stronger observability, and more robust security and storage patterns.
