"""Core stdapi primitives used by the router implementation."""

from __future__ import annotations

from ..core.crud.params import Body, Header, Param, Path, Query
from ..response.stdapi import (
    FileResponse,
    HTMLResponse,
    JSONResponse,
    PlainTextResponse,
    Response,
)
from ..runtime.status.exceptions import HTTPException
from ..runtime.status.mappings import status
from ..transport.request import Request
from ..api._route import Handler, Route, compile_path
from ._stdapi_security import (
    Depends,
    HTTPAuthorizationCredentials,
    HTTPBearer,
    Security,
    Dependency,
    _Dependency,
)

__all__ = [
    "Request",
    "Response",
    "JSONResponse",
    "HTMLResponse",
    "PlainTextResponse",
    "FileResponse",
    "HTTPException",
    "status",
    "HTTPAuthorizationCredentials",
    "HTTPBearer",
    "Dependency",
    "_Dependency",
    "Depends",
    "Security",
    "Param",
    "Body",
    "Query",
    "Path",
    "Header",
    "Handler",
    "Route",
    "compile_path",
    "_compile_path",
]

_compile_path = compile_path
