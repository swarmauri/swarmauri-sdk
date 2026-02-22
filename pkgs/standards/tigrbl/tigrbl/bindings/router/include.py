from __future__ import annotations

import logging
from types import SimpleNamespace
from typing import Any, Dict, Sequence, Tuple

from .common import (
    RouterLike,
    _default_prefix,
    _ensure_router_ns,
    _has_include_router,
    _mount_router,
    _resource_name,
)
from .resource_proxy import _ResourceProxy
from .. import model as _binder
from ...config.constants import (
    TIGRBL_AUTH_DEP_ATTR,
    TIGRBL_AUTHORIZE_ATTR,
    TIGRBL_GET_DB_ATTR,
    TIGRBL_REST_DEPENDENCIES_ATTR,
    TIGRBL_RPC_DEPENDENCIES_ATTR,
    TIGRBL_ALLOW_ANON_ATTR,
)
from ...engine import resolver as _resolver

logger = logging.getLogger("uvicorn")
logger.debug("Loaded module v3/bindings/router/include")


def _coerce_model_columns(columns: Any) -> Tuple[str, ...]:
    if isinstance(columns, SimpleNamespace):
        return tuple(columns.__dict__.keys())
    if isinstance(columns, dict):
        return tuple(columns.keys())
    if isinstance(columns, str):
        return (columns,)
    try:
        return tuple(columns)
    except TypeError:
        return ()


# --- keep as helper, no behavior change to transports/kernel ---
def _seed_security_and_deps(router: Any, model: type) -> None:
    """
    Copy ROUTER-level dependency hooks onto the model so downstream binders can use them.
    - __tigrbl_get_db__             : DB dep (ASGI Depends-compatible)
    - __tigrbl_auth_dep__           : auth dependency (returns user or raises 401)
    - __tigrbl_authorize__          : callable(request, model, alias, payload, user)→None/raise 403
    - __tigrbl_rest_dependencies__  : list of extra dependencies for REST (e.g., rate-limits)
    - __tigrbl_rpc_dependencies__   : list of extra dependencies for JSON-RPC router
    """
    # DB deps
    prov = _resolver.resolve_provider(router=router)
    if prov is not None:
        logger.debug("Resolved provider for %s", model.__name__)
        setattr(model, TIGRBL_GET_DB_ATTR, prov.get_db)
    else:
        logger.debug("No provider resolved for %s", model.__name__)

    # Authn (prefer optional dep when available)
    auth_dep = None
    if getattr(router, "_optional_authn_dep", None):
        auth_dep = router._optional_authn_dep
        logger.debug("Using optional auth dependency for %s", model.__name__)
    elif getattr(router, "_allow_anon", True) is False and getattr(router, "_authn", None):
        auth_dep = router._authn
        logger.debug("Using required auth dependency for %s", model.__name__)
    elif getattr(router, "_authn", None):
        auth_dep = router._authn
        logger.debug("Using default auth dependency for %s", model.__name__)
    if auth_dep is not None:
        setattr(model, TIGRBL_AUTH_DEP_ATTR, auth_dep)
    else:
        logger.debug("No auth dependency configured for %s", model.__name__)

    # Allow anonymous verbs
    allow_attr = getattr(model, TIGRBL_ALLOW_ANON_ATTR, None)
    if allow_attr:
        verbs = allow_attr() if callable(allow_attr) else allow_attr
        logger.debug("Allowing anonymous verbs %s for %s", verbs, model.__name__)
        for v in verbs:
            router._allow_anon_ops.add(f"{model.__name__}.{v}")
    else:
        logger.debug("No anonymous verbs for %s", model.__name__)

    # Authz
    if getattr(router, "_authorize", None):
        setattr(model, TIGRBL_AUTHORIZE_ATTR, router._authorize)
        logger.debug("Authorization hook attached for %s", model.__name__)
    else:
        logger.debug("No authorization hook for %s", model.__name__)

    # Extra deps (router-level only; never part of kernel plan)
    rest_deps: list[Any] = []
    if getattr(router, "security_deps", None):
        rest_deps.extend(list(getattr(router, "security_deps", ()) or ()))
    if getattr(router, "rest_dependencies", None):
        rest_deps.extend(list(router.rest_dependencies))
    if rest_deps:
        setattr(model, TIGRBL_REST_DEPENDENCIES_ATTR, rest_deps)
        logger.debug("REST dependencies seeded for %s", model.__name__)
    else:
        logger.debug("No REST dependencies for %s", model.__name__)
    if getattr(router, "rpc_dependencies", None):
        setattr(model, TIGRBL_RPC_DEPENDENCIES_ATTR, list(router.rpc_dependencies))
        logger.debug("RPC dependencies seeded for %s", model.__name__)
    else:
        logger.debug("No RPC dependencies for %s", model.__name__)


