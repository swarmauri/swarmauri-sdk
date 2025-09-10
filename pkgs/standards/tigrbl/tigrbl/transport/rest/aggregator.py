# tigrbl/v3/transport/rest/aggregator.py
"""
Aggregates per-model REST routers into a single Router.

This does not build endpoints by itself — it simply collects the routers that
`tigrbl.bindings.rest` attached to each model at `model.rest.router`.

Recommended workflow:
  1) Include models with `mount_router=False` so you don't double-mount:
        api.include_model(User, mount_router=False)
        api.include_model(Team, mount_router=False)
  2) Aggregate and mount once:
        app.include_router(build_rest_router(api, base_prefix="/api"))
     or:
        mount_rest(api, app, base_prefix="/api")

Notes:
  • Router paths already include `/{resource}`; we only add `base_prefix`.
  • Model-level auth/db deps and extra REST deps are already attached to each
    model router by `bindings.rest`; this wrapper can add *additional* top-level
    dependencies if you pass them in.
"""

from __future__ import annotations

from typing import Any, Mapping, Optional, Sequence

try:
    from ...types import Router, Depends
except Exception:  # pragma: no cover
    # Minimal shim to keep importable without FastAPI
    class Router:  # type: ignore
        def __init__(self, *a, dependencies: Optional[Sequence[Any]] = None, **kw):
            self.routes = []
            self.includes = []
            self.dependencies = list(dependencies or [])

        def add_api_route(self, path: str, endpoint, methods: Sequence[str], **opts):
            self.routes.append((path, methods, endpoint, opts))

        def include_router(self, router: "Router", *, prefix: str = "", **opts):
            self.includes.append((router, prefix, opts))

    def Depends(fn):  # type: ignore
        return fn


def _norm_prefix(p: Optional[str]) -> str:
    if not p:
        return ""
    if not p.startswith("/"):
        p = "/" + p
    # Avoid double trailing slashes; FastAPI is lenient but keep it clean
    return p.rstrip("/")


def _normalize_deps(deps: Optional[Sequence[Any]]) -> list:
    """Accept either Depends(...) objects or plain callables."""
    out = []
    for d in deps or ():
        try:
            is_dep_obj = hasattr(d, "dependency")
        except Exception:
            is_dep_obj = False
        out.append(d if is_dep_obj else Depends(d))
    return out


def _iter_models(api: Any, only: Optional[Sequence[type]] = None) -> Sequence[type]:
    if only:
        return list(only)
    models: Mapping[str, type] = getattr(api, "models", {}) or {}
    # deterministic iteration
    return [models[k] for k in sorted(models.keys())]


def build_rest_router(
    api: Any,
    *,
    models: Optional[Sequence[type]] = None,
    base_prefix: str = "",
    dependencies: Optional[Sequence[Any]] = None,
) -> Router:
    """
    Build a top-level Router that includes each model's router under `base_prefix`.

    Args:
        api: your Tigrbl facade (or any object with `.models` dict).
        models: optional subset of models to include; defaults to all bound models.
        base_prefix: prefix applied once for all included routers (e.g., "/api").
        dependencies: additional router-level dependencies (Depends(...) or callables).

    Returns:
        Router ready to be mounted on your FastAPI app.
    """
    root = Router(dependencies=_normalize_deps(dependencies))
    prefix = _norm_prefix(base_prefix)

    for model in _iter_models(api, models):
        rest_ns = getattr(model, "rest", None)
        router = getattr(rest_ns, "router", None) if rest_ns is not None else None
        if router is None:
            # Nothing to include for this model (not bound or no routes)
            continue
        # Include with only the base prefix; the model router already has /{resource} in its paths
        root.include_router(router, prefix=prefix or "")
    return root


def mount_rest(
    api: Any,
    app: Any,
    *,
    models: Optional[Sequence[type]] = None,
    base_prefix: str = "",
    dependencies: Optional[Sequence[Any]] = None,
) -> Router:
    """
    Convenience helper: build the aggregated router and include it on `app`.

    Returns the created router so you can keep a reference if desired.
    """
    router = build_rest_router(
        api, models=models, base_prefix=base_prefix, dependencies=dependencies
    )
    include = getattr(app, "include_router", None)
    if callable(include):
        include(router)
    return router


__all__ = ["build_rest_router", "mount_rest"]
