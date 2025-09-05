from __future__ import annotations

import inspect
from types import SimpleNamespace
from typing import Any, Callable, Iterable

from sqlalchemy import text

try:  # pragma: no cover - for optional fastapi
    from ...types import Router, Request, Depends  # type: ignore  # noqa: F401
    from fastapi.responses import JSONResponse  # type: ignore
except Exception:  # pragma: no cover

    class Router:  # type: ignore
        def __init__(self, *a, **kw):
            self.routes = []

        def add_api_route(
            self, path: str, endpoint: Callable, methods: Iterable[str], **opts
        ):
            self.routes.append((path, methods, endpoint, opts))

    class Request:  # type: ignore
        def __init__(self, scope=None):
            self.scope = scope or {}
            self.state = SimpleNamespace()
            self.query_params = {}

    class Depends:  # type: ignore
        def __init__(self, dependency):
            self.dependency = dependency

    class JSONResponse(dict):  # type: ignore
        def __init__(self, content: Any, status_code: int = 200):
            super().__init__(content=content, status_code=status_code)


def _model_iter(api: Any) -> Iterable[type]:
    models = getattr(api, "models", {}) or {}
    return models.values()


def _opspecs(model: type):
    return getattr(getattr(model, "opspecs", SimpleNamespace()), "all", ()) or ()


def _label_callable(fn: Any) -> str:
    n = getattr(fn, "__qualname__", getattr(fn, "__name__", repr(fn)))
    m = getattr(fn, "__module__", None)
    return f"{m}.{n}" if m else n


def _label_hook(fn: Any, phase: str) -> str:
    subj = _label_callable(fn).replace(".", ":")
    return f"hook:wire:{subj}@{phase}"


async def _maybe_execute(db: Any, stmt: str):
    try:
        rv = db.execute(text(stmt))  # type: ignore[attr-defined]
        if inspect.isawaitable(rv):
            return await rv
        return rv
    except Exception:
        rv = db.execute(text("select 1"))  # type: ignore[attr-defined]
        if inspect.isawaitable(rv):
            return await rv
        return rv
