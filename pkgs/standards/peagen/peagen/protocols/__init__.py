"""Typed JSON-RPC protocol primitives and method registry."""

from .envelope import Error, Request, Response, parse_request
from .error_codes import ErrorCode, Code
from . import _registry
from .methods import (
    TASK_SUBMIT,
    KEYS_UPLOAD,
    KEYS_FETCH,
    KEYS_DELETE,
    SECRETS_ADD,
    SECRETS_GET,
    SECRETS_DELETE,
)

__all__ = [
    "Error",
    "Request",
    "Response",
    "parse_request",
    "ErrorCode",
    "Code",
    "_registry",
    "TASK_SUBMIT",
    "KEYS_UPLOAD",
    "KEYS_FETCH",
    "KEYS_DELETE",
    "SECRETS_ADD",
    "SECRETS_GET",
    "SECRETS_DELETE",
]
