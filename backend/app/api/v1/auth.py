from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.config import settings
from backend.app.core.oauth import (
    OAuthProvider,
    clear_oauth_state_cookie,
    generate_oauth_state,
    get_oauth_state_cookie,
    set_oauth_state_cookie,
    validate_oauth_state,
)
from backend.app.db.session import get_db
from backend.app.schemas.auth import (
    OAuthCallbackQuery,
    OAuthLoginRequest,
    User as UserSchema,
    AuthResponse,
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

    state = generate_oauth_state()
    redirect_url = build_google_oauth_login_url(state=state)

    response = JSONResponse({"authorization_url": redirect_url})
    set_oauth_state_cookie(response, state)
    return response


@router.get("/google/callback")
async def google_callback(
    request: Request,
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
        response = JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Missing authorization code"},
        )
        clear_oauth_state_cookie(response)
        return response

    cookie_state = get_oauth_state_cookie(request)
    if not validate_oauth_state(cookie_state, query.state):
        response = JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Invalid OAuth state"},
        )
        clear_oauth_state_cookie(response)
        return response

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
    response = RedirectResponse(url=callback_url, status_code=status.HTTP_302_FOUND)
    clear_oauth_state_cookie(response)
    return response


@router.post("/dev-login", response_model=AuthResponse)
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

    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=UserSchema(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            provider=user.provider,
        ),
    )


@router.get("/me", response_model=UserSchema)
async def me(current_user: User = Depends(get_current_user)) -> UserSchema:
    """Return current authenticated user."""
    return to_user_schema(current_user)