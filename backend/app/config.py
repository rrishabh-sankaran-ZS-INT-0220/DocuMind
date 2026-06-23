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

    # Database
    database_url: str = Field(
        "postgresql+asyncpg://documind:documind@localhost:5432/documind",
        env="DATABASE_URL",
    )

    # CORS / frontend
    frontend_origin: str = Field("http://localhost:5173", env="FRONTEND_ORIGIN")

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache
def get_settings() -> "Settings":
    """Return cached settings instance."""

    return Settings()


settings = get_settings()
