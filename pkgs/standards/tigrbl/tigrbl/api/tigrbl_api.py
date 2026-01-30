# tigrbl/v3/api/tigrbl_api.py
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

from ._api import Api as _Api
from ..engine.engine_spec import EngineCfg
from ..engine import resolver as _resolver
from ..ddl import initialize as _ddl_initialize
from ..bindings.api import (
    include_model as _include_model,
    include_models as _include_models,
    rpc_call as _rpc_call,
    _seed_security_and_deps,
    _mount_router,
    _default_prefix,
    AttrDict,
)
from ..bindings.model import rebind as _rebind, bind as _bind
from ..bindings.rest import build_router_and_attach as _build_router_and_attach
from ..transport import mount_jsonrpc as _mount_jsonrpc
from ..system import mount_diagnostics as _mount_diagnostics
from ..op import get_registry, OpSpec
from ..app._model_registry import initialize_model_registry


class TigrblApi(_Api):
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
        engine: EngineCfg | None = None,
        models: Sequence[type] | None = None,
        prefix: str | None = None,
        jsonrpc_prefix: str = "/rpc",
        system_prefix: str = "/system",
        api_hooks: Mapping[str, Iterable[Callable]]
        | Mapping[str, Mapping[str, Iterable[Callable]]]
        | None = None,
        **router_kwargs: Any,
    ) -> None:
        if prefix is not None:
            self.PREFIX = prefix
        _Api.__init__(self, engine=engine, **router_kwargs)
        self.jsonrpc_prefix = jsonrpc_prefix
        self.system_prefix = system_prefix

        # public containers (mirrors used by bindings.api)
        self.models = initialize_model_registry(getattr(self, "MODELS", ()))
        self.schemas = SimpleNamespace()
        self.handlers = SimpleNamespace()
        self.hooks = SimpleNamespace()
        self.rpc = SimpleNamespace()
        self.rest = SimpleNamespace()
        self.routers: Dict[str, Any] = {}
        self.tables = AttrDict()
        self.columns: Dict[str, Tuple[str, ...]] = {}
        self.table_config: Dict[str, Dict[str, Any]] = {}
        self.core = SimpleNamespace()
        self.core_raw = SimpleNamespace()

        # API-level hooks map (merged into each model at include-time; precedence handled in bindings.hooks)
        self._api_hooks_map = copy.deepcopy(api_hooks) if api_hooks else None
        if models:
            self.include_models(list(models))

    # ------------------------- internal helpers -------------------------

    @staticmethod
    def _merge_api_hooks_into_model(model: type, hooks_map: Any) -> None:
        """
        Install API-level hooks on the model so the binder can see them.
        Accepted shapes:
            {phase: [fn, ...]}                           # global, all aliases
            {alias: {phase: [fn, ...]}, "*": {...}}      # per-alias + wildcard
        If the model already has __tigrbl_api_hooks__, we shallow-merge keys.
        """
        if not hooks_map:
            return
        existing = getattr(model, "__tigrbl_api_hooks__", None)
        if existing is None:
            setattr(model, "__tigrbl_api_hooks__", copy.deepcopy(hooks_map))
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
        setattr(model, "__tigrbl_api_hooks__", merged)

    # ------------------------- primary operations -------------------------

    def include_model(
        self, model: type, *, prefix: str | None = None, mount_router: bool = True
    ) -> Tuple[type, Any]:
        """
        Bind a model, mount its REST router, and attach all namespaces to this facade.
        """
        # inject API-level hooks so the binder merges them
        self._merge_api_hooks_into_model(model, self._api_hooks_map)
        return _include_model(
            self, model, app=None, prefix=prefix, mount_router=mount_router
        )

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
            app=None,
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
        """Mount a JSON-RPC router onto this TigrblApi instance."""
        px = prefix if prefix is not None else self.jsonrpc_prefix
        prov = _resolver.resolve_provider(api=self)
        get_db = prov.get_db if prov else None
        router = _mount_jsonrpc(
            self,
            self,
            prefix=px,
            get_db=get_db,
        )
        return router

    def attach_diagnostics(
        self, *, prefix: str | None = None, app: Any | None = None
    ) -> Any:
        """Mount a diagnostics router onto this TigrblApi instance or ``app``."""
        px = prefix if prefix is not None else self.system_prefix
        prov = _resolver.resolve_provider(api=self)
        get_db = prov.get_db if prov else None
        router = _mount_diagnostics(self, get_db=get_db)
        include_self = getattr(self, "include_router", None)
        if callable(include_self):
            include_self(router, prefix=px)
        if app is not None and app is not self:
            include_other = getattr(app, "include_router", None)
            if callable(include_other):
                include_other(router, prefix=px)
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
        return f"<TigrblApi models={models} rpc={rpc_keys}>"
