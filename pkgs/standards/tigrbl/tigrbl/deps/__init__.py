# ── Third-party Dependencies Re-exports ─────────────────────────────────
"""
Centralized third-party dependency imports for tigrbl.

This module provides a single location for all third-party dependencies,
making it easier to manage versions and potential replacements.
"""

from ..api._api import APIRouter, Router
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

# Re-export all SQLAlchemy dependencies
from .sqlalchemy import relationship  # noqa: F401
from .sqlalchemy import *  # noqa: F403, F401

# Re-export all Pydantic dependencies
from .pydantic import *  # noqa: F403, F401

from .fastapi import FastAPI

# Re-export FastAPI compatibility and Starlette compatibility modules
from .fastapi import *  # noqa: F403, F401
from .starlette import *  # noqa: F403, F401

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
    "APIKey",
    "OAuth2",
    "OpenIdConnect",
    "MutualTLS",
    "status",
    "FAVICON_PATH",
]
