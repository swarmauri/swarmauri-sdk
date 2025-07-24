from typing import (
    Any,
)
from fastapi import HTTPException
from pydantic import BaseModel, Field
import uuid

# ───────────────────── Centralized Error Mappings ────────────────────────────

# Standard HTTP to JSON-RPC error code mappings
_HTTP_TO_RPC: dict[int, int] = {
    400: -32602,  # Invalid params
    404: -32601,  # Method / object not found
    409: -32099,  # Application-specific – duplicate key
    422: -32098,  # Application-specific – constraint violation
    500: -32000,  # Server error
}

# Reverse mapping: JSON-RPC to HTTP error codes
_RPC_TO_HTTP: dict[int, int] = {
    -32602: 400,  # Invalid params
    -32601: 404,  # Method / object not found
    -32099: 409,  # Application-specific – duplicate key
    -32098: 422,  # Application-specific – constraint violation
    -32000: 500,  # Server error
    -32700: 400,  # Parse error
    -32600: 400,  # Invalid Request
    -32603: 500,  # Internal error
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


def _http_exc_to_rpc(exc: HTTPException) -> tuple[int, dict]:
    """
    Convert FastAPI HTTPException -> (jsonrpc_code, data_obj)
    `data` is optional per spec; we include the HTTP status for clients
    that want the original information.
    """
    code = _HTTP_TO_RPC.get(exc.status_code, -32000)
    data = {"http_status": exc.status_code}
    return code, data


def _rpc_error_to_http(rpc_code: int, message: str | None = None) -> HTTPException:
    """
    Convert JSON-RPC error code to HTTPException.
    Supports reverse flow from RPC errors to HTTP errors.
    """
    http_status = _RPC_TO_HTTP.get(rpc_code, 500)
    error_message = (
        message
        or ERROR_MESSAGES.get(rpc_code)
        or HTTP_ERROR_MESSAGES.get(http_status, "Unknown error")
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
        rpc_code = _HTTP_TO_RPC.get(http_status, -32000)

    # Determine standardized message
    if message is None:
        message = ERROR_MESSAGES.get(rpc_code) or HTTP_ERROR_MESSAGES.get(
            http_status, "Unknown error"
        )

    http_exc = HTTPException(status_code=http_status, detail=message)
    return http_exc, rpc_code, message


# ───────────────────── JSON-RPC envelopes ────────────────────────────


class _RPCReq(BaseModel):
    jsonrpc: str = Field(default="2.0", Literal=True)
    method: str
    params: dict = {}
    id: str | int | None = str(uuid.uuid4())


class _RPCRes(BaseModel):
    jsonrpc: str = Field(default="2.0", Literal=True)
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
