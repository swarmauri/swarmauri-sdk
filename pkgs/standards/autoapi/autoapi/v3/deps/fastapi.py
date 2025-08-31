# ── FastAPI Imports ─────────────────────────────────────────────────────
from fastapi import (
    APIRouter,
    FastAPI,
    Security,
    Depends,
    Request,
    Response,
    Path as FastAPIPath,
    Body,
    HTTPException,
)
from fastapi.responses import FileResponse
from pathlib import Path as FilePath

Router = APIRouter
Path = FastAPIPath

FAVICON_PATH = FilePath(__file__).with_name("favicon.svg")


def App(*args, **kwargs):
    app = FastAPI(*args, **kwargs)

    @app.get("/favicon.ico", include_in_schema=False)
    async def favicon() -> FileResponse:  # pragma: no cover - simple static route
        return FileResponse(FAVICON_PATH, media_type="image/svg+xml")

    return app


# ── Public Exports ───────────────────────────────────────────────────────
__all__ = [
    "APIRouter",
    "Router",
    "FastAPI",
    "Security",
    "Depends",
    "Request",
    "Response",
    "Path",
    "Body",
    "HTTPException",
    "App",
]
