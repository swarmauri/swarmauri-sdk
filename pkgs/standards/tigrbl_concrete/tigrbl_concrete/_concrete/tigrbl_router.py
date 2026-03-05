# tigrbl/_concrete/tigrbl_router.py
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

from ._router import Router as _Router
from tigrbl_core._spec.engine_spec import EngineCfg
from ..ddl import initialize as _ddl_initialize
from tigrbl_canon.mapping.router.common import _default_prefix, _mount_router
from tigrbl_canon.mapping.router.include import (
    _seed_security_and_deps,
    include_table as _include_table,
    include_tables as _include_tables,
)
from tigrbl_canon.mapping.router.rpc import rpc_call as _rpc_call
from tigrbl_canon.mapping.model import rebind as _rebind, bind as _bind
from tigrbl_canon.mapping.rest import (
    build_router_and_attach as _build_router_and_attach,
)
from ..op import get_registry
from tigrbl_core._spec import OpSpec
from ._table_registry import TableRegistry
from ._routing import include_router as _include_router_impl
from ..system import mount_openrpc as _mount_openrpc
from ..system import mount_diagnostics as _mount_diagnostics
from ..system.docs import build_openapi as _build_openapi
from tigrbl_canon.mapping import engine_resolver as _resolver
from ._engine import Engine


