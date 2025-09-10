from __future__ import annotations

from typing import Any, Tuple

from .utils import (
    HTTPException,
    status,
    PydanticValidationError,
    RequestValidationError,
    IntegrityError,
    DBAPIError,
    OperationalError,
    NoResultFound,
    _is_asyncpg_constraint_error,
    _stringify_exc,
    _format_validation,
)
from .exceptions import TigrblError
from .mappings import (
    _HTTP_TO_RPC,
    _RPC_TO_HTTP,
    ERROR_MESSAGES,
    HTTP_ERROR_MESSAGES,
)


def http_exc_to_rpc(exc: HTTPException) -> tuple[int, str, Any | None]:
    """Convert HTTPException → (rpc_code, message, data)."""
    code = _HTTP_TO_RPC.get(exc.status_code, -32603)
    detail = exc.detail
    if isinstance(detail, (dict, list)):
        return code, ERROR_MESSAGES.get(code, "Unknown error"), detail
    msg = getattr(exc, "rpc_message", None) or (
        detail if isinstance(detail, str) else None
    )
    if not msg:
        msg = ERROR_MESSAGES.get(
            code, HTTP_ERROR_MESSAGES.get(exc.status_code, "Unknown error")
        )
    data = getattr(exc, "rpc_data", None)
    return code, msg, data


def rpc_error_to_http(
    rpc_code: int, message: str | None = None, data: Any | None = None
) -> HTTPException:
    """Convert JSON-RPC error code (and optional message/data) → HTTPException."""
    http_status = _RPC_TO_HTTP.get(rpc_code, 500)
    msg = (
        message
        or HTTP_ERROR_MESSAGES.get(http_status)
        or ERROR_MESSAGES.get(rpc_code, "Unknown error")
    )
    http_exc = HTTPException(status_code=http_status, detail=msg)
    setattr(http_exc, "rpc_code", rpc_code)
    setattr(http_exc, "rpc_message", msg)
    setattr(http_exc, "rpc_data", data)
    return http_exc


def _http_exc_to_rpc(exc: HTTPException) -> tuple[int, str, Any | None]:
    """Alias for :func:`http_exc_to_rpc` to preserve older import paths."""
    return http_exc_to_rpc(exc)


def _rpc_error_to_http(
    rpc_code: int, message: str | None = None, data: Any | None = None
) -> HTTPException:
    """Alias for :func:`rpc_error_to_http` to preserve older import paths."""
    return rpc_error_to_http(rpc_code, message, data)


def _classify_exception(
    exc: BaseException,
) -> Tuple[int, str | dict | list, Any | None]:
    """
    Return (http_status, detail_or_message, data) suitable for HTTPException and JSON-RPC mapping.
    `detail_or_message` may be a string OR a structured dict/list (validation).
    """
    # 0) Typed Tigrbl errors
    if isinstance(exc, TigrblError):
        status_code = getattr(exc, "status", 400) or 400
        details = getattr(exc, "details", None)
        if isinstance(details, (dict, list)):
            return status_code, details, details
        return status_code, str(exc) or exc.code, None

    # 1) Pass-through HTTPException preserving detail
    if isinstance(exc, HTTPException):
        return exc.status_code, exc.detail, getattr(exc, "rpc_data", None)

    # 2) Validation errors → 422 with structured data
    if (PydanticValidationError is not None) and isinstance(
        exc, PydanticValidationError
    ):
        return (
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            HTTP_ERROR_MESSAGES.get(422, "Validation failed"),
            _format_validation(exc),
        )
    if (RequestValidationError is not None) and isinstance(exc, RequestValidationError):
        return (
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            HTTP_ERROR_MESSAGES.get(422, "Validation failed"),
            _format_validation(exc),
        )

    # 3) Common client errors
    if isinstance(exc, (ValueError, TypeError, KeyError)):
        return status.HTTP_400_BAD_REQUEST, _stringify_exc(exc), None
    if isinstance(exc, PermissionError):
        return status.HTTP_403_FORBIDDEN, _stringify_exc(exc), None
    if isinstance(exc, NotImplementedError):
        return status.HTTP_501_NOT_IMPLEMENTED, _stringify_exc(exc), None
    if isinstance(exc, TimeoutError):
        return status.HTTP_504_GATEWAY_TIMEOUT, _stringify_exc(exc), None

    # 4) ORM/DB mapping
    if (NoResultFound is not None) and isinstance(exc, NoResultFound):
        return status.HTTP_404_NOT_FOUND, "Resource not found", None

    if _is_asyncpg_constraint_error(exc):
        return status.HTTP_409_CONFLICT, _stringify_exc(exc), None

    if (IntegrityError is not None) and isinstance(exc, IntegrityError):
        msg = _stringify_exc(exc)
        lower_msg = msg.lower()
        if "not null constraint" in lower_msg or "check constraint" in lower_msg:
            return status.HTTP_422_UNPROCESSABLE_ENTITY, msg, None
        return status.HTTP_409_CONFLICT, msg, None

    if (OperationalError is not None) and isinstance(exc, OperationalError):
        return status.HTTP_503_SERVICE_UNAVAILABLE, _stringify_exc(exc), None

    if (DBAPIError is not None) and isinstance(exc, DBAPIError):
        return status.HTTP_500_INTERNAL_SERVER_ERROR, _stringify_exc(exc), None

    # 5) Fallback
    return status.HTTP_500_INTERNAL_SERVER_ERROR, _stringify_exc(exc), None


