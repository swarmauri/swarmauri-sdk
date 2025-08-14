# autoapi/v3/bindings/api.py
from __future__ import annotations

import logging
from types import SimpleNamespace
from typing import Any, Awaitable, Callable, Dict, Iterable, Mapping, Optional, Sequence, Tuple, Type, Union

from . import model as _binder  # bind(model) → builds/attaches namespaces
from ..opspec import OpSpec

logger = logging.getLogger(__name__)

# Public type for the API facade object users pass to include_model(...)
ApiLike = Any


# ───────────────────────────────────────────────────────────────────────────────
# Helpers: resource/prefix, namespaces, router mounting
# ───────────────────────────────────────────────────────────────────────────────

def _snake(name: str) -> str:
    out = []
    for i, ch in enumerate(name):
        if ch.isupper() and i and (not name[i - 1].isupper()):
            out.append("_")
        out.append(ch.lower())
    return "".join(out)

def _resource_name(model: type) -> str:
    return getattr(model, "__resource__", None) or getattr(model, "__tablename__", None) or _snake(model.__name__)

def _default_prefix(model: type) -> str:
    return f"/{_resource_name(model)}"

def _has_include_router(obj: Any) -> bool:
    return hasattr(obj, "include_router") and callable(getattr(obj, "include_router"))

def _mount_router(app_or_router: Any, router: Any, *, prefix: str) -> None:
    """
    Best-effort mount onto a FastAPI app or APIRouter.
    If not available, we still attach router under api.routers for later use.
    """
    if app_or_router is None:
        return
    try:
        if _has_include_router(app_or_router):
            app_or_router.include_router(router, prefix=prefix)  # FastAPI / APIRouter
    except Exception:
        logger.exception("Failed to mount router at %s", prefix)


def _ensure_api_ns(api: ApiLike) -> None:
    """
    Ensure containers exist on the api facade object.
    """
    for attr, default in (
        ("models", {}),
        ("schemas", SimpleNamespace()),
        ("handlers", SimpleNamespace()),
        ("hooks", SimpleNamespace()),
        ("rpc", SimpleNamespace()),
        ("rest", SimpleNamespace()),
        ("routers", {}),
        ("columns", {}),
        ("table_config", {}),
        ("core", SimpleNamespace()),  # helper method proxies
    ):
        if not hasattr(api, attr):
            setattr(api, attr, default)


# ───────────────────────────────────────────────────────────────────────────────
# Resource proxy: api.core.<ModelName>.<alias>(payload, *, db, request=None, ctx=None)
# ───────────────────────────────────────────────────────────────────────────────

class _ResourceProxy:
    """
    Lightweight dynamic proxy that forwards calls to model.rpc.<alias>.
    We resolve methods lazily so new/changed ops after rebinds are visible.
    """

    __slots__ = ("_model",)

    def __init__(self, model: type) -> None:
        self._model = model

    def __repr__(self) -> str:
        return f"<ResourceProxy {self._model.__name__}>"

    def __getattr__(self, alias: str) -> Callable[..., Awaitable[Any]]:
        rpc_ns = getattr(self._model, "rpc", None)
        target = getattr(rpc_ns, alias, None)
        if target is None:
            raise AttributeError(f"{self._model.__name__} has no RPC method '{alias}'")

        async def _call(payload: Any = None, *, db: Any, request: Any = None, ctx: Optional[Dict[str, Any]] = None) -> Any:
            return await target(payload, db=db, request=request, ctx=ctx)

        _call.__name__ = f"{self._model.__name__}.{alias}"
        _call.__qualname__ = _call.__name__
        _call.__doc__ = f"Helper for RPC call {self._model.__name__}.{alias}"
        return _call


# ───────────────────────────────────────────────────────────────────────────────
# Inclusion logic
# ───────────────────────────────────────────────────────────────────────────────

