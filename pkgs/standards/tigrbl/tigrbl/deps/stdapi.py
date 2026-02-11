"""Standard API primitives for Tigrbl.

This module strictly does not use FastAPI.
"""

from ._stdapi_router import APIRouter, FastAPI
from ..system.favicon import FAVICON_PATH
from ..security import APIKey, MutualTLS, OAuth2, OpenIdConnect
from ._stdapi_types import (
    Body,
    Depends,
    FileResponse,
    HTMLResponse,
    HTTPAuthorizationCredentials,
    HTTPBearer,
    HTTPException,
    Header,
    JSONResponse,
    Path,
    PlainTextResponse,
    Query,
    Request,
    Response,
    Security,
    status,
)

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
    "APIKey",
    "OAuth2",
    "OpenIdConnect",
    "MutualTLS",
    "status",
    "FAVICON_PATH",
]
