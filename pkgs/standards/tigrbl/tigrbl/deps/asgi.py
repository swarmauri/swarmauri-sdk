"""ASGI-oriented API primitives for Tigrbl."""

from ._stdapi_router import APIRouter, ASGIApp
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
from ..security import HTTPAuthorizationCredentials as HTTPAuthorizationCredentials
from ..security import HTTPBearer as HTTPBearer
from ..security.dependencies import Depends, Security
from ..system.favicon import FAVICON_PATH
from ..security import APIKey, MutualTLS, OAuth2, OpenIdConnect
from ..transport.request import Request

Router = APIRouter
App = ASGIApp

__all__ = [
    "APIRouter",
    "ASGIApp",
    "App",
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
