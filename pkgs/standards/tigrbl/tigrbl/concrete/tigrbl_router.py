# tigrbl/v3/router/tigrbl_api.py
from __future__ import annotations

import copy
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

from ..router._router import Router as _Router
from ..engine.engine_spec import EngineCfg
from ..ddl import initialize as _ddl_initialize
from ..mapping.router import (
    include_table as _include_table,
    include_tables as _include_tables,
    rpc_call as _rpc_call,
    _seed_security_and_deps,
    _mount_router,
    _default_prefix,
)
from ..mapping.model import rebind as _rebind, bind as _bind
from ..mapping.rest import build_router_and_attach as _build_router_and_attach
from ..op import get_registry, OpSpec
from ..app._model_registry import initialize_table_registry
from ..system.favicon import mount_favicon
from ..router._routing import include_router as _include_router_impl
from ..transport import mount_jsonrpc as _mount_jsonrpc


class TigrblRouter(_Router):
    """
    Canonical router-focused facade that owns:
      • containers (models, schemas, handlers, hooks, rpc, rest, routers, columns, table_config, core proxies)
      • model inclusion (REST + RPC wiring)
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

    mount_favicon = mount_favicon

    def __init__(
        self,
        *,
        engine: EngineCfg | None = None,
        models: Sequence[type] | None = None,
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
        get_db = router_kwargs.pop("get_db", None)
        _Router.__init__(self, engine=engine, **router_kwargs)
        if get_db is not None:
            self.get_db = get_db
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
        self.rest_prefix = getattr(self, "REST_PREFIX", "/router")

        # public containers (mirrors used by bindings.router)
        self.models = initialize_table_registry(getattr(self, "TABLES", ()))
        self.tables = initialize_table_registry(getattr(self, "TABLES", ()))
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
        if models:
            self.include_tables(list(models))

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
        if mount_router and prefix is None and router is not None:
            _include_router_impl(self, router, prefix=self.rest_prefix)
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
        if mount_router and base_prefix is None:
            for router in included.values():
                if router is not None:
                    _include_router_impl(self, router, prefix=self.rest_prefix)
        return included

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
        """Build and mount a JSON-RPC router on this router instance."""
        px = prefix if prefix is not None else self.jsonrpc_prefix
        self.jsonrpc_prefix = px
        return _mount_jsonrpc(self, self, prefix=px, tags=tags)

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
        for m in self.models.values():
            t = getattr(m, "__table__", None)
            if t is not None and not t.columns:
                continue
            if t is not None and t not in seen:
                seen.add(t)
                tables.append(t)
        return tables

    initialize = _ddl_initialize

    # ------------------------- repr -------------------------

    def __repr__(self) -> str:  # pragma: no cover
        models = list(getattr(self, "models", {}))
        rpc_ns = getattr(self, "rpc", None)
        rpc_keys = list(getattr(rpc_ns, "__dict__", {}).keys()) if rpc_ns else []
        return f"<TigrblRouter models={models} rpc={rpc_keys}>"
