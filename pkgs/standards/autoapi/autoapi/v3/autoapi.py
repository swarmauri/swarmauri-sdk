# autoapi/v3/autoapi.py
from __future__ import annotations

import copy
from types import SimpleNamespace
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Iterable,
    Mapping,
    Optional,
    Sequence,
    Tuple,
)

from .api._api import Api as _Api
from .engine.engine_spec import EngineCfg
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


class AutoAPI(_Api):
    """
    Canonical router-focused facade that owns:
      • containers (models, schemas, handlers, hooks, rpc, rest, routers, columns, table_config, core proxies)
      • model inclusion (REST + RPC wiring)
      • JSON-RPC / diagnostics mounting
      • (optional) auth knobs recognized by some middlewares/dispatchers

    It composes v3 primitives; you can still use the functions directly if you prefer.
    """

    PREFIX = ""
    TAGS: Sequence[Any] = ()
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
        db: EngineCfg | None = None,
        get_db: Optional[Callable[..., Any]] = None,
        get_async_db: Optional[Callable[..., Awaitable[Any]]] = None,
        jsonrpc_prefix: str = "/rpc",
        system_prefix: str = "/system",
        api_hooks: Mapping[str, Iterable[Callable]]
        | Mapping[str, Mapping[str, Iterable[Callable]]]
        | None = None,
        **router_kwargs: Any,
    ) -> None:
        _Api.__init__(self, db=db, **router_kwargs)
        # DB dependencies for transports/diagnostics
        if get_db is not None:
            self.get_db = get_db
        elif db is None:
            self.get_db = None
        if get_async_db is not None:
            self.get_async_db = get_async_db
        elif db is None:
            self.get_async_db = None
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
        self.tables: Dict[str, Any] = {}
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
        """Mount JSON-RPC router onto this facade."""
        px = prefix if prefix is not None else self.jsonrpc_prefix
        router = _mount_jsonrpc(
            self,
            self,
            prefix=px,
            get_db=self.get_db,
            get_async_db=self.get_async_db,
        )
        return router

    def attach_diagnostics(self, *, prefix: str | None = None) -> Any:
        """Mount diagnostics router onto this facade."""
        px = prefix if prefix is not None else self.system_prefix
        router = _mount_diagnostics(
            self, get_db=self.get_db, get_async_db=self.get_async_db
        )
        if hasattr(self, "include_router"):
            self.include_router(router, prefix=px)
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
        # Reset routes and allow_anon ops cache
        self.routes = []
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
        self.tables.update(
            {
                name: getattr(m, "__table__", None)
                for name, m in self.models.items()
                if hasattr(m, "__table__")
            }
        )

    def initialize_sync(self, *, schemas=None, sqlite_attachments=None, tables=None):
        if getattr(self, "_ddl_executed", False):
            return
        if not self.get_db:
            raise ValueError("AutoAPI.get_db is not configured")
        with next(self.get_db()) as db:
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
        if not self.get_async_db:
            raise ValueError("AutoAPI.get_async_db is not configured")
        async for adb in self.get_async_db():  # AsyncSession

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
        self._ddl_executed = True

    # ------------------------- repr -------------------------

    def __repr__(self) -> str:  # pragma: no cover
        return f"<AutoAPI models={list(self.models)} rpc={list(getattr(self.rpc, '__dict__', {}).keys())}>"
