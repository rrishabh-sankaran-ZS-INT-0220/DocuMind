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