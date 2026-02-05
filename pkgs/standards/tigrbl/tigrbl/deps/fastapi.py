from __future__ import annotations

from pathlib import Path as FilePath
import warnings

from .stdapi import (
    APIRouter,
    Body,
    Depends,
    FastAPI,
    FileResponse,
    HTTPException,
    Path,
    Security,
)

warnings.warn(
    "tigrbl.deps.fastapi is deprecated; use tigrbl.deps.stdapi instead.",
    DeprecationWarning,
    stacklevel=2,
)

Router = APIRouter

FAVICON_PATH = FilePath(__file__).with_name("favicon.svg")


def App(*args, **kwargs):
    app = FastAPI(*args, **kwargs)

    @app.get("/favicon.ico", include_in_schema=False)
    async def favicon() -> FileResponse:  # pragma: no cover - simple static route
        return FileResponse(str(FAVICON_PATH), media_type="image/svg+xml")

    return app


# ── Public Exports ───────────────────────────────────────────────────────
__all__ = [
    "APIRouter",
    "Router",
    "FastAPI",
    "Security",
    "Depends",
    "Path",
    "Body",
    "HTTPException",
    "App",
]
