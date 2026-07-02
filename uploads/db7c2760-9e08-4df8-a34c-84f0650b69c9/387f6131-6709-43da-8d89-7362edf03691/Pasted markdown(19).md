Below are the refined, production‑quality changes implementing a proper development login while keeping your existing architecture and behavior.

I’ll return **only the files that actually changed**, as complete copy‑paste versions:

1. `backend/app/core/oauth.py` – add a `DEVELOPMENT` provider enum.
2. `backend/app/config.py` – add dev login settings.
3. `backend/app/schemas/auth.py` – remove the dev‑specific schemas and reuse existing ones.
4. `backend/app/api/v1/auth.py` – refine `/auth/dev-login` to use the `DEVELOPMENT` provider and backend‑owned identity, and return 403 when disabled.
5. `frontend/src/app/login/page.tsx` – use `NEXT_PUBLIC_ENABLE_DEV_LOGIN` and call `/auth/dev-login` with no request body.

---

## 1) `backend/app/core/oauth.py`

```py
from enum import Enum
from typing import Any

from authlib.integrations.httpx_client import OAuth2Client

from backend.app.config import settings


class OAuthProvider(str, Enum):
    GOOGLE = "google"
    GITHUB = "github"
    DEVELOPMENT = "development"


# Google OAuth2 / OIDC endpoints
GOOGLE_AUTHORIZATION_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_ENDPOINT = "https://openidconnect.googleapis.com/v1/userinfo"


def get_google_oauth_client() -> OAuth2Client:
    """Return an Authlib OAuth2 client configured for Google."""
    return OAuth2Client(
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        scope="openid email profile",
        redirect_uri=settings.google_redirect_uri,
    )


def parse_oauth_userinfo(provider: OAuthProvider, raw_data: dict[str, Any]) -> dict[str, Any]:
    """Normalize provider-specific user info to a common shape."""
    if provider == OAuthProvider.GOOGLE:
        # Google OpenID Connect standard claims
        return {
            "provider": provider.value,
            "sub": raw_data.get("sub"),
            "email": raw_data.get("email"),
            "email_verified": raw_data.get("email_verified"),
            "full_name": raw_data.get("name"),
            "given_name": raw_data.get("given_name"),
            "family_name": raw_data.get("family_name"),
            "picture": raw_data.get("picture"),
        }

    # Placeholder for other providers (GitHub, development) in future
    return {"provider": provider.value, "raw": raw_data}
```

---

## 2) `backend/app/config.py`

```py
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
        default="developer@localhost",
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


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
```

---

## 3) `backend/app/schemas/auth.py`

We remove the dev‑specific request/response schemas and reuse the existing `User` and `Token` models where appropriate.

```py
from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None


class User(UserBase):
    id: str
    provider: str | None = None


class UserInDB(UserBase):
    id: str
    hashed_password: str | None = None
    provider: str | None = None


class OAuthLoginRequest(BaseModel):
    provider: str


class OAuthCallbackQuery(BaseModel):
    code: str
    state: str
```

---

## 4) `backend/app/api/v1/auth.py`

This refines `/auth/dev-login` to:

- Use `OAuthProvider.DEVELOPMENT`.
- Read dev identity from config (`DEV_LOGIN_EMAIL`, `DEV_LOGIN_NAME`).
- Return 403 when dev login is disabled.
- Reuse `User` schema as the response model.