def _attach_to_router(router: RouterLike, model: type) -> None:
    """
    Attach the model’s bound namespaces to the router facade.
    """
    _ensure_router_ns(router)

    mname = model.__name__
    rname = _resource_name(model)
    rtitle = rname[:1].upper() + rname[1:]
    logger.debug("Attaching model %s as resource '%s'", mname, rname)

    # Index model object
    router.models[mname] = model
    router.tables[mname] = getattr(model, "__table__", None)

    # Direct references to model namespaces
    setattr(router.schemas, mname, getattr(model, "schemas", SimpleNamespace()))
    setattr(router.handlers, mname, getattr(model, "handlers", SimpleNamespace()))
    setattr(router.hooks, mname, getattr(model, "hooks", SimpleNamespace()))
    rpc_ns = getattr(model, "rpc", SimpleNamespace())
    setattr(router.rpc, mname, rpc_ns)
    if rtitle != mname:
        setattr(router.rpc, rtitle, rpc_ns)
        logger.debug("Registered RPC namespace alias '%s'", rtitle)
    # rest (router lives on model.rest.router)
    rest_ns = getattr(router, "rest")
    setattr(
        rest_ns,
        mname,
        SimpleNamespace(
            router=getattr(getattr(model, "rest", SimpleNamespace()), "router", None)
        ),
    )
    # also keep a flat routers dict for quick access
    router.routers[mname] = getattr(
        getattr(model, "rest", SimpleNamespace()), "router", None
    )

    # Table metadata (introspection only)
    router.columns[mname] = _coerce_model_columns(getattr(model, "columns", ()))
    router.table_config[mname] = dict(getattr(model, "table_config", {}) or {})

    # Core helper proxies (now aware of ROUTER for DB resolution precedence)
    core_proxy = _ResourceProxy(model, router=router)
    setattr(router.core, mname, core_proxy)
    if rtitle != mname:
        setattr(router.core, rtitle, core_proxy)
    core_raw_proxy = _ResourceProxy(model, serialize=False, router=router)
    setattr(router.core_raw, mname, core_raw_proxy)
    if rtitle != mname:
        setattr(router.core_raw, rtitle, core_raw_proxy)


def include_table(
    router: RouterLike,
    model: type,
    *,
    app: Any | None = None,
    prefix: str | None = None,
    mount_router: bool = True,
) -> Tuple[type, Any]:
    """
    Bind a model (if not already bound), mount its REST router, and attach all namespaces to `router`.

    Args:
        router: An arbitrary facade object; we’ll attach containers onto it if missing.
        model: The SQLAlchemy model (table class).
        app: Optional ASGI app or Router (anything with `include_router`).
             Routers are always mounted on `router.router`; if provided, we also
             mount onto this `app` (or `router.app` when not given).
        prefix: Optional mount prefix. When None, defaults to `/{ModelClassName}` or
                `/{__resource__}` if set on the model.
        mount_router: If False, we skip mounting onto the host app but still bind
            the router under `router.router`/`router.rest`/`router.routers`.

    Returns:
        (model, router) – the model class and its Router (or None if not present).
    """
    logger.debug("Including table %s", model.__name__)

    # If another test or call disposed the SQLAlchemy registry, previously
    # imported models lose their table mapping.  Re-map on demand so tests that
    # run after a registry dispose still have working models.
    if not hasattr(model, "__table__"):
        try:  # pragma: no cover - defensive path exercised in tests
            from ...table import Base
            from ...table._base import _materialize_colspecs_to_sqla

            # Recreate mapped_column attributes from ColumnSpecs then map
            _materialize_colspecs_to_sqla(model)
            Base.registry.map_declaratively(model)
        except Exception:  # pragma: no cover
            logger.debug("Failed to remap model %s", model.__name__, exc_info=True)

    # 0) seed deps/security so binders can see them (transport-level only)
    _seed_security_and_deps(router, model)

    # 1) Build/bind model namespaces (idempotent)
    _binder.bind(model, router=router)

    # 2) Pick a router & mount prefix
    router = getattr(getattr(model, "rest", SimpleNamespace()), "router", None)
    if prefix is None:
        prefix = _default_prefix(model)
        logger.debug("Computed default prefix '%s' for %s", prefix, model.__name__)
    else:
        logger.debug("Using provided prefix '%s' for %s", prefix, model.__name__)

    # 3) Always bind model router to the ROUTER object when possible
    root_router = router if _has_include_router(router) else getattr(router, "router", None)
    if router is not None:
        logger.debug("Mounting model router for %s on router", model.__name__)
        _mount_router(root_router, router, prefix=prefix)
    else:
        logger.debug("Model %s has no router to mount", model.__name__)

    # Optionally mount onto a host app
    target_app = app or getattr(router, "app", None)
    if mount_router and router is not None:
        logger.debug("Mounting router for %s on host app", model.__name__)
        _mount_router(target_app, router, prefix=prefix)    
    else:
        logger.debug(
            "Skipping host app mount for %s (mount_router=%s, router=%s)",
            model.__name__,
            mount_router,
            router is not None,
        )

    # 4) Attach all namespaces onto router
    _attach_to_router(router, model)

    logger.debug("bindings.router: included %s at prefix %s", model.__name__, prefix)
    return model, router


def include_tables(
    router: RouterLike,
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
    logger.debug("Including %d tables", len(models))
    results: Dict[str, Any] = {}
    for mdl in models:
        px = base_prefix.rstrip("/") if base_prefix else None
        logger.debug("Including model %s with base prefix %s", mdl.__name__, px)
        _, router = include_table(
            router, mdl, app=app, prefix=px, mount_router=mount_router
        )
        results[mdl.__name__] = router
    logger.debug("Finished including tables")
    return results
