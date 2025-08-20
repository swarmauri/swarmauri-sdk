# autoapi/v3/bindings/api.py
from __future__ import annotations

import logging
from types import SimpleNamespace
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Optional,
    Sequence,
    Tuple,
    Union,
)

from . import model as _binder  # bind(model) → builds/attaches namespaces
from .rpc import _coerce_payload, _get_phase_chains, _validate_input
from ..config.constants import (
    AUTOAPI_AUTH_DEP_ATTR,
    AUTOAPI_AUTHORIZE_ATTR,
    AUTOAPI_GET_ASYNC_DB_ATTR,
    AUTOAPI_GET_DB_ATTR,
    AUTOAPI_REST_DEPENDENCIES_ATTR,
    AUTOAPI_RPC_DEPENDENCIES_ATTR,
)
from ..runtime import executor as _executor

logger = logging.getLogger(__name__)

# Public type for the API facade object users pass to include_model(...)
ApiLike = Any

# ───────────────────────────────────────────────────────────────────────────────
# Helpers: resource/prefix, namespaces, router mounting
# ───────────────────────────────────────────────────────────────────────────────


def _resource_name(model: type) -> str:
    """
    Compute the API resource segment.

    Policy:
      - Prefer explicit `__resource__` when present (caller-controlled).
      - Otherwise, use the model *class name* exactly as written.
      - DO NOT use `__tablename__` here (strictly DB-only per project policy).
    """
    return getattr(model, "__resource__", model.__name__)


def _default_prefix(model: type) -> str:
    # Router prefix will be '/<ModelClassName>' unless __resource__ overrides it.
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
    """Dynamic proxy that executes core operations without output serialization."""

    __slots__ = ("_model",)

    def __init__(self, model: type) -> None:  # pragma: no cover - trivial
        self._model = model

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<ResourceProxy {self._model.__name__}>"

    def __getattr__(self, alias: str) -> Callable[..., Awaitable[Any]]:
        handlers_root = getattr(self._model, "handlers", None)
        h_alias = getattr(handlers_root, alias, None) if handlers_root else None
        if h_alias is None or not hasattr(h_alias, "core"):
            raise AttributeError(f"{self._model.__name__} has no core method '{alias}'")

        async def _call(
            payload: Any = None,
            *,
            db: Any,
            request: Any = None,
            ctx: Optional[Dict[str, Any]] = None,
        ) -> Any:
            raw_payload = _coerce_payload(payload)
            norm_payload = _validate_input(self._model, alias, alias, raw_payload)
            base_ctx: Dict[str, Any] = dict(ctx or {})
            base_ctx.setdefault("payload", norm_payload)
            base_ctx.setdefault("db", db)
            if request is not None:
                base_ctx.setdefault("request", request)
            base_ctx.setdefault(
                "env",
                SimpleNamespace(
                    method=alias, params=norm_payload, target=alias, model=self._model
                ),
            )
            phases = _get_phase_chains(self._model, alias)
            return await _executor._invoke(
                request=request,
                db=db,
                phases=phases,
                ctx=base_ctx,
            )

        _call.__name__ = f"{self._model.__name__}.{alias}"
        _call.__qualname__ = _call.__name__
        _call.__doc__ = f"Helper for core call {self._model.__name__}.{alias}"
        return _call


# --- keep as helper, no behavior change to transports/kernel ---
def _seed_security_and_deps(api: Any, model: type) -> None:
    """
    Copy API-level dependency hooks onto the model so downstream binders can use them.
    - __autoapi_get_db__             : sync DB dep (FastAPI Depends-compatible)
    - __autoapi_get_async_db__       : async DB dep
    - __autoapi_auth_dep__           : auth dependency (returns user or raises 401)
    - __autoapi_authorize__          : callable(request, model, alias, payload, user)→None/raise 403
    - __autoapi_rest_dependencies__  : list of extra dependencies for REST (e.g., rate-limits)
    - __autoapi_rpc_dependencies__   : list of extra dependencies for JSON-RPC router
    """
    # DB deps
    if getattr(api, "get_db", None):
        setattr(model, AUTOAPI_GET_DB_ATTR, api.get_db)
    if getattr(api, "get_async_db", None):
        setattr(model, AUTOAPI_GET_ASYNC_DB_ATTR, api.get_async_db)

    # Authn (prefer required if allow_anon is False)
    auth_dep = None
    if getattr(api, "_allow_anon", True) is False and getattr(api, "_authn", None):
        auth_dep = api._authn
    elif getattr(api, "_optional_authn_dep", None):
        auth_dep = api._optional_authn_dep
    elif getattr(api, "_authn", None):
        auth_dep = api._authn
    if auth_dep is not None:
        setattr(model, AUTOAPI_AUTH_DEP_ATTR, auth_dep)

    # Authz
    if getattr(api, "_authorize", None):
        setattr(model, AUTOAPI_AUTHORIZE_ATTR, api._authorize)

    # Extra deps (router-level only; never part of runtime plan)
    if getattr(api, "rest_dependencies", None):
        setattr(model, AUTOAPI_REST_DEPENDENCIES_ATTR, list(api.rest_dependencies))
    if getattr(api, "rpc_dependencies", None):
        setattr(model, AUTOAPI_RPC_DEPENDENCIES_ATTR, list(api.rpc_dependencies))


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
    setattr(
        rest_ns,
        mname,
        SimpleNamespace(
            router=getattr(getattr(model, "rest", SimpleNamespace()), "router", None)
        ),
    )
    # also keep a flat routers dict for quick access
    api.routers[mname] = getattr(
        getattr(model, "rest", SimpleNamespace()), "router", None
    )

    # Table metadata (introspection only)
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
        prefix: Optional mount prefix. When None, defaults to `/{ModelClassName}` or
                `/{__resource__}` if set on the model.
        mount_router: If False, we won’t mount; we still attach the router under `api.rest`/`api.routers`.

    Returns:
        (model, router) – the model class and its APIRouter (or None if not present).
    """
    # 0) seed deps/security so binders can see them (transport-level only)
    _seed_security_and_deps(api, model)

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

    If ``base_prefix`` is provided, each model's router is mounted under that
    prefix. The model router itself already has its own `/{resource}` prefix.
    """
    results: Dict[str, Any] = {}
    for mdl in models:
        px = base_prefix.rstrip("/") if base_prefix else None
        _, router = include_model(
            api, mdl, app=app, prefix=px, mount_router=mount_router
        )
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
        raise AttributeError(
            f"{getattr(mdl, '__name__', mdl)} has no RPC method '{method}'"
        )

    return await fn(payload, db=db, request=request, ctx=ctx)


__all__ = ["include_model", "include_models", "rpc_call"]
