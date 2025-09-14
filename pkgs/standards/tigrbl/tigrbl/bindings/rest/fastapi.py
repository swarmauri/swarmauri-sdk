from __future__ import annotations
import logging

from types import SimpleNamespace
from typing import Callable, Sequence

logger = logging.getLogger("uvicorn")
logger.debug("Loaded module v3/bindings/rest/fastapi")

try:
    from ...types import (
        Router,
        Request,
        Body,
        Depends,
        HTTPException,
        Response,
        Path,
        Security,
    )
    from fastapi import Query
    from fastapi import status as _status
except Exception:  # pragma: no cover

    class Router:  # type: ignore
        def __init__(self, *a, **kw):
            self.routes = []

        def add_api_route(
            self, path: str, endpoint: Callable, methods: Sequence[str], **opts
        ):
            self.routes.append((path, methods, endpoint, opts))

    class Request:  # type: ignore
        def __init__(self, scope=None):
            self.scope = scope or {}
            self.query_params = {}
            self.state = SimpleNamespace()

    def Body(default=None, **kw):  # type: ignore
        return default

    def Depends(fn):  # type: ignore
        return fn

    def Security(fn):  # type: ignore
        return fn

    def Query(default=None, **kw):  # type: ignore
        return default

    def Path(default=None, **kw):  # type: ignore
        return default

    class HTTPException(Exception):  # type: ignore
        def __init__(self, status_code: int, detail: str | None = None):
            super().__init__(detail)
            self.status_code = status_code
            self.detail = detail

    class Response:  # type: ignore
        def __init__(self, *a, **kw):
            pass

    class _status:  # type: ignore
        HTTP_200_OK = 200
        HTTP_201_CREATED = 201
        HTTP_204_NO_CONTENT = 204
        HTTP_400_BAD_REQUEST = 400
        HTTP_401_UNAUTHORIZED = 401
        HTTP_403_FORBIDDEN = 403
        HTTP_404_NOT_FOUND = 404
        HTTP_409_CONFLICT = 409
        HTTP_422_UNPROCESSABLE_ENTITY = 422
        HTTP_429_TOO_MANY_REQUESTS = 429
        HTTP_500_INTERNAL_SERVER_ERROR = 500
