from __future__ import annotations

from typing import Any, Callable, Sequence
from types import SimpleNamespace

try:
    from ...types import Router, Request, Depends
    from fastapi.responses import JSONResponse
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
            self.state = SimpleNamespace()
            self.query_params = {}

    class JSONResponse(dict):  # type: ignore
        def __init__(self, content: Any, status_code: int = 200):
            super().__init__(content=content, status_code=status_code)

    def Depends(fn: Callable[..., Any]):  # type: ignore
        return fn