def _attach_to_api(api: ApiLike, model: type) -> None:
    """
    Attach the model’s bound namespaces to the api facade.
    """
    _ensure_api_ns(api)

    mname = model.__name__

    # Index model object
    api.models[mname] = model

    # Direct references to model namespaces
    setattr(api.schemas, mname, getattr(model, "schemas", SimpleNamespace()))
    setattr(api.handlers, mname, getattr(model, "handlers", SimpleNamespace()))
    setattr(api.hooks, mname, getattr(model, "hooks", SimpleNamespace()))
    setattr(api.rpc, mname, getattr(model, "rpc", SimpleNamespace()))
    # rest (router lives on model.rest.router)
    rest_ns = getattr(api, "rest")
    setattr(rest_ns, mname, SimpleNamespace(router=getattr(getattr(model, "rest", SimpleNamespace()), "router", None)))
    # also keep a flat routers dict for quick access
    api.routers[mname] = getattr(getattr(model, "rest", SimpleNamespace()), "router", None)

    # Table metadata
    api.columns[mname] = tuple(getattr(model, "columns", ()))
    api.table_config[mname] = dict(getattr(model, "table_config", {}) or {})

    # Core helper proxy
    setattr(api.core, mname, _ResourceProxy(model))


def include_model(
    api: ApiLike,
    model: type,
    *,
    app: Any | None = None,
    prefix: str | None = None,
    mount_router: bool = True,
) -> Tuple[type, Any]:
    """
    Bind a model (if not already bound), mount its REST router, and attach all namespaces to `api`.

    Args:
        api: An arbitrary facade object; we’ll attach containers onto it if missing.
        model: The SQLAlchemy model (table class).
        app: Optional FastAPI app or APIRouter (anything with `include_router`).
             If not provided, we attempt to use `api.app` or `api.router` if present.
        prefix: Optional mount prefix; defaults to `/{resource}`.
        mount_router: If False, we won’t mount; we still attach the router under `api.rest`/`api.routers`.

    Returns:
        (model, router) – the model class and its APIRouter (or None if not present).
    """
    # 1) Build/bind model namespaces (idempotent)
    _binder.bind(model)

    # 2) Pick a router & mount prefix
    router = getattr(getattr(model, "rest", SimpleNamespace()), "router", None)
    if prefix is None:
        prefix = _default_prefix(model)

    # 3) Mount if requested and possible
    target_app = app or getattr(api, "app", None) or getattr(api, "router", None)
    if mount_router and router is not None:
        _mount_router(target_app, router, prefix=prefix)

    # 4) Attach all namespaces onto api
    _attach_to_api(api, model)

    logger.debug("bindings.api: included %s at prefix %s", model.__name__, prefix)
    return model, router


def include_models(
    api: ApiLike,
    models: Sequence[type],
    *,
    app: Any | None = None,
    base_prefix: str | None = None,
    mount_router: bool = True,
) -> Dict[str, Any]:
    """
    Convenience helper to include multiple models.
    Each model is mounted at `{base_prefix}/{resource}` when base_prefix is provided.
    """
    results: Dict[str, Any] = {}
    for mdl in models:
        px = (base_prefix.rstrip("/") if base_prefix else "") + _default_prefix(mdl)
        _, router = include_model(api, mdl, app=app, prefix=px, mount_router=mount_router)
        results[mdl.__name__] = router
    return results


# ───────────────────────────────────────────────────────────────────────────────
# Optional: generic RPC dispatcher on the api facade
# ───────────────────────────────────────────────────────────────────────────────

async def rpc_call(
    api: ApiLike,
    model_or_name: Union[type, str],
    method: str,
    payload: Any = None,
    *,
    db: Any,
    request: Any = None,
    ctx: Optional[Dict[str, Any]] = None,
) -> Any:
    """
    Call a registered RPC method by (model, method) pair.
    `model_or_name` may be a model class or its name.
    """
    _ensure_api_ns(api)

    if isinstance(model_or_name, str):
        mdl = api.models.get(model_or_name)
        if mdl is None:
            raise KeyError(f"Unknown model '{model_or_name}'")
    else:
        mdl = model_or_name

    fn = getattr(getattr(mdl, "rpc", SimpleNamespace()), method, None)
    if fn is None:
        raise AttributeError(f"{getattr(mdl, '__name__', mdl)} has no RPC method '{method}'")

    return await fn(payload, db=db, request=request, ctx=ctx)


__all__ = ["include_model", "include_models", "rpc_call"]
