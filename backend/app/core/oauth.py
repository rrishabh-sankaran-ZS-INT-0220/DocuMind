import hmac
import secrets
from enum import Enum
from typing import Any

from authlib.integrations.httpx_client import OAuth2Client
from fastapi import Request, Response

from backend.app.config import settings


class OAuthProvider(str, Enum):
    GOOGLE = "google"
    GITHUB = "github"
    DEVELOPMENT = "development"


# Google OAuth2 / OIDC endpoints
GOOGLE_AUTHORIZATION_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_ENDPOINT = "https://openidconnect.googleapis.com/v1/userinfo"

OAUTH_STATE_COOKIE_NAME = "oauth_state"
OAUTH_STATE_TTL_SECONDS = 600


def generate_oauth_state() -> str:
    """Create a cryptographically random state token for OAuth CSRF protection."""
    return secrets.token_urlsafe(32)


def set_oauth_state_cookie(response: Response, state: str, ttl_seconds: int = OAUTH_STATE_TTL_SECONDS) -> None:
    """Persist the state token in an HTTP-only, Secure, SameSite=Lax cookie."""
    response.set_cookie(
        key=OAUTH_STATE_COOKIE_NAME,
        value=state,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=ttl_seconds,
    )


def get_oauth_state_cookie(request: Request) -> str | None:
    """Read the state token from the incoming request cookies."""
    return request.cookies.get(OAUTH_STATE_COOKIE_NAME)


def clear_oauth_state_cookie(response: Response) -> None:
    """Remove the state cookie from the client response."""
    response.delete_cookie(
        key=OAUTH_STATE_COOKIE_NAME,
        httponly=True,
        secure=True,
        samesite="lax",
    )


def validate_oauth_state(cookie_state: str | None, query_state: str | None) -> bool:
    """Compare the state value using a constant-time comparison."""
    if not cookie_state or not query_state:
        return False
    return hmac.compare_digest(cookie_state, query_state)


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