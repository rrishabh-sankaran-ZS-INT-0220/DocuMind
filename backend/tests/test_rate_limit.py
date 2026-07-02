import pytest
from fastapi import HTTPException, status

from backend.app.core.rate_limit import build_rate_limiter


@pytest.mark.asyncio
async def test_build_rate_limiter_raises_429_on_limit_exceeded(monkeypatch):
    class DummyLimiter:
        async def __call__(self, request, response):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later.",
            )

    monkeypatch.setattr(
        "backend.app.core.rate_limit.RateLimiter",
        lambda *args, **kwargs: DummyLimiter(),
    )
    monkeypatch.setattr(
        "backend.app.core.rate_limit.get_current_user",
        lambda *args, **kwargs: type("User", (), {"id": "user-123"})(),
    )

    dependency = build_rate_limiter(limit=1, window_seconds=60, limiter_name="qa")

    class DummyRequest:
        app = type("App", (), {"state": type("State", (), {"rate_limiters": {"qa": object()}})()})()

    with pytest.raises(HTTPException) as exc_info:
        await dependency(request=DummyRequest(), current_user=type("User", (), {"id": "user-123"})())

    assert exc_info.value.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    assert exc_info.value.detail == "Rate limit exceeded. Please try again later."
