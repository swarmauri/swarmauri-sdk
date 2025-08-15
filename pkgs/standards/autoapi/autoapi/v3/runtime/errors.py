# autoapi/v3/runtime/errors.py
from __future__ import annotations

from typing import Any, Optional, Iterable, Tuple
import logging

logger = logging.getLogger(__name__)

# Prefer FastAPI HTTPException/status; fall back to Starlette; finally a tiny shim.
try:  # FastAPI present
    from fastapi import HTTPException, status
except Exception:  # pragma: no cover
    try:  # Starlette present
        from starlette.exceptions import HTTPException  # type: ignore
        from starlette import status  # type: ignore
    except Exception:  # pragma: no cover

        class HTTPException(Exception):  # minimal shim
            def __init__(
                self,
                status_code: int,
                detail: Any = None,
                headers: Optional[dict] = None,
            ) -> None:
                super().__init__(detail)
                self.status_code = status_code
                self.detail = detail
                self.headers = headers

        class _Status:
            HTTP_400_BAD_REQUEST = 400
            HTTP_401_UNAUTHORIZED = 401
            HTTP_403_FORBIDDEN = 403
            HTTP_404_NOT_FOUND = 404
            HTTP_409_CONFLICT = 409
            HTTP_422_UNPROCESSABLE_ENTITY = 422
            HTTP_500_INTERNAL_SERVER_ERROR = 500
            HTTP_501_NOT_IMPLEMENTED = 501
            HTTP_503_SERVICE_UNAVAILABLE = 503
            HTTP_504_GATEWAY_TIMEOUT = 504

        status = _Status()  # type: ignore


# Optional imports – code must run even if these packages aren’t installed.
try:
    from pydantic import ValidationError as PydanticValidationError  # v2
except Exception:  # pragma: no cover
    PydanticValidationError = None  # type: ignore

try:
    from fastapi.exceptions import (
        RequestValidationError,
    )  # emitted by FastAPI input validation
except Exception:  # pragma: no cover
    RequestValidationError = None  # type: ignore

try:
    # SQLAlchemy v1/v2 exception sets
    from sqlalchemy.exc import IntegrityError, DBAPIError, OperationalError
    from sqlalchemy.orm.exc import NoResultFound  # type: ignore
except Exception:  # pragma: no cover
    IntegrityError = DBAPIError = OperationalError = NoResultFound = None  # type: ignore


# Detect asyncpg constraint errors without importing asyncpg (optional dep).
_ASYNCPG_CONSTRAINT_NAMES = {
    "UniqueViolationError",
    "ForeignKeyViolationError",
    "NotNullViolationError",
    "CheckViolationError",
    "ExclusionViolationError",
}


def _is_asyncpg_constraint_error(exc: BaseException) -> bool:
    cls = type(exc)
    return (cls.__module__ or "").startswith("asyncpg") and (
        cls.__name__ in _ASYNCPG_CONSTRAINT_NAMES
    )


# ───────────────────── Centralized Error Mappings ────────────────────────────

# HTTP → JSON-RPC code map
_HTTP_TO_RPC: dict[int, int] = {
    400: -32602,  # Bad Request -> Invalid params
    401: -32001,  # Unauthorized -> Authentication required
    403: -32002,  # Forbidden -> Insufficient permissions
    404: -32003,  # Not Found -> Resource not found
    409: -32004,  # Conflict -> Resource conflict
    422: -32602,  # Unprocessable Entity -> Invalid params
    500: -32603,  # Internal Server Error -> Internal error
    501: -32603,
    503: -32603,
    504: -32603,
}

