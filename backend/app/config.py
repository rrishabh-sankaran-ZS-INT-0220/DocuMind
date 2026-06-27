from functools import lru_cache

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Central configuration object for the DocuMind backend.
    """

    app_name: str = Field("DocuMind Backend", env="APP_NAME")
    environment: str = Field("development", env="ENVIRONMENT")
    api_v1_prefix: str = "/api/v1"

    # Security / JWT
    secret_key: str = Field("dev-secret-key", env="SECRET_KEY")
    refresh_secret_key: str = Field("dev-refresh-secret-key", env="REFRESH_SECRET_KEY")

    # OAuth (Google)
    google_client_id: str = Field("", env="GOOGLE_CLIENT_ID")
    google_client_secret: str = Field("", env="GOOGLE_CLIENT_SECRET")
    google_redirect_uri: str = Field(
        "http://localhost:8000/api/v1/auth/google/callback",
        env="GOOGLE_REDIRECT_URI",
    )

    # Database connection pieces
    db_user: str = Field("documind", env="DB_USER")
    db_password: str = Field("documind", env="DB_PASSWORD")
    db_host: str = Field("localhost", env="DB_HOST")
    db_port: str = Field("5432", env="DB_PORT")
    db_name: str = Field("documind", env="DB_NAME")

    # Full database URL for async app (asyncpg)
    database_url: str = Field(
        "",
        env="DATABASE_URL",
    )

    # CORS / frontend
    frontend_origin: str = Field("http://localhost:5173", env="FRONTEND_ORIGIN")

    # ------------------------------------------------------------------
    # Retrieval (Qdrant / vector store)
    # ------------------------------------------------------------------
    qdrant_url: str = Field("http://localhost:6333", env="QDRANT_URL")
    qdrant_api_key: str = Field("", env="QDRANT_API_KEY")
    qdrant_collection_name: str = Field(
        "documents_bge_large", env="QDRANT_COLLECTION_NAME"
    )

    # Embedding model used for query encoding
    embedding_model_name: str = Field(
        "BAAI/bge-large-en-v1.5", env="EMBEDDING_MODEL_NAME"
    )

    # Reranker model
    reranker_model_name: str = Field(
        "BAAI/bge-reranker-large", env="RERANKER_MODEL_NAME"
    )

    # Search parameters
    vector_top_k: int = Field(10, ge=1, le=100, env="VECTOR_TOP_K")
    bm25_top_k: int = Field(10, ge=1, le=100, env="BM25_TOP_K")
    rerank_top_k: int = Field(5, ge=1, le=50, env="RERANK_TOP_K")
    rrf_k: int = Field(60, ge=1, env="RRF_K")
    search_timeout: int = Field(30, ge=1, env="SEARCH_TIMEOUT")



    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def async_db_url(self) -> str:
        """Async DB URL for SQLAlchemy+asyncpg."""
        if self.database_url:
            return self.database_url
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def sync_db_url(self) -> str:
        """Sync DB URL for Alembic/psycopg2."""
        return (
            f"postgresql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


@lru_cache
def get_settings() -> "Settings":
    """Return cached settings instance."""
    return Settings()


settings = get_settings()