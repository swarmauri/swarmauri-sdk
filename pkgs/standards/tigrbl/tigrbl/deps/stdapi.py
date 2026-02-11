"""Standard API primitives for Tigrbl.

This module strictly does not use FastAPI.
"""

from ._stdapi_router import APIRouter, FAVICON_PATH, FastAPI
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
    "status",
    "FAVICON_PATH",
]