# JSON-RPC → HTTP status map
_RPC_TO_HTTP: dict[int, int] = {
    # Standard JSON-RPC errors
    -32700: 400,  # Parse error -> Bad Request
    -32600: 400,  # Invalid Request -> Bad Request
    -32601: 404,  # Method not found -> Not Found
    -32602: 400,  # Invalid params -> Bad Request
    -32603: 500,  # Internal error -> Internal Server Error
    # Application-specific errors
    -32001: 401,  # Authentication required -> Unauthorized
    -32002: 403,  # Insufficient permissions -> Forbidden
    -32003: 404,  # Resource not found -> Not Found
    -32004: 409,  # Resource conflict -> Conflict
}

# Standardized error messages
ERROR_MESSAGES: dict[int, str] = {
    # Standard JSON-RPC errors
    -32700: "Parse error",
    -32600: "Invalid Request",
    -32601: "Method not found",
    -32602: "Invalid params",
    -32603: "Internal error",
    # Application-specific errors
    -32001: "Authentication required",
    -32002: "Insufficient permissions",
    -32003: "Resource not found",
    -32004: "Resource conflict",
    # Legacy application-specific errors (kept for backward compatibility)
    -32000: "Server error",
    -32099: "Duplicate key constraint violation",
    -32098: "Data constraint violation",
    -32097: "Foreign key constraint violation",
    -32096: "Authentication required",
    -32095: "Authorization failed",
    -32094: "Resource not found",
    -32093: "Validation error",
    -32092: "Transaction failed",
}

# HTTP status code → standardized message
HTTP_ERROR_MESSAGES: dict[int, str] = {
    400: "Bad Request: malformed input",
    401: "Unauthorized: authentication required",
    403: "Forbidden: insufficient permissions",
    404: "Not Found: resource does not exist",
    409: "Conflict: duplicate key or constraint violation",
    422: "Unprocessable Entity: validation failed",
    500: "Internal Server Error: unexpected server error",
    501: "Not Implemented",
    503: "Service Unavailable",
    504: "Gateway Timeout",
}


# ───────────────────── Formatting helpers ────────────────────────────


def _limit(s: str, n: int = 4000) -> str:
    if len(s) <= n:
        return s
    return s[: n - 3] + "..."


def _stringify_exc(exc: BaseException) -> str:
    detail = getattr(exc, "detail", None)
    if detail:
        return _limit(str(detail))
    cls = exc.__class__
    msg = str(exc) or repr(exc)
    return _limit(f"{cls!r}: {msg}")


def _format_validation(err: Any) -> Any:
    # Pydantic v2/RequestValidationError both expose .errors()
    try:
        items = err.errors()  # type: ignore[attr-defined]
        if isinstance(items, Iterable):
            return list(items)
    except Exception:  # pragma: no cover
        pass
    return _limit(str(err))


# ───────────────────── Public conversions ────────────────────────────


def http_exc_to_rpc(exc: HTTPException) -> tuple[int, str, Any | None]:
    """
    Convert HTTPException → (rpc_code, message, data).
    """
    code = _HTTP_TO_RPC.get(exc.status_code, -32603)
    detail = exc.detail
    if isinstance(detail, (dict, list)):
        return code, ERROR_MESSAGES.get(code, "Unknown error"), detail
    # if we previously attached rpc attrs, prefer those
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
    """
    Convert JSON-RPC error code (and optional message/data) → HTTPException.
    """
    http_status = _RPC_TO_HTTP.get(rpc_code, 500)
    msg = (
        message
        or HTTP_ERROR_MESSAGES.get(http_status)
        or ERROR_MESSAGES.get(rpc_code, "Unknown error")
    )
    http_exc = HTTPException(status_code=http_status, detail=msg)
    # attach rpc context for symmetry
    setattr(http_exc, "rpc_code", rpc_code)
    setattr(http_exc, "rpc_message", msg)
    setattr(http_exc, "rpc_data", data)
    return http_exc


# ───────────────────── Exception → Standardized error ─────────────────────────


