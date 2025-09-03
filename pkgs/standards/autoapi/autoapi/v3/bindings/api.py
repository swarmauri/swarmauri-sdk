# autoapi/v3/bindings/api.py
from __future__ import annotations

import logging
from types import SimpleNamespace
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Union,
)

from . import model as _binder  # bind(model) → builds/attaches namespaces
from .rpc import _coerce_payload, _get_phase_chains, _validate_input, _serialize_output
from ..config.constants import (
    AUTOAPI_AUTH_DEP_ATTR,
    AUTOAPI_AUTHORIZE_ATTR,
    AUTOAPI_GET_DB_ATTR,
    AUTOAPI_REST_DEPENDENCIES_ATTR,
    AUTOAPI_RPC_DEPENDENCIES_ATTR,
    AUTOAPI_ALLOW_ANON_ATTR,
)
from ..runtime import executor as _executor

# NEW: engine resolver (strict precedence: op > model > api > app)
from ..engine import resolver as _resolver  # acquire(api=?, model=?, op_alias=?)

logger = logging.getLogger(__name__)


class AttrDict(dict):
    """Dictionary providing attribute-style access."""

    def __getattr__(self, item: str) -> Any:  # pragma: no cover - trivial
        try:
            return self[item]
        except KeyError as e:  # pragma: no cover - debug aid
            raise AttributeError(item) from e

    def __setattr__(self, key: str, value: Any) -> None:  # pragma: no cover - trivial
        self[key] = value


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
      - Otherwise, use the model *class name* in lowercase.
      - DO NOT use `__tablename__` here (strictly DB-only per project policy).
    """
    return getattr(model, "__resource__", model.__name__.lower())


def _default_prefix(model: type) -> str:
    """Default mount prefix for a model router.

    Historically routers were mounted under ``/{resource}``, resulting in
    duplicated path segments such as ``/item/item``.  To expose REST endpoints
    under ``/item`` we now mount routers at the application root by default.
    """
    return ""


def _has_include_router(obj: Any) -> bool:
    return hasattr(obj, "include_router") and callable(getattr(obj, "include_router"))


def _mount_router(app_or_router: Any, router: Any, *, prefix: str) -> None:
    """
    Best-effort mount onto a FastAPI app or Router.
    If not available, we still attach router under api.routers for later use.
    """
    if app_or_router is None:
        return
    try:
        if _has_include_router(app_or_router):
            app_or_router.include_router(router, prefix=prefix)  # FastAPI / Router
    except Exception:
        logger.exception("Failed to mount router at %s", prefix)


def _ensure_api_ns(api: ApiLike) -> None:
    """
    Ensure containers exist on the api facade object.
    """
    for attr, default in (
        ("models", {}),
        ("tables", AttrDict()),
        ("schemas", SimpleNamespace()),
        ("handlers", SimpleNamespace()),
        ("hooks", SimpleNamespace()),
        ("rpc", SimpleNamespace()),
        ("rest", SimpleNamespace()),
        ("routers", {}),
        ("columns", {}),
        ("table_config", {}),
        ("core", SimpleNamespace()),  # helper method proxies
        ("core_raw", SimpleNamespace()),
    ):
        if not hasattr(api, attr):
            setattr(api, attr, default)


class _ResourceProxy:
    """Dynamic proxy that executes core operations."""

    __slots__ = ("_model", "_serialize", "_api")

    def __init__(
        self, model: type, *, serialize: bool = True, api: Any = None
    ) -> None:  # pragma: no cover - trivial
        self._model = model
        self._serialize = serialize
        self._api = api

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
            db: Any | None = None,
            request: Any = None,
            ctx: Optional[Dict[str, Any]] = None,
        ) -> Any:
            raw_payload = _coerce_payload(payload)
            if alias == "bulk_delete" and not isinstance(raw_payload, Mapping):
                raw_payload = {"ids": raw_payload}
            norm_payload = _validate_input(self._model, alias, alias, raw_payload)

            base_ctx: Dict[str, Any] = dict(ctx or {})
            base_ctx.setdefault("payload", norm_payload)
            if request is not None:
                base_ctx.setdefault("request", request)
            base_ctx.setdefault(
                "env",
                SimpleNamespace(
                    method=alias, params=norm_payload, target=alias, model=self._model
                ),
            )
            if self._serialize:
                base_ctx.setdefault(
                    "response_serializer",
                    lambda r: _serialize_output(self._model, alias, alias, r),
                )
            else:
                base_ctx.setdefault("response_serializer", lambda r: r)

            # Acquire DB if one was not explicitly provided (op > model > api > app)
            _release_db = None
            if db is None:
                try:
                    db, _release_db = _resolver.acquire(
                        api=self._api, model=self._model, op_alias=alias
                    )
                except Exception:
                    logger.exception(
                        "DB acquire failed for %s.%s; no default configured?",
                        self._model.__name__,
                        alias,
                    )
                    raise

            base_ctx.setdefault("db", db)
            phases = _get_phase_chains(self._model, alias)
            try:
                return await _executor._invoke(
                    request=request,
                    db=db,
                    phases=phases,
                    ctx=base_ctx,
                )
            finally:
                if _release_db is not None:
                    try:
                        _release_db()
                    except Exception:
                        logger.debug(
                            "Non-fatal: error releasing acquired DB session",
                            exc_info=True,
                        )

        _call.__name__ = f"{self._model.__name__}.{alias}"
        _call.__qualname__ = _call.__name__
        _call.__doc__ = f"Helper for core call {self._model.__name__}.{alias}"
        return _call


# --- keep as helper, no behavior change to transports/kernel ---
def _seed_security_and_deps(api: Any, model: type) -> None:
    """
    Copy API-level dependency hooks onto the model so downstream binders can use them.
    - __autoapi_get_db__             : DB dep (FastAPI Depends-compatible)
    - __autoapi_auth_dep__           : auth dependency (returns user or raises 401)
    - __autoapi_authorize__          : callable(request, model, alias, payload, user)→None/raise 403
    - __autoapi_rest_dependencies__  : list of extra dependencies for REST (e.g., rate-limits)
    - __autoapi_rpc_dependencies__   : list of extra dependencies for JSON-RPC router
    """
    # DB deps
    prov = _resolver.resolve_provider(api=api)
    if prov is not None:
        setattr(model, AUTOAPI_GET_DB_ATTR, prov.get_db)

    # Authn (prefer optional dep when available)
    auth_dep = None
    if getattr(api, "_optional_authn_dep", None):
        auth_dep = api._optional_authn_dep
    elif getattr(api, "_allow_anon", True) is False and getattr(api, "_authn", None):
        auth_dep = api._authn
    elif getattr(api, "_authn", None):
        auth_dep = api._authn
    if auth_dep is not None:
        setattr(model, AUTOAPI_AUTH_DEP_ATTR, auth_dep)

    # Allow anonymous verbs
    allow_attr = getattr(model, AUTOAPI_ALLOW_ANON_ATTR, None)
    if allow_attr:
        verbs = allow_attr() if callable(allow_attr) else allow_attr
        for v in verbs:
            api._allow_anon_ops.add(f"{model.__name__}.{v}")

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
    rname = _resource_name(model)
    rtitle = rname[:1].upper() + rname[1:]

    # Index model object
    api.models[mname] = model
    api.tables[mname] = getattr(model, "__table__", None)

    # Direct references to model namespaces
    setattr(api.schemas, mname, getattr(model, "schemas", SimpleNamespace()))
    setattr(api.handlers, mname, getattr(model, "handlers", SimpleNamespace()))
    setattr(api.hooks, mname, getattr(model, "hooks", SimpleNamespace()))
    rpc_ns = getattr(model, "rpc", SimpleNamespace())
    setattr(api.rpc, mname, rpc_ns)
    if rtitle != mname:
        setattr(api.rpc, rtitle, rpc_ns)
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

    # Core helper proxies (now aware of API for DB resolution precedence)
    core_proxy = _ResourceProxy(model, api=api)
    setattr(api.core, mname, core_proxy)
    if rtitle != mname:
        setattr(api.core, rtitle, core_proxy)

    core_raw_proxy = _ResourceProxy(model, serialize=False, api=api)
    setattr(api.core_raw, mname, core_raw_proxy)
    if rtitle != mname:
        setattr(api.core_raw, rtitle, core_raw_proxy)


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
        app: Optional FastAPI app or Router (anything with `include_router`).
             Routers are always mounted on `api.router`; if provided, we also
             mount onto this `app` (or `api.app` when not given).
        prefix: Optional mount prefix. When None, defaults to `/{ModelClassName}` or
                `/{__resource__}` if set on the model.
        mount_router: If False, we skip mounting onto the host app but still bind
            the router under `api.router`/`api.rest`/`api.routers`.

    Returns:
        (model, router) – the model class and its Router (or None if not present).
    """
    # 0) seed deps/security so binders can see them (transport-level only)
    _seed_security_and_deps(api, model)

    # 1) Build/bind model namespaces (idempotent)
    _binder.bind(model)

    # 2) Pick a router & mount prefix
    router = getattr(getattr(model, "rest", SimpleNamespace()), "router", None)
    if prefix is None:
        prefix = _default_prefix(model)

    # 3) Always bind model router to the API object when possible
    root_router = api if _has_include_router(api) else getattr(api, "router", None)
    if router is not None:
        _mount_router(root_router, router, prefix=prefix)

    # Optionally mount onto a host app
    target_app = app or getattr(api, "app", None)
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
    db: Any | None = None,
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

    # Acquire DB if not explicitly provided (op > model > api > app)
    _release_db = None
    if db is None:
        try:
            db, _release_db = _resolver.acquire(api=api, model=mdl, op_alias=method)
        except Exception:
            logger.exception(
                "DB acquire failed for rpc_call %s.%s; no default configured?",
                getattr(mdl, "__name__", mdl),
                method,
            )
            raise

    try:
        return await fn(payload, db=db, request=request, ctx=ctx)
    finally:
        if _release_db is not None:
            try:
                _release_db()
            except Exception:
                logger.debug(
                    "Non-fatal: error releasing acquired DB session (rpc_call)",
                    exc_info=True,
                )


__all__ = ["include_model", "include_models", "rpc_call"]