def create_standardized_error(exc: BaseException) -> HTTPException:
    """
    Normalize any exception → HTTPException with attached RPC context:
      • .rpc_code
      • .rpc_message
      • .rpc_data
    """
    http_status, detail_or_message, data = _classify_exception(exc)
    rpc_code = _HTTP_TO_RPC.get(http_status, -32603)
    if isinstance(detail_or_message, (dict, list)):
        http_detail = detail_or_message
        rpc_message = ERROR_MESSAGES.get(
            rpc_code, HTTP_ERROR_MESSAGES.get(http_status, "Unknown error")
        )
    else:
        http_detail = detail_or_message
        rpc_message = detail_or_message or ERROR_MESSAGES.get(
            rpc_code, HTTP_ERROR_MESSAGES.get(http_status, "Unknown error")
        )
    http_exc = HTTPException(status_code=http_status, detail=http_detail)
    setattr(http_exc, "rpc_code", rpc_code)
    setattr(http_exc, "rpc_message", rpc_message)
    setattr(http_exc, "rpc_data", data)
    return http_exc


def create_standardized_error_from_status(
    http_status: int,
    message: str | None = None,
    *,
    rpc_code: int | None = None,
    data: Any | None = None,
) -> tuple[HTTPException, int, str]:
    """Explicit constructor used by code paths that already decided on an HTTP status."""
    if rpc_code is None:
        rpc_code = _HTTP_TO_RPC.get(http_status, -32603)
    if message is None:
        http_message = HTTP_ERROR_MESSAGES.get(http_status) or ERROR_MESSAGES.get(
            rpc_code, "Unknown error"
        )
        rpc_message = ERROR_MESSAGES.get(rpc_code) or HTTP_ERROR_MESSAGES.get(
            http_status, "Unknown error"
        )
    else:
        http_message = rpc_message = message
    http_exc = HTTPException(status_code=http_status, detail=http_message)
    setattr(http_exc, "rpc_code", rpc_code)
    setattr(http_exc, "rpc_message", rpc_message)
    setattr(http_exc, "rpc_data", data)
    return http_exc, rpc_code, rpc_message


def to_rpc_error_payload(exc: HTTPException) -> dict:
    """Produce a JSON-RPC error object from an HTTPException (with or without rpc_* attrs)."""
    code, msg, data = http_exc_to_rpc(exc)
    payload = {"code": code, "message": msg}
    if data is not None:
        payload["data"] = data
    else:
        if isinstance(exc.detail, (dict, list)):
            payload["data"] = exc.detail
    return payload


__all__ = [
    "http_exc_to_rpc",
    "rpc_error_to_http",
    "_http_exc_to_rpc",
    "_rpc_error_to_http",
    "create_standardized_error",
    "create_standardized_error_from_status",
    "to_rpc_error_payload",
]