def _classify_exception(
    exc: BaseException,
) -> Tuple[int, str | dict | list, Any | None]:
    """
    Return (http_status, detail_or_message, data) suitable for HTTPException and JSON-RPC mapping.
    `detail_or_message` may be a string OR a structured dict/list (validation).
    """
    # Pass-through HTTPException preserving detail
    if isinstance(exc, HTTPException):
        return exc.status_code, exc.detail, getattr(exc, "rpc_data", None)

    # Validation errors → 422 with structured data
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

    # Common client errors
    if isinstance(exc, (ValueError, TypeError, KeyError)):
        return status.HTTP_400_BAD_REQUEST, _stringify_exc(exc), None
    if isinstance(exc, PermissionError):
        return status.HTTP_403_FORBIDDEN, _stringify_exc(exc), None
    if isinstance(exc, NotImplementedError):
        return status.HTTP_501_NOT_IMPLEMENTED, _stringify_exc(exc), None
    if isinstance(exc, TimeoutError):
        return status.HTTP_504_GATEWAY_TIMEOUT, _stringify_exc(exc), None

    # ORM/DB mapping
    if (NoResultFound is not None) and isinstance(exc, NoResultFound):
        return status.HTTP_404_NOT_FOUND, "Resource not found", None

    if _is_asyncpg_constraint_error(exc):
        # Bubble asyncpg constraints as 422; keep full message as detail
        return status.HTTP_422_UNPROCESSABLE_ENTITY, _stringify_exc(exc), None

    if (IntegrityError is not None) and isinstance(exc, IntegrityError):
        return status.HTTP_422_UNPROCESSABLE_ENTITY, _stringify_exc(exc), None

    if (OperationalError is not None) and isinstance(exc, OperationalError):
        return status.HTTP_503_SERVICE_UNAVAILABLE, "Database operation failed", None

    if (DBAPIError is not None) and isinstance(exc, DBAPIError):
        return status.HTTP_500_INTERNAL_SERVER_ERROR, _stringify_exc(exc), None

    # Fallback
    return status.HTTP_500_INTERNAL_SERVER_ERROR, _stringify_exc(exc), None


def create_standardized_error(exc: BaseException) -> HTTPException:
    """
    Normalize any exception → HTTPException with attached RPC context:
      • .rpc_code
      • .rpc_message
      • .rpc_data

    This keeps existing call sites intact (`raise create_standardized_error(exc)`)
    while giving the JSON-RPC layer enough info to produce a proper error envelope.
    """
    http_status, detail_or_message, data = _classify_exception(exc)

    # Compute RPC code/message
    rpc_code = _HTTP_TO_RPC.get(http_status, -32603)
    # If detail is structured, use default message; else prefer the string detail
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


# Convenience: build standardized error from explicit HTTP status/message (for non-exception paths)


def create_standardized_error_from_status(
    http_status: int,
    message: str | None = None,
    *,
    rpc_code: int | None = None,
    data: Any | None = None,
) -> tuple[HTTPException, int, str]:
    """
    Explicit constructor used by code paths that already decided on an HTTP status.
    Returns (HTTPException, rpc_code, rpc_message).
    """
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


# Convenience: build a JSON-RPC error payload directly from an HTTPException


def to_rpc_error_payload(exc: HTTPException) -> dict:
    """
    Produce a JSON-RPC error object from an HTTPException (with or without rpc_* attrs).
    Shape: {"code": int, "message": str, "data": Any|None}
    """
    code, msg, data = http_exc_to_rpc(exc)
    payload = {"code": code, "message": msg}
    if data is not None:
        payload["data"] = data
    else:
        # if detail was structured, include it as data (common for 422)
        if isinstance(exc.detail, (dict, list)):
            payload["data"] = exc.detail
    return payload


__all__ = [
    "HTTP_ERROR_MESSAGES",
    "ERROR_MESSAGES",
    "_HTTP_TO_RPC",
    "_RPC_TO_HTTP",
    "http_exc_to_rpc",
    "rpc_error_to_http",
    "create_standardized_error",
    "create_standardized_error_from_status",
    "to_rpc_error_payload",
]
