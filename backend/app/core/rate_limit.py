from fastapi import Depends, HTTPException, Request, Response
from fastapi_limiter.depends import RateLimiter

from backend.app.db.models import User
from backend.app.dependencies import get_current_user


async def rate_limit_callback(request: Request, response: Response):
    raise HTTPException(
        status_code=429,
        detail="Rate limit exceeded. Please try again later.",
    )


def build_rate_limiter(limit: int, window_seconds: int, limiter_name: str):
    async def dependency(
        request: Request,
        current_user: User = Depends(get_current_user),
    ) -> None:
        rate_limiter = request.app.state.rate_limiters.get(limiter_name)
        if rate_limiter is None:
            raise HTTPException(status_code=500, detail="Rate limiter is not initialized")

        async def identifier(req: Request) -> str:
            return f"user:{current_user.id}"

        limiter_dependency = RateLimiter(
            limiter=rate_limiter,
            identifier=identifier,
            callback=rate_limit_callback,
        )
        await limiter_dependency(request, Response())

    return dependency
