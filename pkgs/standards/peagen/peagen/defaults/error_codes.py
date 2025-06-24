"""peagen.defaults.error_codes
----------------------------
Application-specific JSON-RPC error codes.
"""

from enum import IntEnum


class ErrorCode(IntEnum):
    """Enumerates Peagen-specific JSON-RPC error codes."""

    SECRET_NOT_FOUND = -32004
    TASK_NOT_FOUND = -32001
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602


__all__ = ["ErrorCode"]
