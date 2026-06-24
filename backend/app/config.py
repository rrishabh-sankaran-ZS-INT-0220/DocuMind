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