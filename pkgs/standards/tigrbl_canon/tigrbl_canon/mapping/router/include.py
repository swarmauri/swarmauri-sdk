from __future__ import annotations

import logging
from dataclasses import replace
from types import SimpleNamespace
from typing import Any, Dict, Sequence, Tuple

from .common import (
    RouterLike,
    _default_prefix,
    _ensure_router_ns,
    _has_include_router,
    _mount_router,
)
from .resource_proxy import _ResourceProxy
from .. import model as _binder
from ..column_mro_collect import mro_collect_columns
from tigrbl.config.constants import (
    TIGRBL_AUTH_DEP_ATTR,
    TIGRBL_GET_DB_ATTR,
    TIGRBL_REST_DEPENDENCIES_ATTR,
    TIGRBL_RPC_DEPENDENCIES_ATTR,
    TIGRBL_ALLOW_ANON_ATTR,
)
from tigrbl.mapping import engine_resolver as _resolver
from ..model_helpers import _OpSpecGroup

logger = logging.getLogger("uvicorn")
logger.debug("Loaded module v3/mapping/router/include")


def _build_router_rpc_namespace(router: RouterLike, model: type) -> SimpleNamespace:
    """Return router-scoped RPC methods that execute and serialize results."""
    from .rpc import rpc_call as _rpc_call

    model_rpc_ns = getattr(model, "rpc", SimpleNamespace())
    router_rpc_ns = SimpleNamespace()

    for attr_name, attr_value in vars(model_rpc_ns).items():
        if not callable(attr_value):
            setattr(router_rpc_ns, attr_name, attr_value)
            continue

        async def _router_rpc_method(
            payload: Any = None,
            *,
            db: Any | None = None,
            request: Any = None,
            ctx: Dict[str, Any] | None = None,
            _alias: str = attr_name,
        ) -> Any:
            return await _rpc_call(
                router,
                model,
                _alias,
                payload,
                db=db,
                request=request,
                ctx=ctx,
            )

        _router_rpc_method.__name__ = f"rpc_{model.__name__}_{attr_name}"
        _router_rpc_method.__qualname__ = _router_rpc_method.__name__
        _router_rpc_method.__doc__ = (
            f"Router RPC method for {model.__name__}.{attr_name}"
        )
        setattr(router_rpc_ns, attr_name, _router_rpc_method)

    return router_rpc_ns


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
def _mark_required_auth_dependency(dep: Any) -> Any:
    """Tag an auth dependency as required so runtime can reject missing auth."""
    try:
        setattr(dep, "__tigrbl_require_auth__", True)
        return dep
    except Exception:
        pass

    async def _required_auth_wrapper(*args: Any, **kwargs: Any) -> Any:
        rv = dep(*args, **kwargs)
        if hasattr(rv, "__await__"):
            rv = await rv
        return rv

    setattr(_required_auth_wrapper, "__tigrbl_require_auth__", True)
    setattr(_required_auth_wrapper, "__wrapped__", dep)
    return _required_auth_wrapper