class TigrblRouter(_Router):
    """
    Canonical router-focused facade that owns:
      • containers (tables, schemas, handlers, hooks, rpc, rest, routers, columns, table_config, core proxies)
      • table inclusion (REST + RPC wiring)
      • (optional) auth knobs recognized by some middlewares/dispatchers

    It composes v3 primitives; you can still use the functions directly if you prefer.
    """

    PREFIX = ""
    REST_PREFIX = "/api"
    RPC_PREFIX = "/rpc"
    SYSTEM_PREFIX = "/system"
    TAGS: Sequence[Any] = ()
    ROUTERS: Sequence[Any] = ()
    TABLES: Sequence[Any] = ()

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
        tables: Sequence[type] | None = None,
        prefix: str | None = None,
        jsonrpc_prefix: str | None = None,
        system_prefix: str | None = None,
        router_hooks: Mapping[str, Iterable[Callable]]
        | Mapping[str, Mapping[str, Iterable[Callable]]]
        | None = None,
        **router_kwargs: Any,
    ) -> None:
        if prefix is not None:
            self.PREFIX = prefix
        _Router.__init__(self, engine=engine, **router_kwargs)
        self._authn = None
        self._allow_anon = True
        self._authorize = None
        self._optional_authn_dep = None
        self._allow_anon_ops: set[str] = set()
        self.jsonrpc_prefix = (
            jsonrpc_prefix
            if jsonrpc_prefix is not None
            else getattr(self, "RPC_PREFIX", getattr(self, "JSONRPC_PREFIX", "/rpc"))
        )
        self.system_prefix = (
            system_prefix
            if system_prefix is not None
            else getattr(self, "SYSTEM_PREFIX", "/system")
        )
        # ``prefix=...`` is the canonical REST mount prefix for router-scoped
        # table routes. Fall back to REST_PREFIX only when no explicit prefix
        # is provided.
        self.rest_prefix = (
            prefix if prefix is not None else getattr(self, "REST_PREFIX", "/api")
        )

        # public containers (mirrors used by bindings.router)
        self.tables = TableRegistry(tables=getattr(self, "TABLES", ()))
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

        # Router-level hooks map (merged into each model at include-time; precedence handled in bindings.hooks)
        self._router_hooks_map = copy.deepcopy(router_hooks) if router_hooks else None
        if tables:
            self.include_tables(list(tables))

    # ------------------------- internal helpers -------------------------

    @staticmethod
    def _merge_router_hooks_into_model(model: type, hooks_map: Any) -> None:
        """
        Install Router-level hooks on the model so the binder can see them.
        Accepted shapes:
            {phase: [fn, ...]}                           # global, all aliases
            {alias: {phase: [fn, ...]}, "*": {...}}      # per-alias + wildcard
        If the model already has __tigrbl_router_hooks__, we shallow-merge keys.
        """
        if not hooks_map:
            return
        existing = getattr(model, "__tigrbl_router_hooks__", None)
        if existing is None:
            setattr(model, "__tigrbl_router_hooks__", copy.deepcopy(hooks_map))
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
                    # fallback: prefer model-local value, then append router-level
                    if isinstance(merged[k], list):
                        merged[k] = list(merged[k]) + list(v or [])
                    else:
                        merged[k] = v
        setattr(model, "__tigrbl_router_hooks__", merged)

    # ------------------------- primary operations -------------------------

    def include_table(
        self, model: type, *, prefix: str | None = None, mount_router: bool = True
    ) -> Tuple[type, Any]:
        """
        Bind a model, mount its REST router, and attach all namespaces to this facade.
        """
        # inject Router-level hooks so the binder merges them
        self._merge_router_hooks_into_model(model, self._router_hooks_map)
        included_table, router = _include_table(
            self, model, app=None, prefix=prefix, mount_router=mount_router
        )
        if mount_router and router is not None:
            _include_router_impl(self, router, prefix=prefix)
        return included_table, router

    def include_tables(
        self,
        tables: Sequence[type],
        *,
        base_prefix: str | None = None,
        mount_router: bool = True,
    ) -> Dict[str, Any]:
        for m in tables:
            self._merge_router_hooks_into_model(m, self._router_hooks_map)
        included = _include_tables(
            self,
            tables,
            app=None,
            base_prefix=base_prefix,
            mount_router=mount_router,
        )
        if mount_router:
            for router in included.values():
                if router is not None:
                    _include_router_impl(self, router, prefix=base_prefix)
        return included

    def install_engines(
        self, *, router: Any | None = None, tables: tuple[Any, ...] | None = None
    ) -> None:
        """Install engine providers for this router and optional table set."""
        selected_router = self if router is None else router
        selected_tables = tables if tables is not None else tuple(self.tables.values())
        Engine.install_from_objects(
            router=selected_router, tables=tuple(selected_tables)
        )

    def initialize(
        self,
        *,
        schemas: Iterable[str] | None = None,
        sqlite_attachments: Mapping[str, str] | None = None,
        tables: Iterable[Any] | None = None,
    ):
        """Initialize DDL for this router."""
        try:
            result = _ddl_initialize(
                self,
                schemas=schemas,
                sqlite_attachments=sqlite_attachments,
                tables=tables,
            )
        except ValueError as exc:
            if str(exc) != "Engine provider is not configured":
                raise
            result = None

        if inspect.isawaitable(result):

            async def _inner() -> None:
                await result

            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                asyncio.run(_inner())
                return None
            return loop.create_task(_inner())

        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return None

        async def _noop() -> None:
            return None

        return _noop()

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

    def mount_jsonrpc(
        self, *, prefix: str | None = None, tags: Sequence[str] | None = ("rpc",)
    ) -> Any:
        del tags
        if prefix is not None:
            self.jsonrpc_prefix = prefix

        existing_paths = {getattr(route, "path", None) for route in self.routes}
        if (
            self.jsonrpc_prefix not in existing_paths
            and f"{self.jsonrpc_prefix}/" not in existing_paths
        ):
            self.add_route(
                self.jsonrpc_prefix,
                lambda *_args, **_kwargs: None,
                methods=["POST"],
            )
        return self

    def mount_openrpc(
        self,
        *,
        path: str = "/openrpc.json",
        name: str = "openrpc_json",
        tags: Sequence[str] | None = None,
    ) -> Any:
        """Mount an OpenRPC JSON endpoint onto this router instance."""
        return _mount_openrpc(self, path=path, name=name, tags=tags)

    def attach_diagnostics(
        self, *, prefix: str | None = None, app: Any | None = None
    ) -> Any:
        """Mount diagnostics router onto this router or the provided ``app``."""
        px = prefix if prefix is not None else self.system_prefix
        prov = _resolver.resolve_provider(router=self)
        get_db = prov.get_db if prov else None
        router = _mount_diagnostics(self, get_db=get_db)
        _include_router_impl(self, router, prefix=px)
        if app is not None and app is not self:
            include_other = getattr(app, "include_router", None)
            if callable(include_other):
                include_other(router, prefix=px)
        return router

    def openapi(self) -> Dict[str, Any]:
        """Build and return the OpenAPI document for this router."""
        return _build_openapi(self)

    # ------------------------- registry passthroughs -------------------------

    def registry(self, model: type):
        """Return the per-model OpspecRegistry."""
        return get_registry(model)

    def bind(self, model: type) -> Tuple[OpSpec, ...]:
        """Bind/rebuild a model in place (without mounting)."""
        self._merge_router_hooks_into_model(model, self._router_hooks_map)
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
            if allow_anon is None:
                allow_anon = False
        if allow_anon is not None:
            self._allow_anon = bool(allow_anon)
        if authorize is not None:
            self._authorize = authorize
        if optional_authn_dep is not None:
            self._optional_authn_dep = optional_authn_dep

        # Refresh already-included models so routers pick up new auth settings
        if self.tables:
            self._refresh_security()

    def _resolve_registered_model(self, name: str, value: Any) -> Any:
        if isinstance(value, type):
            return value
        core_proxy = getattr(self.core, name, None)
        model = getattr(core_proxy, "_model", None)
        return model if isinstance(model, type) else None

    def _refresh_security(self) -> None:
        """Re-seed auth deps on models and rebuild routers."""
        # Reset routes and allow_anon ops cache
        self.routes = []
        self._allow_anon_ops = set()
        for name, registered in self.tables.items():
            model = self._resolve_registered_model(name, registered)
            if not isinstance(model, type):
                continue
            _seed_security_and_deps(self, model)
            specs = getattr(getattr(model, "opspecs", SimpleNamespace()), "all", ())
            if specs:
                _build_router_and_attach(model, list(specs))
            router = getattr(getattr(model, "rest", SimpleNamespace()), "router", None)
            if router is None:
                continue
            # update router-level references
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
        for name, registered in self.tables.items():
            table = (
                registered
                if not isinstance(registered, type)
                and hasattr(registered, "metadata")
                and hasattr(registered, "columns")
                else None
            )
            if table is None:
                model = self._resolve_registered_model(name, registered)
                table = (
                    getattr(model, "__table__", None)
                    if isinstance(model, type)
                    else None
                )
            if table is not None and not table.columns:
                continue
            if table is not None and table not in seen:
                seen.add(table)
                tables.append(table)
        return tables

    # ------------------------- repr -------------------------

    def __repr__(self) -> str:  # pragma: no cover
        tables = list(getattr(self, "tables", {}))
        rpc_ns = getattr(self, "rpc", None)
        rpc_keys = list(getattr(rpc_ns, "__dict__", {}).keys()) if rpc_ns else []
        return f"<TigrblRouter tables={tables} rpc={rpc_keys}>"
