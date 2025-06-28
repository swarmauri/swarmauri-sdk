"""Canonical JSON-RPC error codes used across Peagen components."""

from enum import IntEnum


class ErrorCode(IntEnum):
    """Enumerates JSON-RPC and Peagen-specific error codes."""

    # Standard JSON-RPC codes
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603

    # Peagen domain codes
    TEMPLATE_SET_MISSING = -32010
    WORKER_OFFLINE = -32020
    DATABASE_FAILURE = -32030
    SECRET_NOT_FOUND = -32004
    TASK_NOT_FOUND = -32001


# Backwards compatibility for imports using ``Code``
Code = ErrorCode


__all__ = ["ErrorCode", "Code"]
