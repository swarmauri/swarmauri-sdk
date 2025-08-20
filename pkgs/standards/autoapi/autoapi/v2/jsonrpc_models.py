from typing import (
    Any,
)
from fastapi import HTTPException
from pydantic import BaseModel, Field
import uuid

# ───────────────────── Centralized Error Mappings ────────────────────────────

# Standard HTTP to JSON-RPC error code mappings
_HTTP_TO_RPC: dict[int, int] = {
    400: -32602,  # Bad Request -> Invalid params
    401: -32001,  # Unauthorized -> Authentication required
    403: -32002,  # Forbidden -> Insufficient permissions
    404: -32003,  # Not Found -> Resource not found
    409: -32004,  # Conflict -> Resource conflict
    422: -32602,  # Unprocessable Entity -> Invalid params
    500: -32603,  # Internal Server Error -> Internal error
}

# Reverse mapping: JSON-RPC to HTTP error codes
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

# HTTP status code to standardized error message mapping
HTTP_ERROR_MESSAGES: dict[int, str] = {
    400: "Bad Request: malformed input",
    401: "Unauthorized: authentication required",
    403: "Forbidden: insufficient permissions",
    404: "Not Found: resource does not exist",
    409: "Conflict: duplicate key or constraint violation",
    422: "Unprocessable Entity: validation failed",
    500: "Internal Server Error: unexpected server error",
}


def _http_exc_to_rpc(exc: HTTPException) -> tuple[int, str, Any | None]:
    """Convert :class:`HTTPException` to ``(rpc_code, message, data)``.

    Any non-string detail on the ``HTTPException`` is propagated via the
    ``data`` field of the JSON-RPC error response so callers can inspect
    validation issues such as missing parameters.
    """

    code = _HTTP_TO_RPC.get(exc.status_code, -32603)  # default → Internal error
    detail = exc.detail
    if isinstance(detail, (dict, list)):
        return code, ERROR_MESSAGES.get(code, "Unknown error"), detail
    return code, detail or ERROR_MESSAGES.get(code, "Unknown error"), None


def _rpc_error_to_http(rpc_code: int, message: str | None = None) -> HTTPException:
    """
    Convert JSON-RPC error code to HTTPException.
    Supports reverse flow from RPC errors to HTTP errors.
    """
    http_status = _RPC_TO_HTTP.get(rpc_code, 500)
    error_message = (
        message
        or HTTP_ERROR_MESSAGES.get(http_status)
        or ERROR_MESSAGES.get(rpc_code, "Unknown error")
    )
    return HTTPException(status_code=http_status, detail=error_message)


def create_standardized_error(
    http_status: int, message: str | None = None, rpc_code: int | None = None
) -> tuple[HTTPException, int, str]:
    """
    Create a standardized error with both HTTP and RPC representations.

    Returns:
        tuple: (HTTPException, rpc_code, standardized_message)
    """
    # Determine RPC code
    if rpc_code is None:
        rpc_code = _HTTP_TO_RPC.get(http_status, -32603)  # Default to Internal error

    # Determine standardized messages
    if message is None:
        # Use HTTP-specific message for HTTP exception
        http_message = HTTP_ERROR_MESSAGES.get(http_status) or ERROR_MESSAGES.get(
            rpc_code, "Unknown error"
        )
        # Use RPC-specific message for RPC response
        rpc_message = ERROR_MESSAGES.get(rpc_code) or HTTP_ERROR_MESSAGES.get(
            http_status, "Unknown error"
        )
    else:
        # Use custom message for both
        http_message = rpc_message = message

    http_exc = HTTPException(status_code=http_status, detail=http_message)
    return http_exc, rpc_code, rpc_message


# ───────────────────── JSON-RPC envelopes ────────────────────────────


class _RPCReq(BaseModel):
    jsonrpc: str = Field(default="2.0", json_schema_extra={"Literal": True})
    method: str
    params: dict = {}
    id: str | int | None = str(uuid.uuid4())


class _RPCRes(BaseModel):
    jsonrpc: str = Field(default="2.0", json_schema_extra={"Literal": True})
    result: Any | None = None
    error: dict | None = None
    id: str | int | None = None


def _ok(x: Any, q: _RPCReq) -> _RPCRes:
    return _RPCRes(result=x, id=q.id)


def _err(code: int, msg: str, q: _RPCReq, data: dict | None = None) -> _RPCRes:
    # Use standardized message if none provided
    if not msg:
        msg = ERROR_MESSAGES.get(code, "Unknown error")
    return _RPCRes(error={"code": code, "message": msg, "data": data}, id=q.id)
