# autoapi/v3/system/diagnostics.py
"""
Diagnostics endpoints for AutoAPI v3.

Exposes a small router with:
  - GET /healthz     → DB connectivity check (sync or async)
  - GET /methodz     → list RPC-visible methods derived from OpSpecs
  - GET /hookz       → per-op phase chains (sequential order)
  - GET /planz       → runtime execution plan (flattened labels) per op

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
    from ..types import Router, Request, Depends
    from fastapi.responses import JSONResponse
except Exception:  # pragma: no cover
    # Lightweight shims so the module is importable without FastAPI
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


from sqlalchemy import text
from ..opspec.types import PHASES
from ..runtime.kernel import build_phase_chains
from ..runtime import events as _ev, plan as _plan, labels as _lbl

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
    """Return a module-qualified label for *fn* suitable for hook listings."""
    n = getattr(fn, "__qualname__", getattr(fn, "__name__", repr(fn)))
    m = getattr(fn, "__module__", None)
    return f"{m}.{n}" if m else n


def _label_hook(fn: Any, phase: str) -> str:
    subj = _label_callable(fn).replace(".", ":")
    return f"hook:{_lbl.DOMAINS[-1]}:{subj}@{phase}"


async def _maybe_execute(db: Any, stmt: str):
    try:
        rv = db.execute(text(stmt))  # type: ignore[attr-defined]
        if inspect.isawaitable(rv):
            return await rv
        return rv
    except Exception:
        # Some drivers prefer lowercase 'select 1'
        rv = db.execute(text("select 1"))  # type: ignore[attr-defined]
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
        """Ordered, canonical operation list."""
        methods: List[str] = []
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
                        "request_model": getattr(sp, "request_model", None) is not None,
                        "response_model": getattr(sp, "response_model", None)
                        is not None,
                        "routes": bool(getattr(sp, "expose_routes", True)),
                        "rpc": bool(getattr(sp, "expose_rpc", True)),
                        "tags": list(getattr(sp, "tags", ()) or (mname,)),
                    }
                )
        methods.sort(key=lambda x: (x["model"], x["alias"]))
        return {"methods": methods}

    return _methodz


def _build_hookz_endpoint(api: Any):
    async def _hookz():
        """
        Expose hook execution order for each method.

        Phases appear in runner order; error phases trail.
        Within each phase, hooks are listed in execution order: global (None) hooks,
        then method-specific hooks.
        """
        out: Dict[str, Dict[str, Dict[str, List[str]]]] = {}
        for model in _model_iter(api):
            mname = getattr(model, "__name__", "Model")
            hooks_root = getattr(model, "hooks", SimpleNamespace())
            # Build list of aliases from RPC ns or opspecs
            alias_sources = set()
            rpc_ns = getattr(model, "rpc", SimpleNamespace())
            alias_sources.update(getattr(rpc_ns, "__dict__", {}).keys())
            for sp in _opspecs(model):
                alias_sources.add(sp.alias)

            model_map: Dict[str, Dict[str, List[str]]] = {}
            for alias in sorted(alias_sources):
                alias_ns = getattr(hooks_root, alias, None) or SimpleNamespace()
                phase_map: Dict[str, List[str]] = {}
                for ph in PHASES:
                    steps = list(getattr(alias_ns, ph, []) or [])
                    if steps:
                        phase_map[ph] = [_label_callable(fn) for fn in steps]
                if phase_map:
                    model_map[alias] = phase_map
            if model_map:
                out[mname] = model_map
        return out

    return _hookz


def _build_planz_endpoint(api: Any):
    cache: Optional[Dict[str, Dict[str, List[str]]]] = None

    async def _planz():
        nonlocal cache
        """Expose the runtime step sequence for each operation."""
        if cache is not None:
            return cache
        out: Dict[str, Dict[str, List[str]]] = {}
        for model in _model_iter(api):
            mname = getattr(model, "__name__", "Model")
            model_map: Dict[str, List[str]] = {}
            compiled_plan = getattr(
                getattr(model, "runtime", SimpleNamespace()), "plan", None
            )
            if compiled_plan is None:
                specs = getattr(model, "__autoapi_colspecs__", None) or getattr(
                    model, "__autoapi_cols__", None
                )
                if specs is not None:
                    try:
                        compiled_plan = _plan.attach_atoms_for_model(model, specs)
                    except Exception:
                        compiled_plan = None
            for sp in _opspecs(model):
                seq: List[str] = []
                persist = getattr(sp, "persist", "default") != "skip"
                if compiled_plan is not None:
                    deps: List[str] = [
                        _label_callable(d) if callable(d) else str(d)
                        for d in getattr(sp, "deps", []) or []
                    ]
                    secdeps: List[str] = [
                        _label_callable(d) if callable(d) else str(d)
                        for d in getattr(sp, "secdeps", []) or []
                    ]
                    handler = getattr(sp, "handler", None)
                    if handler is not None:
                        deps.append(_label_callable(handler))
                    labels = _plan.flattened_order(
                        compiled_plan,
                        persist=persist,
                        include_system_steps=True,
                        deps=deps,
                        secdeps=secdeps,
                    )
                    pre_labels: List[str] = []
                    phase_labels: Dict[str, List[str]] = {ph: [] for ph in PHASES}
                    for lbl in labels:
                        kind = getattr(lbl, "kind", None)
                        if kind in {"secdep", "dep"}:
                            pre_labels.append(str(lbl))
                            continue
                        phase = (
                            lbl.anchor
                            if kind == "sys"
                            else _ev.phase_for_event(lbl.anchor)
                        )
                        phase_labels[phase].append(str(lbl))
                    hooks_root = getattr(model, "hooks", SimpleNamespace())
                    alias_ns = getattr(hooks_root, sp.alias, SimpleNamespace())
                    hook_labels: Dict[str, List[str]] = {
                        ph: [
                            _label_hook(fn, ph)
                            for fn in getattr(alias_ns, ph, []) or []
                        ]
                        for ph in PHASES
                    }
                    seq.extend(pre_labels)
                    for ph in PHASES:
                        if ph == "START_TX":
                            # PRE_HANDLER hooks run before starting the TX
                            seq.extend(hook_labels.get("PRE_HANDLER", []))
                            seq.extend(phase_labels.get("PRE_HANDLER", []))
                            seq.extend(phase_labels.get(ph, []))
                            seq.extend(hook_labels.get(ph, []))
                        elif ph == "PRE_HANDLER":
                            # handled in START_TX branch
                            continue
                        elif ph == "HANDLER":
                            phase_list = phase_labels.get(ph, [])
                            if phase_list and phase_list[0].startswith("sys:"):
                                seq.append(phase_list[0])
                                atoms = phase_list[1:]
                            else:
                                atoms = phase_list
                            seq.extend(hook_labels.get(ph, []))
                            seq.extend(atoms)
                        elif ph == "END_TX":
                            seq.extend(hook_labels.get(ph, []))
                            seq.extend(phase_labels.get(ph, []))
                        else:
                            seq.extend(hook_labels.get(ph, []))
                            seq.extend(phase_labels.get(ph, []))
                else:
                    deps: List[str] = [
                        _label_callable(d) if callable(d) else str(d)
                        for d in getattr(sp, "deps", []) or []
                    ]
                    secdeps: List[str] = [
                        _label_callable(d) if callable(d) else str(d)
                        for d in getattr(sp, "secdeps", []) or []
                    ]
                    handler = getattr(sp, "handler", None)
                    if handler is not None:
                        deps.append(_label_callable(handler))
                    chains = build_phase_chains(model, sp.alias)
                    seq.extend(f"secdep:{s}" for s in secdeps)
                    seq.extend(f"dep:{d}" for d in deps)
                    for ph in PHASES:
                        if ph == "START_TX" and persist:
                            seq.append("sys:txn:begin@START_TX")
                        if ph == "HANDLER" and persist:
                            seq.append(f"sys:handler:{sp.target}@HANDLER")
                        for step in chains.get(ph, []) or []:
                            name = getattr(step, "__name__", "")
                            if name in {"start_tx", "end_tx"}:
                                continue
                            seq.append(_label_hook(step, ph))
                        if ph == "END_TX" and persist:
                            seq.append("sys:txn:commit@END_TX")
                model_map[sp.alias] = seq
            if model_map:
                out[mname] = model_map
        cache = out
        return cache

    return _planz


# ───────────────────────────────────────────────────────────────────────────────
# Public factory
# ───────────────────────────────────────────────────────────────────────────────


def mount_diagnostics(
    api: Any,
    *,
    get_db: Optional[Callable[..., Any]] = None,
    get_async_db: Optional[Callable[..., Awaitable[Any]]] = None,
) -> Router:
    """
    Create & return a Router that exposes:
      GET /healthz
      GET /methodz
      GET /hookz
      GET /planz
    """
    router = Router()

    # Prefer async DB getter if provided
    dep = get_async_db or get_db

    router.add_api_route(
        "/healthz",
        _build_healthz_endpoint(dep),
        methods=["GET"],
        name="healthz",
        tags=["system"],
        summary="Health",
        description="Database connectivity check.",
    )
    router.add_api_route(
        "/methodz",
        _build_methodz_endpoint(api),
        methods=["GET"],
        name="methodz",
        tags=["system"],
        summary="Methods",
        description="Ordered, canonical operation list.",
    )
    router.add_api_route(
        "/hookz",
        _build_hookz_endpoint(api),
        methods=["GET"],
        name="hookz",
        tags=["system"],
        summary="Hooks",
        description=(
            "Expose hook execution order for each method.\n\n"
            "Phases appear in runner order; error phases trail.\n"
            "Within each phase, hooks are listed in execution order: "
            "global (None) hooks, then method-specific hooks."
        ),
    )
    router.add_api_route(
        "/planz",
        _build_planz_endpoint(api),
        methods=["GET"],
        name="planz",
        tags=["system"],
        summary="Plan",
        description="Flattened runtime execution plan per operation.",
    )

    return router


__all__ = ["mount_diagnostics"]
