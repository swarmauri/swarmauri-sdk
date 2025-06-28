from enum import IntEnum


class Code(IntEnum):
    # Standard JSON-RPC codes
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603

    # Peagen-specific domain errors, never re-use numbers
    TEMPLATE_SET_MISSING = -32010
    WORKER_OFFLINE = -32020
    DATABASE_FAILURE = -32030
    SECRET_NOT_FOUND = -32004
    TASK_NOT_FOUND = -32001


__all__ = ["Code"]
