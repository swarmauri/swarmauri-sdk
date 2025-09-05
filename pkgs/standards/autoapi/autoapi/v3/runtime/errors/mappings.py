from __future__ import annotations

# HTTP → JSON-RPC code map
_HTTP_TO_RPC: dict[int, int] = {
    400: -32602,
    401: -32001,
    403: -32002,
    404: -32003,
    409: -32004,
    422: -32602,
    500: -32603,
    501: -32603,
    503: -32603,
    504: -32603,
}

# JSON-RPC → HTTP status map
_RPC_TO_HTTP: dict[int, int] = {
    -32700: 400,
    -32600: 400,
    -32601: 404,
    -32602: 400,
    -32603: 500,
    -32001: 401,
    -32002: 403,
    -32003: 404,
    -32004: 409,
}

# Standardized error messages
ERROR_MESSAGES: dict[int, str] = {
    -32700: "Parse error",
    -32600: "Invalid Request",
    -32601: "Method not found",
    -32602: "Invalid params",
    -32603: "Internal error",
    -32001: "Authentication required",
    -32002: "Insufficient permissions",
    -32003: "Resource not found",
    -32004: "Resource conflict",
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

__all__ = [
    "_HTTP_TO_RPC",
    "_RPC_TO_HTTP",
    "ERROR_MESSAGES",
    "HTTP_ERROR_MESSAGES",
]
