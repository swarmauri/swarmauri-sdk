# autoapi/v3/autoapp.py
from __future__ import annotations

import copy
import asyncio
import inspect
from types import SimpleNamespace
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    Mapping,
    Optional,
    Sequence,
    Tuple,
)

from .app._app import App as _App
from .engine.engine_spec import EngineCfg
from .engine import resolver as _resolver
from .system.dbschema import (
    ensure_schemas,
    bootstrap_dbschema,
    sqlite_default_attach_map,
)
from .bindings.api import (
    include_model as _include_model,
    include_models as _include_models,
    rpc_call as _rpc_call,
    _seed_security_and_deps,
    _mount_router,
    _default_prefix,
)
from .bindings.model import rebind as _rebind, bind as _bind
from .bindings.rest import build_router_and_attach as _build_router_and_attach
from .transport import mount_jsonrpc as _mount_jsonrpc
from .system import mount_diagnostics as _mount_diagnostics
from .ops import get_registry, OpSpec


# optional compat: legacy transactional decorator
try:
    from .compat.transactional import transactional as _txn_decorator
except Exception:  # pragma: no cover
    _txn_decorator = None


class AutoApp(_App):
    """
    Monolithic facade that owns:
      • containers (models, schemas, handlers, hooks, rpc, rest, routers, columns, table_config, core proxies)
      • model inclusion (REST + RPC wiring)
      • JSON-RPC / diagnostics mounting
      • (optional) legacy-friendly helpers (transactional decorator, auth flags)

    It composes v3 primitives; you can still use the functions directly if you prefer.
    """

    TITLE = "AutoApp"
    VERSION = "0.1.0"
    LIFESPAN = None
    MIDDLEWARES: Sequence[Any] = ()
    APIS: Sequence[Any] = ()
    MODELS: Sequence[Any] = ()

    # --- optional auth knobs recognized by some middlewares/dispatchers (kept for back-compat) ---
    _authn: Any = None
    _allow_anon: bool = True
    _authorize: Any = None
    _optional_authn_dep: Any = None
    _allow_anon_ops: set[str] = set()

    def __init__(
        self,
        *,
        engine: EngineCfg | None = None,
        jsonrpc_prefix: str = "/rpc",
        system_prefix: str = "/system",
        api_hooks: Mapping[str, Iterable[Callable]]
        | Mapping[str, Mapping[str, Iterable[Callable]]]
        | None = None,
        **fastapi_kwargs: Any,
    ) -> None:
        title = fastapi_kwargs.pop("title", None)
        if title is not None:
            self.TITLE = title
        version = fastapi_kwargs.pop("version", None)
        if version is not None:
            self.VERSION = version
        lifespan = fastapi_kwargs.pop("lifespan", None)
        if lifespan is not None:
            self.LIFESPAN = lifespan
        super().__init__(engine=engine, **fastapi_kwargs)
        # capture initial routes so refreshes retain FastAPI defaults
        self._base_routes = list(self.router.routes)
        self.jsonrpc_prefix = jsonrpc_prefix
        self.system_prefix = system_prefix

        # public containers (mirrors used by bindings.api)
        self.models: Dict[str, type] = {}
        self.schemas = SimpleNamespace()
        self.handlers = SimpleNamespace()
        self.hooks = SimpleNamespace()
        self.rpc = SimpleNamespace()
        self.rest = SimpleNamespace()
        self.routers: Dict[str, Any] = {}
        self.columns: Dict[str, Tuple[str, ...]] = {}
        self.table_config: Dict[str, Dict[str, Any]] = {}
        self.core = SimpleNamespace()
        self.core_raw = SimpleNamespace()

        # API-level hooks map (merged into each model at include-time; precedence handled in bindings.hooks)
        self._api_hooks_map = copy.deepcopy(api_hooks) if api_hooks else None

    # ------------------------- internal helpers -------------------------

    @staticmethod
    def _merge_api_hooks_into_model(model: type, hooks_map: Any) -> None:
        """
        Install API-level hooks on the model so the binder can see them.
        Accepted shapes:
            {phase: [fn, ...]}                           # global, all aliases
            {alias: {phase: [fn, ...]}, "*": {...}}      # per-alias + wildcard
        If the model already has __autoapi_api_hooks__, we shallow-merge keys.
        """
        if not hooks_map:
            return
        existing = getattr(model, "__autoapi_api_hooks__", None)
        if existing is None:
            setattr(model, "__autoapi_api_hooks__", copy.deepcopy(hooks_map))
            return

        # shallow merge (alias or phase keys); values are lists we extend
        merged = copy.deepcopy(existing)
        for k, v in (hooks_map or {}).items():
            if k not in merged:
                merged[k] = copy.deepcopy(v)
            else:
                # when both are dicts, merge phase lists
                if isinstance(v, Mapping) and isinstance(merged[k], Mapping):
                    for ph, fns in v.items():
                        merged[k].setdefault(ph, [])
                        merged[k][ph] = list(merged[k][ph]) + list(fns or [])
                else:
                    # fallback: prefer model-local value, then append api-level
                    if isinstance(merged[k], list):
                        merged[k] = list(merged[k]) + list(v or [])
                    else:
                        merged[k] = v
        setattr(model, "__autoapi_api_hooks__", merged)

    # ------------------------- primary operations -------------------------

    def include_model(
        self, model: type, *, prefix: str | None = None, mount_router: bool = True
    ) -> Tuple[type, Any]:
        """
        Bind a model, mount its REST router, and attach all namespaces to this facade.
        """
        # inject API-level hooks so the binder merges them
        self._merge_api_hooks_into_model(model, self._api_hooks_map)
        return _include_model(self, model, prefix=prefix, mount_router=mount_router)

    def include_models(
        self,
        models: Sequence[type],
        *,
        base_prefix: str | None = None,
        mount_router: bool = True,
    ) -> Dict[str, Any]:
        for m in models:
            self._merge_api_hooks_into_model(m, self._api_hooks_map)
        return _include_models(
            self,
            models,
            base_prefix=base_prefix,
            mount_router=mount_router,
        )

    async def rpc_call(
        self,
        model_or_name: type | str,
        method: str,
        payload: Any = None,
        *,
        db: Any,
        request: Any = None,
        ctx: Optional[Dict[str, Any]] = None,
    ) -> Any:
        return await _rpc_call(
            self, model_or_name, method, payload, db=db, request=request, ctx=ctx
        )

    # ------------------------- extras / mounting -------------------------

    def mount_jsonrpc(self, *, prefix: str | None = None) -> Any:
        """Mount JSON-RPC router onto this app."""
        px = prefix if prefix is not None else self.jsonrpc_prefix
        router = _mount_jsonrpc(
            self,
            self,
            prefix=px,
        )
        self._base_routes = list(self.router.routes)
        return router

    def attach_diagnostics(self, *, prefix: str | None = None) -> Any:
        """Mount diagnostics router onto this app."""
        px = prefix if prefix is not None else self.system_prefix
        router = _mount_diagnostics(self)
        if hasattr(self, "include_router"):
            self.include_router(router, prefix=px)
        self._base_routes = list(self.router.routes)
        return router

    # ------------------------- registry passthroughs -------------------------

    def registry(self, model: type):
        """Return the per-model OpspecRegistry."""
        return get_registry(model)

    def bind(self, model: type) -> Tuple[OpSpec, ...]:
        """Bind/rebuild a model in place (without mounting)."""
        self._merge_api_hooks_into_model(model, self._api_hooks_map)
        return _bind(model)

    def rebind(
        self, model: type, *, changed_keys: Optional[set[tuple[str, str]]] = None
    ) -> Tuple[OpSpec, ...]:
        """Targeted rebuild of a bound model."""
        return _rebind(model, changed_keys=changed_keys)

    # ------------------------- legacy helpers -------------------------

    def transactional(self, *dargs, **dkw):
        """
        Legacy-friendly decorator: @api.transactional(...)
        Wraps a function as a v3 custom op with START_TX/END_TX.
        """
        if _txn_decorator is None:
            raise RuntimeError("transactional decorator not available")
        return _txn_decorator(self, *dargs, **dkw)

    # Optional: let callers set auth knobs used by some middlewares/dispatchers
    def set_auth(
        self,
        *,
        authn: Any = None,
        allow_anon: Optional[bool] = None,
        authorize: Any = None,
        optional_authn_dep: Any = None,
    ) -> None:
        if authn is not None:
            self._authn = authn
        if allow_anon is not None:
            self._allow_anon = bool(allow_anon)
        if authorize is not None:
            self._authorize = authorize
        if optional_authn_dep is not None:
            self._optional_authn_dep = optional_authn_dep

        # Refresh already-included models so routers pick up new auth settings
        if self.models:
            self._refresh_security()

    def _refresh_security(self) -> None:
        """Re-seed auth deps on models and rebuild routers."""
        # Reset router to baseline and allow_anon ops cache
        self.router.routes = list(self._base_routes)
        self._allow_anon_ops = set()
        for model in self.models.values():
            _seed_security_and_deps(self, model)
            specs = getattr(getattr(model, "opspecs", SimpleNamespace()), "all", ())
            if specs:
                _build_router_and_attach(model, list(specs))
            router = getattr(getattr(model, "rest", SimpleNamespace()), "router", None)
            if router is None:
                continue
            # update api-level references
            mname = model.__name__
            rest_ns = getattr(self.rest, mname, SimpleNamespace())
            rest_ns.router = router
            setattr(self.rest, mname, rest_ns)
            self.routers[mname] = router
            prefix = _default_prefix(model)
            _mount_router(self, router, prefix=prefix)

    def _collect_tables(self):
        # dedupe; handle multiple DeclarativeBases (multiple metadatas)
        seen = set()
        tables = []
        for m in self.models.values():
            t = getattr(m, "__table__", None)
            if t is not None and t not in seen:
                seen.add(t)
                tables.append(t)
        return tables

    def _create_all_on_bind(
        self, bind, *, schemas=None, sqlite_attachments=None, tables=None
    ):
        # 1) collect tables + schemas / SQLite ATTACH
        engine = getattr(bind, "engine", bind)
        tables = tables or self._collect_tables()

        schema_names = set(schemas or [])
        for t in tables:
            if getattr(t, "schema", None):
                schema_names.add(t.schema)

        attachments = sqlite_attachments
        if attachments is None and getattr(engine.dialect, "name", "") == "sqlite":
            if schema_names:
                attachments = sqlite_default_attach_map(engine, schema_names)

        if attachments:
            # accept PathLike values for attachment targets
            attachments = {k: str(v) for k, v in attachments.items()}
            # also applies ensure_schemas; immediate listener warm-up
            bootstrap_dbschema(
                engine,
                schemas=schema_names,
                sqlite_attachments=attachments,
                immediate=True,
            )
        else:
            ensure_schemas(engine, schema_names)

        # 2) create tables (group by metadata to support multiple bases)
        by_meta = {}
        for t in tables:
            by_meta.setdefault(t.metadata, []).append(t)
        for md, group in by_meta.items():
            md.create_all(bind=bind, checkfirst=True, tables=group)

        # 3) publish tables namespace
        self.tables = SimpleNamespace(
            **{
                name: getattr(m, "__table__", None)
                for name, m in self.models.items()
                if hasattr(m, "__table__")
            }
        )

    def initialize_sync(self, *, schemas=None, sqlite_attachments=None, tables=None):
        if getattr(self, "_ddl_executed", False):
            return
        prov = _resolver.resolve_provider()
        if prov is None:
            raise ValueError("Engine provider is not configured")
        with next(prov.get_db()) as db:
            bind = db.get_bind()  # Connection or Engine
            self._create_all_on_bind(
                bind,
                schemas=schemas,
                sqlite_attachments=sqlite_attachments,
                tables=tables,
            )
        self._ddl_executed = True

    async def initialize_async(
        self, *, schemas=None, sqlite_attachments=None, tables=None
    ):
        if getattr(self, "_ddl_executed", False):
            return
        prov = _resolver.resolve_provider()
        if prov is None:
            raise ValueError("Engine provider is not configured")

        if inspect.isasyncgenfunction(prov.get_db):
            async for adb in prov.get_db():  # AsyncSession

                def _sync_bootstrap(arg):
                    bind = arg.get_bind() if hasattr(arg, "get_bind") else arg
                    self._create_all_on_bind(
                        bind,
                        schemas=schemas,
                        sqlite_attachments=sqlite_attachments,
                        tables=tables,
                    )

                await adb.run_sync(_sync_bootstrap)
                break
        else:
            gen = prov.get_db()
            db = next(gen)

            try:
                if hasattr(db, "run_sync"):

                    def _sync_bootstrap(arg):
                        bind = arg.get_bind() if hasattr(arg, "get_bind") else arg
                        self._create_all_on_bind(
                            bind,
                            schemas=schemas,
                            sqlite_attachments=sqlite_attachments,
                            tables=tables,
                        )

                    await db.run_sync(_sync_bootstrap)
                else:
                    bind = db.get_bind()
                    await asyncio.to_thread(
                        self._create_all_on_bind,
                        bind,
                        schemas=schemas,
                        sqlite_attachments=sqlite_attachments,
                        tables=tables,
                    )
            finally:
                try:
                    next(gen)
                except StopIteration:
                    pass
        self._ddl_executed = True

    # ------------------------- repr -------------------------

    def __repr__(self) -> str:  # pragma: no cover
        return f"<AutoApp models={list(self.models)} rpc={list(getattr(self.rpc, '__dict__', {}).keys())}>"
