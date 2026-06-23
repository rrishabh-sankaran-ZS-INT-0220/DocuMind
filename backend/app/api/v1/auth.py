from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.core.oauth import OAuthProvider
from backend.app.schemas.auth import OAuthCallbackQuery, OAuthLoginRequest, Token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/google/login", response_model=dict)
async def google_login(payload: OAuthLoginRequest) -> dict:
    """Initiate Google OAuth login.

    TODO: Implement Authlib redirect URL generation.
    """

    if payload.provider.lower() != OAuthProvider.GOOGLE.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid provider")

    return {"message": "Google OAuth login not yet implemented"}


@router.get("/google/callback", response_model=Token)
async def google_callback(query: OAuthCallbackQuery = Depends()) -> Token:
    """Handle Google OAuth callback and issue JWT tokens.

    TODO: Exchange code for tokens, fetch user info, upsert user, issue JWT.
    """

    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Google OAuth callback not yet implemented")


@router.get("/me", response_model=dict)
async def me() -> dict:
    """Return current user info (placeholder)."""

    return {"message": "Current user endpoint not yet implemented"}
