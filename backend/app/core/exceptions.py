import logging
from typing import Any

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

logger = logging.getLogger(__name__)


class AppException(Exception):
    def __init__(self, message: str, status_code: int = 500) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


async def http_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None)
    route = request.url.path
    user = getattr(request.state, "user", None)
    logger.exception(
        "unhandled_exception",
        extra={
            "request_id": request_id,
            "route": route,
            "user": str(user) if user is not None else None,
            "error": exc.message,
        },
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message, "request_id": request_id},
    )


async def request_validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None)
    logger.warning(
        "request_validation_error",
        extra={
            "request_id": request_id,
            "route": request.url.path,
            "errors": exc.errors(),
        },
    )
    return JSONResponse(
        status_code=422,
        content={"error": "validation_error", "request_id": request_id},
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None)
    route = request.url.path
    user = getattr(request.state, "user", None)
    logger.exception(
        "unhandled_exception",
        extra={
            "request_id": request_id,
            "route": route,
            "user": str(user) if user is not None else None,
            "error": str(exc),
        },
    )
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "internal_server_error", "request_id": request_id},
    )