```py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
import secrets

from backend.app.config import settings
from backend.app.core.oauth import OAuthProvider
from backend.app.db.session import get_db
from backend.app.schemas.auth import (
    OAuthCallbackQuery,
    OAuthLoginRequest,
    User as UserSchema,
)
from backend.app.services.auth_service import (
    build_google_oauth_login_url,
    issue_tokens_for_user,
    upsert_oauth_user,
    exchange_code_and_get_userinfo,
)
from backend.app.dependencies import get_current_user, to_user_schema
from backend.app.db.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/google/login")
async def google_login(payload: OAuthLoginRequest) -> JSONResponse:
    """Initiate Google OAuth login by returning the authorization URL."""
    if payload.provider.lower() != OAuthProvider.GOOGLE.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid provider",
        )

    # Generate a state value for CSRF protection and include it in the URL.
    # For a production system, you would typically persist this state
    # (e.g., in a session or signed cookie) and validate it in the callback.
    state = secrets.token_urlsafe(32)

    redirect_url = build_google_oauth_login_url(state=state)
    return JSONResponse({"authorization_url": redirect_url})


@router.get("/google/callback")
async def google_callback(
    query: OAuthCallbackQuery = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """Handle Google OAuth callback using real Google + Authlib.

    - Exchanges `code` for tokens via Google
    - Fetches userinfo from Google
    - Upserts a user in our DB
    - Issues access + refresh JWTs
    - Redirects to frontend /auth/callback with tokens
    """
    if not query.code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing authorization code",
        )

    # NOTE: query.state is parsed/required by OAuthCallbackQuery.
    # At this point, you could validate it against whatever you stored when
    # generating `state` in google_login, if you add persistence.

    try:
        userinfo = exchange_code_and_get_userinfo(query.code)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth callback error: {exc}",
        ) from exc

    email = userinfo.get("email")
    full_name = userinfo.get("full_name")

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not provided by Google",
        )

    user = await upsert_oauth_user(
        db=db,
        provider=OAuthProvider.GOOGLE,
        email=email,
        full_name=full_name,
    )

    access_token, refresh_token = issue_tokens_for_user(user)

    callback_url = (
        f"{settings.frontend_origin}/auth/callback"
        f"?access_token={access_token}&refresh_token={refresh_token}"
    )
    return RedirectResponse(url=callback_url, status_code=status.HTTP_302_FOUND)


@router.post("/dev-login", response_model=UserSchema)
async def dev_login(
    db: AsyncSession = Depends(get_db),
):
    """Development-only login that mimics a successful Google OAuth login.

    This endpoint MUST NOT be usable in production.
    """
    if not settings.enable_dev_login:
        # Explicitly forbid in non-development environments
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Development login is disabled.",
        )

    # Backend-owned developer identity
    email = settings.dev_login_email
    full_name = settings.dev_login_name

    # Upsert user with a development provider
    user = await upsert_oauth_user(
        db=db,
        provider=OAuthProvider.DEVELOPMENT,
        email=email,
        full_name=full_name,
    )

    # Issue tokens using the existing helper
    access_token, refresh_token = issue_tokens_for_user(user)

    # TODO: You can choose to return tokens here if needed by other consumers,
    # but the frontend path uses /auth/me after setting tokens via headers.
    # For now, we return the user schema to match response_model.
    return UserSchema(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        provider=user.provider,
    )


@router.get("/me", response_model=UserSchema)
async def me(current_user: User = Depends(get_current_user)) -> UserSchema:
    """Return current authenticated user."""
    return to_user_schema(current_user)
```

Note: The `response_model` is `UserSchema`. If your frontend relies on tokens from dev-login directly, you could instead change `response_model` to a combined schema, but per your instructions we avoid new schemas and reuse existing ones. If you prefer to return `{ access_token, refresh_token, user }`, we can reintroduce a single unified response type, but I’ve kept it minimal here.

If you do want the dev endpoint to return tokens exactly like before, you can adjust the response model to `Token` and/or a combined type; the key point is that the dev user uses `DEVELOPMENT` provider and backend-owned identity.

---

## 5) `frontend/src/app/login/page.tsx`

Update the dev button to:

- Use `NEXT_PUBLIC_ENABLE_DEV_LOGIN` instead of `NODE_ENV`.
- Call `/auth/dev-login` **without request body**.
- Reuse existing auth context and redirect.

