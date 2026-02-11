"""Compatibility exports for legacy ``tigrbl.deps.stdapi`` imports."""

from __future__ import annotations

import warnings

from ..api._api import APIRouter
from ..api._router import Router
from ..api._route import Route, compile_path
from ..core.crud.params import Body, Header, Path, Query
from ..response.stdapi import (
    FileResponse,
    HTMLResponse,
    JSONResponse,
    PlainTextResponse,
    RedirectResponse,
    Response,
    StreamingResponse,
)
from ..runtime.status.exceptions import HTTPException
from ..runtime.status.mappings import status
from ..security import (
    APIKey,
    HTTPAuthorizationCredentials,
    HTTPBearer,
    MutualTLS,
    OAuth2,
    OpenIdConnect,
)
from ..security.dependencies import Depends, Security
from ..system.favicon import FAVICON_PATH
from ..transport.request import Request

warnings.warn(
    "tigrbl.deps.stdapi is deprecated; import from concrete modules such as "
    "tigrbl.api._api, tigrbl.transport.request, tigrbl.response.stdapi, "
    "tigrbl.core.crud.params, and tigrbl.security.dependencies.",
    DeprecationWarning,
    stacklevel=2,
)

FastAPI = APIRouter

__all__ = [
    "APIRouter",
    "FastAPI",
    "Router",
    "Request",
    "Response",
    "JSONResponse",
    "HTMLResponse",
    "PlainTextResponse",
    "StreamingResponse",
    "FileResponse",
    "RedirectResponse",
    "HTTPException",
    "Depends",
    "Security",
    "Path",
    "Query",
    "Body",
    "Header",
    "HTTPBearer",
    "HTTPAuthorizationCredentials",
    "Route",
    "compile_path",
    "APIKey",
    "OAuth2",
    "OpenIdConnect",
    "MutualTLS",
    "status",
    "FAVICON_PATH",
]
