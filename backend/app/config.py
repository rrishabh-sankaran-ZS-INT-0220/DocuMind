from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]

print(PROJECT_ROOT)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        case_sensitive=True,
        extra="ignore",
    )

    # ------------------------------------------------------------------
    # Application
    # ------------------------------------------------------------------
    app_name: str = Field(default="DocuMind Backend", alias="APP_NAME")
    environment: str = Field(default="development", alias="ENVIRONMENT")
    api_v1_prefix: str = "/api/v1"

    # Development-only auth features
    enable_dev_login: bool = Field(
        default=False,
        alias="ENABLE_DEV_LOGIN",
    )
    dev_login_email: str = Field(
        default="developer@documind.dev",
        alias="DEV_LOGIN_EMAIL",
    )
    dev_login_name: str = Field(
        default="Developer",
        alias="DEV_LOGIN_NAME",
    )

    # ------------------------------------------------------------------
    # Security / JWT
    # ------------------------------------------------------------------
    secret_key: str = Field(default="dev-secret-key", alias="SECRET_KEY")
    refresh_secret_key: str = Field(
        default="dev-refresh-secret-key",
        alias="REFRESH_SECRET_KEY",
    )

    # ------------------------------------------------------------------
    # Google OAuth
    # ------------------------------------------------------------------
    google_client_id: str = Field(default="", alias="GOOGLE_CLIENT_ID")
    google_client_secret: str = Field(default="", alias="GOOGLE_CLIENT_SECRET")
    google_redirect_uri: str = Field(
        default="http://localhost:8000/api/v1/auth/google/callback",
        alias="GOOGLE_REDIRECT_URI",
    )

    # ------------------------------------------------------------------
    # Database
    # ------------------------------------------------------------------
    db_user: str = Field(default="documind", alias="DB_USER")
    db_password: str = Field(default="documind", alias="DB_PASSWORD")
    db_host: str = Field(default="localhost", alias="DB_HOST")
    db_port: str = Field(default="5432", alias="DB_PORT")
    db_name: str = Field(default="documind", alias="DB_NAME")

    database_url: str = Field(default="", alias="DATABASE_URL")

    # ------------------------------------------------------------------
    # Frontend / CORS
    # ------------------------------------------------------------------
    frontend_origin: str = Field(
        default="http://localhost:5173",
        alias="FRONTEND_ORIGIN",
    )

    # ------------------------------------------------------------------
    # Qdrant
    # ------------------------------------------------------------------
    qdrant_url: str = Field(
        default="http://localhost:6333",
        alias="QDRANT_URL",
    )

    redis_url: str = Field(
        default="redis://localhost:6379/0",
        alias="REDIS_URL",
    )

    qa_rate_limit_requests: int = Field(
        default=10,
        alias="QA_RATE_LIMIT_REQUESTS",
    )

    qa_rate_limit_window_seconds: int = Field(
        default=60,
        alias="QA_RATE_LIMIT_WINDOW_SECONDS",
    )

    upload_rate_limit_requests: int = Field(
        default=5,
        alias="UPLOAD_RATE_LIMIT_REQUESTS",
    )

    upload_rate_limit_window_seconds: int = Field(
        default=60,
        alias="UPLOAD_RATE_LIMIT_WINDOW_SECONDS",
    )

    qdrant_api_key: str = Field(
        default="",
        alias="QDRANT_API_KEY",
    )

    qdrant_collection_name: str = Field(
        default="documents_bge_large",
        alias="QDRANT_COLLECTION_NAME",
    )

    # ------------------------------------------------------------------
    # Embeddings / Retrieval
    # ------------------------------------------------------------------
    embedding_model_name: str = Field(
        default="BAAI/bge-large-en-v1.5",
        alias="EMBEDDING_MODEL_NAME",
    )

    reranker_model_name: str = Field(
        default="BAAI/bge-reranker-large",
        alias="RERANKER_MODEL_NAME",
    )

    vector_top_k: int = Field(
        default=10,
        ge=1,
        le=100,
        alias="VECTOR_TOP_K",
    )

    bm25_top_k: int = Field(
        default=10,
        ge=1,
        le=100,
        alias="BM25_TOP_K",
    )

    rerank_top_k: int = Field(
        default=5,
        ge=1,
        le=50,
        alias="RERANK_TOP_K",
    )

    rrf_k: int = Field(
        default=60,
        ge=1,
        alias="RRF_K",
    )

    search_timeout: int = Field(
        default=30,
        ge=1,
        alias="SEARCH_TIMEOUT",
    )

    # ------------------------------------------------------------------
    # OpenRouter
    # ------------------------------------------------------------------
    openrouter_api_key: str = Field(
        default="",
        alias="OPENROUTER_API_KEY",
    )

    openrouter_endpoint: str = Field(
        default="https://openrouter.ai/api/v1/chat/completions",
        alias="OPENROUTER_ENDPOINT",
    )

    openrouter_model: str = Field(
        default="anthropic/claude-3.5-haiku",
        alias="OPENROUTER_MODEL",
    )

    llm_timeout: float = Field(
        default=60.0,
        alias="LLM_TIMEOUT",
    )

    llm_temperature: float = Field(
        default=0.1,
        alias="LLM_TEMPERATURE",
    )

    # ------------------------------------------------------------------
    # Computed database URLs
    # ------------------------------------------------------------------
    @property
    def async_db_url(self) -> str:
        """Async SQLAlchemy database URL."""
        # Prefer DATABASE_URL if provided
        if self.database_url:
            return self.database_url

        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def sync_db_url(self) -> str:
        """Synchronous SQLAlchemy database URL for Alembic."""
        # Prefer DATABASE_URL if provided
        if self.database_url:
            return (
                self.database_url
                .replace(
                    "postgresql+asyncpg://",
                    "postgresql+psycopg2://",
                )
            )

        return (
            f"postgresql+psycopg2://"
            f"{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}"
            f"/{self.db_name}"
        )

@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()