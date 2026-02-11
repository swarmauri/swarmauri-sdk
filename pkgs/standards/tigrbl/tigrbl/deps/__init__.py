# ── Third-party and framework dependency re-exports ──────────────────────
"""Centralized dependency exports for Tigrbl's ASGI runtime."""

from .sqlalchemy import relationship  # noqa: F401
from .sqlalchemy import *  # noqa: F403, F401
from .pydantic import *  # noqa: F403, F401

from ._stdapi_router import APIRouter, FastAPI
from ..api._route import Route, compile_path
from ..core.crud.params import Body, Header, Path, Query
from ..response.stdapi import (
    FileResponse,
    HTMLResponse,
    JSONResponse,
    PlainTextResponse,
    Response,
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

Router = APIRouter

__all__ = [
    "APIRouter",
    "FastAPI",
    "Router",
    "Request",
    "Response",
    "JSONResponse",
    "HTMLResponse",
    "PlainTextResponse",
    "FileResponse",
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
