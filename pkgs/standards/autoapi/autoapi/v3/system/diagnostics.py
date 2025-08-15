# autoapi/v3/system/diagnostics.py
"""
Diagnostics endpoints for AutoAPI v3.

Exposes a small router with:
  - GET /healthz     → DB connectivity check (sync or async)
  - GET /methodz     → list RPC-visible methods derived from OpSpecs
  - GET /hookz       → per-op phase chains (sequential order)

Usage:
    from autoapi.v3.system.diagnostics import mount_diagnostics
    app.include_router(mount_diagnostics(api, get_async_db=get_async_db), prefix="/system")
"""

from __future__ import annotations

import inspect
import logging
from types import SimpleNamespace
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Sequence,
)

try:
    from fastapi import APIRouter, Request, Depends
    from fastapi.responses import JSONResponse
except Exception:  # pragma: no cover
    # Lightweight shims so the module is importable without FastAPI
    class APIRouter:  # type: ignore
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


from ..opspec.types import PHASES

logger = logging.getLogger(__name__)


# ───────────────────────────────────────────────────────────────────────────────
# Helpers
# ───────────────────────────────────────────────────────────────────────────────


def _model_iter(api: Any) -> Iterable[type]:
    models = getattr(api, "models", {}) or {}
    return models.values()


def _opspecs(model: type):
    return getattr(getattr(model, "opspecs", SimpleNamespace()), "all", ()) or ()


def _label_callable(fn: Any) -> str:
    # Best-effort human-readable name
    if hasattr(fn, "__name__"):
        return fn.__name__  # type: ignore[return-value]
    if hasattr(fn, "__qualname__"):
        return fn.__qualname__  # type: ignore[return-value]
    return repr(fn)


async def _maybe_execute(db: Any, stmt: Any):
    try:
        rv = db.execute(stmt)  # type: ignore[attr-defined]
        if inspect.isawaitable(rv):
            return await rv
        return rv
    except TypeError:
        # Some drivers prefer lowercase 'select 1'
        rv = db.execute("select 1")  # type: ignore[attr-defined]
        if inspect.isawaitable(rv):
            return await rv
        return rv


# ───────────────────────────────────────────────────────────────────────────────
# Builders
# ───────────────────────────────────────────────────────────────────────────────


def _build_healthz_endpoint(dep: Optional[Callable[..., Any]]):
    """
    Returns a FastAPI endpoint function for /healthz.
    If `dep` is provided, it's used as a dependency to supply `db`.
    Otherwise, we try request.state.db.
    """
    if dep is not None:

        async def _healthz(db: Any = Depends(dep)):
            try:
                await _maybe_execute(db, "SELECT 1")
                return {"ok": True}
            except Exception as e:  # pragma: no cover
                logger.exception("/healthz failed")
                return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

        return _healthz

    async def _healthz(request: Request):
        db = getattr(request.state, "db", None)
        if db is None:
            # No DB provided—treat as healthy from API process standpoint
            return {"ok": True, "warning": "no-db"}
        try:
            await _maybe_execute(db, "SELECT 1")
            return {"ok": True}
        except Exception as e:  # pragma: no cover
            logger.exception("/healthz failed")
            return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

    return _healthz


def _build_methodz_endpoint(api: Any):
    async def _methodz():
        methods: List[Dict[str, Any]] = []
        for model in _model_iter(api):
            mname = getattr(model, "__name__", "Model")
            for sp in _opspecs(model):
                if not getattr(sp, "expose_rpc", True):
                    continue
                methods.append(
                    {
                        "method": f"{mname}.{sp.alias}",
                        "model": mname,
                        "alias": sp.alias,
                        "target": sp.target,
                        "arity": sp.arity,
                        "persist": sp.persist,
                        "returns": sp.returns,
                        "routes": bool(getattr(sp, "expose_routes", True)),
                        "rpc": bool(getattr(sp, "expose_rpc", True)),
                        "tags": list(getattr(sp, "tags", ()) or ()),
                    }
                )
        methods.sort(key=lambda x: (x["model"], x["alias"]))
        return {"methods": methods}

    return _methodz


def _build_hookz_endpoint(api: Any):
    async def _hookz():
        out: Dict[str, Dict[str, Dict[str, List[str]]]] = {}
        for model in _model_iter(api):
            mname = getattr(model, "__name__", "Model")
            out.setdefault(mname, {})
            hooks_root = getattr(model, "hooks", SimpleNamespace())
            # Build list of aliases from RPC ns or opspecs
            alias_sources = set()
            rpc_ns = getattr(model, "rpc", SimpleNamespace())
            alias_sources.update(getattr(rpc_ns, "__dict__", {}).keys())
            for sp in _opspecs(model):
                alias_sources.add(sp.alias)

            for alias in sorted(alias_sources):
                alias_ns = getattr(hooks_root, alias, None)
                if alias_ns is None:
                    continue
                phase_map: Dict[str, List[str]] = {}
                for ph in PHASES:
                    steps = list(getattr(alias_ns, ph, []) or [])
                    phase_map[ph] = [_label_callable(fn) for fn in steps]
                out[mname][alias] = phase_map
        return out

    return _hookz


# ───────────────────────────────────────────────────────────────────────────────
# Public factory
# ───────────────────────────────────────────────────────────────────────────────


def mount_diagnostics(
    api: Any,
    *,
    get_db: Optional[Callable[..., Any]] = None,
    get_async_db: Optional[Callable[..., Awaitable[Any]]] = None,
) -> APIRouter:
    """
    Create & return an APIRouter that exposes:
      GET /healthz
      GET /methodz
      GET /hookz
    """
    router = APIRouter()

    # Prefer async DB getter if provided
    dep = get_async_db or get_db

    router.add_api_route(
        "/healthz",
        _build_healthz_endpoint(dep),
        methods=["GET"],
        name="autoapi.healthz",
    )
    router.add_api_route(
        "/methodz",
        _build_methodz_endpoint(api),
        methods=["GET"],
        name="autoapi.methodz",
    )
    router.add_api_route(
        "/hookz", _build_hookz_endpoint(api), methods=["GET"], name="autoapi.hookz"
    )

    return router


__all__ = ["mount_diagnostics"]
