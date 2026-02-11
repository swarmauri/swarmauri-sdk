"""Deprecated compatibility module for REST FastAPI-style primitives.

Prefer importing directly from:
- ``tigrbl.response`` for response classes
- ``tigrbl.runtime.status`` for ``status`` and ``HTTPException``
- ``tigrbl.deps.stdapi`` for ``Request`` and dependency helpers
"""

from __future__ import annotations

import warnings

from ...deps.stdapi import Body, Depends, Path, Query, Request, Router, Security
from ...response import (
    FileResponse,
    HTMLResponse,
    JSONResponse,
    PlainTextResponse,
    StdApiResponse,
)
from ...runtime.status import HTTPException, status

warnings.warn(
    "tigrbl.bindings.rest.fastapi is deprecated; import from "
    "tigrbl.response, tigrbl.runtime.status, and tigrbl.deps.stdapi instead.",
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
