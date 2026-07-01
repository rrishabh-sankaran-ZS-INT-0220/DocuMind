from typing import Any, Tuple
from urllib.parse import urlencode

import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.config import settings
from backend.app.core.oauth import (
    OAuthProvider,
    get_google_oauth_client,
    parse_oauth_userinfo,
    GOOGLE_AUTHORIZATION_ENDPOINT,
    GOOGLE_TOKEN_ENDPOINT,
    GOOGLE_USERINFO_ENDPOINT,
)
from backend.app.core.security import create_access_token, create_refresh_token
from backend.app.db.models.user import User


def build_google_oauth_login_url(state: str | None = None) -> str:
    """Build Google OAuth authorization URL."""
    query = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "include_granted_scopes": "true",
    }
    if state:
        query["state"] = state
    return f"{GOOGLE_AUTHORIZATION_ENDPOINT}?{urlencode(query)}"


def exchange_code_and_get_userinfo(code: str) -> dict[str, Any]:
    """Exchange authorization code for tokens and fetch Google userinfo.

    Uses Authlib's OAuth2Client for the code -> token exchange, then performs
    a plain HTTPX request to the userinfo endpoint with a Bearer token.
    """
    client = get_google_oauth_client()

    # Exchange authorization code for token (OAuth2 token)
    token = client.fetch_token(
        GOOGLE_TOKEN_ENDPOINT,
        code=code,
        grant_type="authorization_code",
    )

    # Authlib's OAuth2Client for HTTPX does not accept `token=` in .get().
    # Instead, we call the userinfo endpoint via httpx with a Bearer token.
    access_token = token.get("access_token")
    if not access_token:
        raise RuntimeError("Google token response did not contain access_token")

    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    with httpx.Client() as http_client:
        resp = http_client.get(GOOGLE_USERINFO_ENDPOINT, headers=headers)
        resp.raise_for_status()
        data = resp.json()

    # Normalize provider-specific userinfo into our common shape
    return parse_oauth_userinfo(OAuthProvider.GOOGLE, data)


async def upsert_oauth_user(
    db: AsyncSession,
    provider: OAuthProvider,
    email: str,
    full_name: str | None = None,
) -> User:
    """Find or create a user based on OAuth identity."""
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        user = User(email=email, full_name=full_name, provider=provider.value)
        db.add(user)
        await db.commit()
        await db.refresh(user)
    else:
        updated = False
        if user.provider != provider.value:
            user.provider = provider.value
            updated = True
        if full_name is not None and user.full_name != full_name:
            user.full_name = full_name
            updated = True
        if updated:
            await db.commit()
            await db.refresh(user)
    return user


def issue_tokens_for_user(user: User) -> Tuple[str, str]:
    """Create access and refresh tokens for a given user."""
    payload: dict[str, Any] = {
        "sub": str(user.id),
        "email": user.email,
    }
    access = create_access_token(payload)
    refresh = create_refresh_token(payload)
    return access, refresh