from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pyrate_limiter import Duration, Limiter, Rate, RedisBucket
from redis import asyncio as aioredis

from backend.app.api.v1.router import api_router
from backend.app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = aioredis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)
    app.state.redis = redis
    app.state.rate_limiters = {
        "qa": Limiter(
            [Rate(settings.qa_rate_limit_requests, Duration.SECOND * settings.qa_rate_limit_window_seconds)],
            bucket_class=RedisBucket,
            bucket_kwargs={"redis": redis, "bucket_key": "qa-rate-limit"},
        ),
        "upload": Limiter(
            [Rate(settings.upload_rate_limit_requests, Duration.SECOND * settings.upload_rate_limit_window_seconds)],
            bucket_class=RedisBucket,
            bucket_kwargs={"redis": redis, "bucket_key": "upload-rate-limit"},
        ),
    }
    yield
    await redis.close()


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, lifespan=lifespan)

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_origin],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # API routes
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    return app


app = create_app()
