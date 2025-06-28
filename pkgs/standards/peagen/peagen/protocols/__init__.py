"""Typed JSON-RPC protocol primitives and method registry."""

from .envelope import Error, Request, Response, parse_request
from .error_codes import Code
from . import _registry
from .methods import (
    TASK_SUBMIT,
    TASK_PATCH,
    TASK_GET,
    TASK_CANCEL,
    TASK_PAUSE,
    TASK_RESUME,
    TASK_RETRY,
    TASK_RETRY_FROM,
    KEYS_UPLOAD,
    KEYS_FETCH,
    KEYS_DELETE,
    SECRETS_ADD,
    SECRETS_GET,
    SECRETS_DELETE,
    WORKER_REGISTER,
    WORKER_HEARTBEAT,
    WORKER_LIST,
)

__all__ = [
    "Error",
    "Request",
    "Response",
    "parse_request",
    "Code",
    "_registry",
    "TASK_SUBMIT",
    "TASK_PATCH",
    "TASK_GET",
    "TASK_CANCEL",
    "TASK_PAUSE",
    "TASK_RESUME",
    "TASK_RETRY",
    "TASK_RETRY_FROM",
    "KEYS_UPLOAD",
    "KEYS_FETCH",
    "KEYS_DELETE",
    "SECRETS_ADD",
    "SECRETS_GET",
    "SECRETS_DELETE",
    "WORKER_REGISTER",
    "WORKER_HEARTBEAT",
    "WORKER_LIST",
]
