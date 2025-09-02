from __future__ import annotations

try:  # pragma: no cover - optional runtime dependency
    from starlette.background import BackgroundTask
    from starlette.requests import Request
    from starlette.responses import (
        Response,
        JSONResponse,
        HTMLResponse,
        PlainTextResponse,
        StreamingResponse,
        FileResponse,
        RedirectResponse,
    )
except Exception:  # pragma: no cover
    BackgroundTask = None  # type: ignore
    Request = None  # type: ignore
    Response = None  # type: ignore
    JSONResponse = None  # type: ignore
    HTMLResponse = None  # type: ignore
    PlainTextResponse = None  # type: ignore
    StreamingResponse = None  # type: ignore
    FileResponse = None  # type: ignore
    RedirectResponse = None  # type: ignore

__all__ = [
    "BackgroundTask",
    "Request",
    "Response",
    "JSONResponse",
    "HTMLResponse",
    "PlainTextResponse",
    "StreamingResponse",
    "FileResponse",
    "RedirectResponse",
]