def _seed_security_and_deps(router: Any, model: type) -> None:
    """
    Copy API-level dependency hooks onto the model so downstream binders can use them.
    - __tigrbl_get_db__             : DB dep (ASGI Depends-compatible)
    - __tigrbl_auth_dep__           : auth dependency (returns user or raises 401)
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
    elif getattr(router, "_allow_anon", True) is False and getattr(
        router, "_authn", None
    ):
        auth_dep = router._authn
        logger.debug("Using required auth dependency for %s", model.__name__)
    elif getattr(router, "_authn", None):
        auth_dep = router._authn
        logger.debug("Using default auth dependency for %s", model.__name__)
    if auth_dep is not None and getattr(router, "_allow_anon", True) is False:
        auth_dep = _mark_required_auth_dependency(auth_dep)

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

    runtime_secdeps: tuple[Any, ...] = ()
    if auth_dep is not None:
        runtime_secdeps = runtime_secdeps + (auth_dep,)

    authorize_dep = _make_authorize_secdep(router)
    if authorize_dep is not None:
        runtime_secdeps = runtime_secdeps + (authorize_dep,)

    if authorize_dep is not None:
        logger.debug("Authorization secdep attached for %s", model.__name__)
    else:
        logger.debug("No authorization secdep for %s", model.__name__)

    # Extra deps (router-level only; never part of kernel plan)
    rest_deps: list[Any] = []
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


def _inject_runtime_secdeps(
    model: type, runtime_secdeps: tuple[Any, ...], allow_anon: set[Any]
) -> None:
    if not runtime_secdeps:
        return
    ops_ns = getattr(model, "ops", None)
    by_alias = getattr(ops_ns, "by_alias", None)
    if not isinstance(by_alias, dict):
        return

    for alias, specs in list(by_alias.items()):
        patched_specs = []
        changed = False
        for sp in tuple(specs or ()):  # type: ignore[arg-type]
            exempt = sp.alias in allow_anon or sp.target in allow_anon
            if exempt:
                patched_specs.append(sp)
                continue
            secdeps = tuple(getattr(sp, "secdeps", ()) or ())
            missing = tuple(dep for dep in runtime_secdeps if dep not in secdeps)
            if not missing:
                patched_specs.append(sp)
                continue
            patched_specs.append(replace(sp, secdeps=((*missing, *secdeps))))
            changed = True
        if changed:
            by_alias[alias] = _OpSpecGroup(tuple(patched_specs))


def _make_authorize_secdep(router: Any) -> Any | None:
    authorize = getattr(router, "_authorize", None)
    if not callable(authorize):
        return None

    async def _authorize_secdep(ctx: Any) -> None:
        ctx_map = ctx if isinstance(ctx, dict) else {}
        request = getattr(ctx, "request", None) or ctx_map.get("request")
        model = getattr(ctx, "model", None) or ctx_map.get("model")
        alias = getattr(ctx, "op", None) or ctx_map.get("op") or ctx_map.get("method")
        payload = getattr(ctx, "payload", None) or ctx_map.get("payload")
        user = (
            getattr(ctx, "auth_context", None)
            or ctx_map.get("auth_context")
            or getattr(getattr(request, "state", None), "user", None)
        )

        rv = authorize(request, model, alias, payload, user)
        if hasattr(rv, "__await__"):
            rv = await rv
        if rv is False:
            from ...errors import ForbiddenError

            raise ForbiddenError("Forbidden")

    setattr(_authorize_secdep, "__tigrbl_dep_name__", "security.authorize")
    return _authorize_secdep


def _attach_to_router(router: RouterLike, table: type) -> None:
    """
    Attach the model’s bound namespaces to the router facade.
    """
    _ensure_router_ns(router)

    tname = table.__name__
    rname = getattr(table, "resource_name", None) or getattr(
        table, "__tablename__", tname.lower()
    )
    rtitle = rname[:1].upper() + rname[1:]
    logger.debug("Attaching table %s as resource '%s'", tname, rname)

    router.tables[tname] = table

    # Direct references to model namespaces
    setattr(router.schemas, tname, getattr(table, "schemas", SimpleNamespace()))
    setattr(router.handlers, tname, getattr(table, "handlers", SimpleNamespace()))
    setattr(router.hooks, tname, getattr(table, "hooks", SimpleNamespace()))
    rpc_ns = _build_router_rpc_namespace(router, table)
    setattr(router.rpc, tname, rpc_ns)
    if rtitle != tname:
        setattr(router.rpc, rtitle, rpc_ns)
        logger.debug("Registered RPC namespace alias '%s'", rtitle)
    # rest (router lives on table.rest.router)
    rest_ns = getattr(router, "rest")
    setattr(
        rest_ns,
        tname,
        SimpleNamespace(
            router=getattr(getattr(table, "rest", SimpleNamespace()), "router", None)
        ),
    )
    # also keep a flat routers dict for quick access
    router.routers[tname] = getattr(
        getattr(table, "rest", SimpleNamespace()), "router", None
    )

    # Table metadata (introspection only)
    declared_columns = _coerce_model_columns(getattr(table, "columns", ()))
    collected_columns = tuple(mro_collect_columns(table).keys())
    if declared_columns:
        ordered = []
        seen = set()
        for name in (*declared_columns, *collected_columns):
            if name in seen:
                continue
            seen.add(name)
            ordered.append(name)
        columns = tuple(ordered)
    else:
        columns = collected_columns
    router.columns[tname] = columns
    router.table_config[tname] = dict(getattr(table, "table_config", {}) or {})

    # Core helper proxies (now aware of API for DB resolution precedence)
    core_proxy = _ResourceProxy(table, router=router)
    setattr(router.core, tname, core_proxy)
    if rtitle != tname:
        setattr(router.core, rtitle, core_proxy)
    core_raw_proxy = _ResourceProxy(table, serialize=False, router=router)
    setattr(router.core_raw, tname, core_raw_proxy)
    if rtitle != tname:
        setattr(router.core_raw, rtitle, core_raw_proxy)


def include_model(
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
    logger.debug("Including model %s", model.__name__)

    # If another test or call disposed the SQLAlchemy registry, previously
    # imported models can retain ``__table__`` while losing mapper state.
    # Re-map on demand so later requests still operate on mapped ORM classes.
    needs_remap = not hasattr(model, "__table__")
    if not needs_remap:
        try:
            from sqlalchemy import inspect as _sa_inspect
            from sqlalchemy.exc import NoInspectionAvailable

            try:
                _sa_inspect(model)
            except NoInspectionAvailable:
                needs_remap = True
        except Exception:  # pragma: no cover - defensive import guard
            needs_remap = False

    if needs_remap:
        try:  # pragma: no cover - defensive path exercised in tests
            from ...table import Base
            from ...table._base import _materialize_colspecs_to_sqla

            # Recreate mapped_column attributes from ColumnSpecs then map.
            # Prefer the model's own registry so classes survive external
            # ``TableBase.registry.dispose()`` calls in other tests.
            _materialize_colspecs_to_sqla(model)
            registry = getattr(model, "registry", None) or getattr(
                Base, "registry", None
            )
            if registry is not None:
                registry.map_declaratively(model)
        except Exception:  # pragma: no cover
            logger.debug("Failed to remap model %s", model.__name__, exc_info=True)

    # 0) seed deps/security so binders can see them (transport-level only)
    _seed_security_and_deps(router, model)

    # 1) Build/bind model namespaces (idempotent)
    _binder.bind(model, router=router)

    auth_dep = getattr(model, TIGRBL_AUTH_DEP_ATTR, None)
    authorize_dep = _make_authorize_secdep(router)
    runtime_secdeps = tuple(d for d in (auth_dep, authorize_dep) if d is not None)
    allow_attr = getattr(model, TIGRBL_ALLOW_ANON_ATTR, None)
    allow_anon = set((allow_attr() if callable(allow_attr) else allow_attr) or ())
    _inject_runtime_secdeps(model, runtime_secdeps, allow_anon)

    # 2) Pick a router & mount prefix
    model_router = getattr(getattr(model, "rest", SimpleNamespace()), "router", None)
    if prefix is None:
        prefix = _default_prefix(model)
        logger.debug("Computed default prefix '%s' for %s", prefix, model.__name__)
    else:
        logger.debug("Using provided prefix '%s' for %s", prefix, model.__name__)

    # 3) Always bind model router to the Router object when possible
    root_router = (
        router if _has_include_router(router) else getattr(router, "router", None)
    )
    if model_router is not None:
        logger.debug("Mounting model router for %s on router", model.__name__)
        _mount_router(root_router, model_router, prefix=prefix)
    else:
        logger.debug("Model %s has no router to mount", model.__name__)

    # Optionally mount onto a host app
    target_app = app or getattr(router, "app", None)
    if mount_router and model_router is not None:
        logger.debug("Mounting router for %s on host app", model.__name__)
        _mount_router(target_app, model_router, prefix=prefix)
    else:
        logger.debug(
            "Skipping host app mount for %s (mount_router=%s, router=%s)",
            model.__name__,
            mount_router,
            model_router is not None,
        )

    # 4) Attach all namespaces onto router
    _attach_to_router(router, model)

    logger.debug("mapping.router: included %s at prefix %s", model.__name__, prefix)
    return model, model_router


def include_models(
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
    logger.debug("Including %d models", len(models))
    results: Dict[str, Any] = {}
    for mdl in models:
        px = base_prefix.rstrip("/") if base_prefix else None
        logger.debug("Including model %s with base prefix %s", mdl.__name__, px)
        _, model_router = include_model(
            router, mdl, app=app, prefix=px, mount_router=mount_router
        )
        results[mdl.__name__] = model_router
    logger.debug("Finished including models")
    return results


def include_table(
    router: RouterLike,
    model: type,
    *,
    app: Any | None = None,
    prefix: str | None = None,
    mount_router: bool = True,
) -> Tuple[type, Any]:
    return include_model(
        router, model, app=app, prefix=prefix, mount_router=mount_router
    )


def include_tables(
    router: RouterLike,
    models: Sequence[type],
    *,
    app: Any | None = None,
    base_prefix: str | None = None,
    mount_router: bool = True,
) -> Dict[str, Any]:
    return include_models(
        router, models, app=app, base_prefix=base_prefix, mount_router=mount_router
    )