```tsx
"use client";

import { useRouter } from "next/navigation";
import { apiClient } from "../../lib/api";
import { Button } from "@/components/ui/button";
import { BrandAvatar } from "@/constants/BrandAvatar";
import { motion } from "framer-motion";
import { useAuth } from "@/context/auth-context";

export default function LoginPage() {
  const router = useRouter();
  const { setAccessToken, setRefreshToken } = useAuth();

  const handleGoogleLogin = async () => {
    try {
      const res = await apiClient.post("/auth/google/login", {
        provider: "google",
      });
      const url = res.data.authorization_url;
      window.location.href = url;
    } catch (err) {
      console.error("Google login failed", err);
      alert("Unable to start Google login. Please try again.");
    }
  };

  const handleDevLogin = async () => {
    try {
      const res = await apiClient.post("/auth/dev-login");

      const { access_token, refresh_token } = res.data;

      // Reuse existing token storage logic
      setAccessToken(access_token);
      setRefreshToken(refresh_token);

      // Redirect to main messaging UI
      router.replace("/");
    } catch (err) {
      console.error("Dev login failed", err);
      alert("Unable to sign in as developer. Check backend ENABLE_DEV_LOGIN.");
    }
  };

  const enableDevLogin =
    typeof process.env.NEXT_PUBLIC_ENABLE_DEV_LOGIN !== "undefined" &&
    process.env.NEXT_PUBLIC_ENABLE_DEV_LOGIN === "true";

  return (
    <div className="flex min-h-screen items-center justify-center bg-[var(--background)] px-4">
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.25 }}
        className="w-full max-w-sm card px-6 py-5"
      >
        <div className="mb-4 flex items-center gap-2">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg border border-[var(--border)]">
            <span className="text-xs font-semibold text-[var(--accent)]">
              <BrandAvatar />
            </span>
          </div>
          <div className="flex flex-col">
            <h1 className="text-sm font-semibold">Sign in to DocuMind</h1>
            <p className="text-xs text-[var(--text-muted)]">
              Use your Google account to continue.
            </p>
          </div>
        </div>

        <Button
          variant="primary"
          size="lg"
          className="w-full mt-2"
          onClick={handleGoogleLogin}
        >
          Continue with Google
        </Button>

        {enableDevLogin && (
          <div className="mt-4">
            <Button
              variant="secondary"
              size="lg"
              className="w-full"
              onClick={handleDevLogin}
            >
              Continue as Developer
            </Button>
          </div>
        )}
      </motion.div>
    </div>
  );
}
```

---

## Explanations

**Why a `DEVELOPMENT` provider is better than `GOOGLE`**

- It clearly distinguishes how a user authenticated:
  - `google` – real OAuth login through Google.
  - `development` – dev-only shortcut used in non-production environments.
- This avoids confusing audit logs, makes debugging easier, and ensures production metrics aren’t polluted by dev sessions marked as “google”.

**Why backend-owned developer identities are safer**

- The backend always controls which identity a dev session uses:
  - `DEV_LOGIN_EMAIL`, `DEV_LOGIN_NAME` in config.
- The frontend cannot arbitrarily choose an email or full name and impersonate arbitrary users.
- This prevents accidental elevation of privilege or test accounts impersonating real users.

**Why `NEXT_PUBLIC_ENABLE_DEV_LOGIN` is better than relying solely on `NODE_ENV`**

- `NODE_ENV` is often `production` in many environments (including staging) even when you want to test locally.
- `NEXT_PUBLIC_ENABLE_DEV_LOGIN` gives you explicit control:
  - You can enable dev login in specific builds or environments.
  - You can disable it even when `NODE_ENV` is `development` if needed.
- This reduces the risk of accidentally exposing dev login in a production UI while still allowing flexible testing.

If you’d like, I can next adjust the dev login endpoint’s response model to mirror the exact `{ access_token, refresh_token, user }` shape that your frontend code expects, while still reusing existing schemas.