"""Deprecated compatibility module for REST FastAPI-style primitives.

Prefer importing directly from:
- ``tigrbl.response`` for response classes
- ``tigrbl.runtime.status`` for ``status`` and ``HTTPException``
- ``tigrbl.api._api`` / ``tigrbl.transport.request`` / ``tigrbl.security.dependencies``
"""

from __future__ import annotations

import warnings

from ...api._api import Router
from ...core.crud.params import Body, Path, Query
from ...response import (
    FileResponse,
    HTMLResponse,
    JSONResponse,
    PlainTextResponse,
    StdApiResponse,
)
from ...runtime.status import HTTPException, status
from ...security.dependencies import Depends, Security
from ...transport.request import Request

warnings.warn(
    "tigrbl.bindings.rest.fastapi is deprecated; import from "
    "tigrbl.response, tigrbl.runtime.status, and concrete modules instead.",
    DeprecationWarning,
    stacklevel=2,
)

Response = StdApiResponse
_status = status

__all__ = [
    "Router",
    "Request",
    "Body",
    "Depends",
    "Security",
    "Query",
    "Path",
    "HTTPException",
    "status",
    "_status",
    "Response",
    "JSONResponse",
    "HTMLResponse",
    "PlainTextResponse",
    "FileResponse",
]
