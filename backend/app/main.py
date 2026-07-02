import json
import logging
import uuid
from contextlib import asynccontextmanager
from contextvars import ContextVar
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pyrate_limiter import Duration, Limiter, Rate, RedisBucket
from redis import asyncio as aioredis

from backend.app.api.v1.router import api_router
from backend.app.config import settings
from backend.app.core.exceptions import (
    AppException,
    http_exception_handler,
    request_validation_exception_handler,
    unhandled_exception_handler,
)

REQUEST_ID_CONTEXT: ContextVar[str | None] = ContextVar("request_id", default=None)


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        request_id = REQUEST_ID_CONTEXT.get()
        if request_id:
            payload["request_id"] = request_id

        for key, value in record.__dict__.items():
            if key in {"name", "msg", "args", "levelname", "levelno", "pathname", "filename", "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName", "created", "msecs", "relativeCreated", "thread", "threadName", "processName", "process", "message", "asctime"}:
                continue
            payload[key] = value

        return json.dumps(payload)


def configure_logging() -> None:
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)


async def request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    token = REQUEST_ID_CONTEXT.set(request_id)
    request.state.request_id = request_id
    try:
        response = await call_next(request)
    except Exception as exc:
        handler = request.app.exception_handlers.get(type(exc)) or request.app.exception_handlers.get(Exception)
        if handler is None:
            raise
        response = await handler(request, exc)
    finally:
        REQUEST_ID_CONTEXT.reset(token)

    response.headers["X-Request-ID"] = request_id
    return response


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
    configure_logging()
    app = FastAPI(title=settings.app_name, lifespan=lifespan)

    app.middleware("http")(request_id_middleware)

    app.add_exception_handler(AppException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

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
