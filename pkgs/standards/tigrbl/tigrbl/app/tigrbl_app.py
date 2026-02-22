# tigrbl/v3/app/tigrbl_app.py
from __future__ import annotations

import asyncio
import copy
import inspect
from pathlib import Path
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

from ._app import App as _App
from ..router.tigrbl_router import TigrblRouter
from ..engine.engine_spec import EngineCfg
from ..engine import resolver as _resolver
from ..ddl import initialize as _ddl_initialize
from ..bindings.router import (
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
from ..system import mount_lens as _mount_lens
from ..system import mount_openapi as _mount_openapi
from ..system import mount_openrpc as _mount_openrpc
from ..system import build_openrpc_spec as _build_openrpc_spec
from ..op import get_registry, OpSpec
from ._model_registry import initialize_model_registry
from ..system.favicon import FAVICON_PATH, mount_favicon


# optional compat: legacy transactional decorator
try:
    from .compat.transactional import transactional as _txn_decorator
except Exception:  # pragma: no cover
    _txn_decorator = None


class TigrblApp(_App):
    """
    Monolithic facade that owns:
      • containers (models, schemas, handlers, hooks, rpc, rest, routers, columns, table_config, core proxies)
      • model inclusion (REST + RPC wiring)
      • JSON-RPC / diagnostics mounting
      • (optional) legacy-friendly helpers (transactional decorator, auth flags)

    It composes v3 primitives; you can still use the functions directly if you prefer.
    """

    TITLE = "TigrblApp"
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
    _event_handlers: Dict[str, list[Callable[..., Any]]]

    mount_favicon = mount_favicon

    def __init__(
        self,
        *,
        engine: EngineCfg | None = None,
        apis: Sequence[Any] | None = None,
        jsonrpc_prefix: str | None = None,
        system_prefix: str | None = None,
        favicon_path: str | Path = FAVICON_PATH,
        router_hooks: Mapping[str, Iterable[Callable]]
        | Mapping[str, Mapping[str, Iterable[Callable]]]
        | None = None,
        **asgi_kwargs: Any,
    ) -> None:
        title = asgi_kwargs.pop("title", None)
        if title is not None:
            self.TITLE = title
        version = asgi_kwargs.pop("version", None)
        if version is not None:
            self.VERSION = version
        lifespan = asgi_kwargs.pop("lifespan", None)
        if lifespan is not None:
            self.LIFESPAN = lifespan
        super().__init__(engine=engine, **asgi_kwargs)
        self.router = self
        self._middlewares: list[tuple[Any, dict[str, Any]]] = []
        self.middlewares = tuple(getattr(self, "MIDDLEWARES", ()))
        self._favicon_path = favicon_path
        for mw in self.middlewares:
            mw_cls = getattr(mw, "cls", mw.__class__)
            self.add_middleware(mw_cls, **getattr(mw, "kwargs", {}))
        self._install_favicon()
        # capture initial routes so refreshes retain ASGI defaults
        self._base_routes = list(self.router.routes)
        self.jsonrpc_prefix = (
            jsonrpc_prefix
            if jsonrpc_prefix is not None
            else getattr(self, "JSONRPC_PREFIX", "/rpc")
        )
        self.system_prefix = (
            system_prefix
            if system_prefix is not None
            else getattr(self, "SYSTEM_PREFIX", "/system")
        )

        # public containers (mirrors used by bindings.router)
        self.models = initialize_model_registry(getattr(self, "MODELS", ()))
        self.schemas = SimpleNamespace()
        self.handlers = SimpleNamespace()
        self.hooks = tuple(getattr(self, "HOOKS", ()))
        self.state = SimpleNamespace()
        self.rpc = SimpleNamespace()
        self.rest = SimpleNamespace()
        self.routers: Dict[str, Any] = {}
        self.tables = AttrDict()
        self.columns: Dict[str, Tuple[str, ...]] = {}
        self.table_config: Dict[str, Dict[str, Any]] = {}
        self.core = SimpleNamespace()
        self.core_raw = SimpleNamespace()
        self.apis = list(getattr(self, "APIS", ()))
        self._event_handlers = {
            "startup": [],
            "shutdown": [],
        }

        # Router-level hooks map (merged into each model at include-time; precedence handled in bindings.hooks)
        self._router_hooks_map = copy.deepcopy(router_hooks) if router_hooks else None
        self._default_api: TigrblRouter | None = None
        self.mount_openrpc(path="/openrpc.json")
        self.mount_lens(path="/rdocs", spec_path="/openrpc.json")
        if apis:
            self.apis.extend(list(apis))
            self.include_apis(self.apis)

    @property
    def event_handlers(self) -> Dict[str, list[Callable[..., Any]]]:
        """Expose registered startup and shutdown callbacks by event name."""
        return self._event_handlers

    def add_event_handler(
        self,
        event_type: str,
        handler: Callable[..., Any],
    ) -> None:
        """Register a startup or shutdown handler."""
        if event_type not in self._event_handlers:
            raise ValueError(
                f"Unsupported event type '{event_type}'. "
                f"Expected one of: {tuple(self._event_handlers.keys())}."
            )
        self._event_handlers[event_type].append(handler)

    def on_event(
        self, event_type: str
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator form of :meth:`add_event_handler`."""

        def _decorator(handler: Callable[..., Any]) -> Callable[..., Any]:
            self.add_event_handler(event_type, handler)
            return handler

        return _decorator

    async def run_event_handlers(self, event_type: str) -> None:
        """Execute registered handlers for an event type in registration order."""
        if event_type not in self._event_handlers:
            raise ValueError(
                f"Unsupported event type '{event_type}'. "
                f"Expected one of: {tuple(self._event_handlers.keys())}."
            )
        for handler in self._event_handlers[event_type]:
            result = handler()
            if inspect.isawaitable(result):
                await result

    def add_middleware(self, middleware_class: Any, **options: Any) -> None:
        self._middlewares.append((middleware_class, options))

    def _install_favicon(self) -> None:
        self.mount_favicon(favicon_path=self._favicon_path)

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
                    # fallback: prefer model-local value, then append api-level
                    if isinstance(merged[k], list):
                        merged[k] = list(merged[k]) + list(v or [])
                    else:
                        merged[k] = v
        setattr(model, "__tigrbl_router_hooks__", merged)

    # ------------------------- primary operations -------------------------

    def _ensure_default_api(self) -> TigrblRouter:
        """Create and register the app-scoped default API when needed."""
        if self._default_api is None:
            self._default_api = TigrblRouter(
                engine=self.engine,
                router_hooks=self._router_hooks_map,
            )
            # Mirror current app auth knobs onto the default API.
            self._default_api.set_auth(
                authn=self._authn,
                allow_anon=self._allow_anon,
                authorize=self._authorize,
                optional_authn_dep=self._optional_authn_dep,
            )
            self.include_api(self._default_api)
        return self._default_api

    def include_model(
        self, model: type, *, prefix: str | None = None, mount_router: bool = True
    ) -> Tuple[type, Any]:
        """
        Include a model through an internal ``TigrblRouter`` mounted on this app.
        """
        default_api = self._ensure_default_api()

        result = default_api.include_model(
            model,
            prefix=prefix,
            mount_router=False,
        )
        if mount_router:
            _, router = result
            if router is not None:
                mount_prefix = prefix if prefix is not None else _default_prefix(model)
                self.include_router(router, prefix=mount_prefix)
        self._sync_default_api_namespaces()
        return result

    def include_models(
        self,
        models: Sequence[type],
        *,
        base_prefix: str | None = None,
        mount_router: bool = True,
    ) -> Dict[str, Any]:
        default_api = self._ensure_default_api()

        result = default_api.include_models(
            models,
            base_prefix=base_prefix,
            mount_router=False,
        )
        if mount_router:
            for model in models:
                router = getattr(
                    getattr(model, "rest", SimpleNamespace()),
                    "router",
                    None,
                )
                if router is None:
                    continue
                mount_prefix = (
                    f"{base_prefix}{_default_prefix(model)}"
                    if base_prefix is not None
                    else _default_prefix(model)
                )
                self.include_router(router, prefix=mount_prefix)
        self._sync_default_api_namespaces()
        return result

    def _sync_default_api_namespaces(self) -> None:
        """Mirror the auto-created API registries onto the app facade."""
        if self._default_api is None:
            return
        self.models = self._default_api.models
        self.schemas = self._default_api.schemas
        self.handlers = self._default_api.handlers
        self.hooks = self._default_api.hooks
        self.rpc = self._default_api.rpc
        self.rest = self._default_api.rest
        self.routers = self._default_api.routers
        self.tables = self._default_api.tables
        self.columns = self._default_api.columns
        self.table_config = self._default_api.table_config
        self.core = self._default_api.core
        self.core_raw = self._default_api.core_raw

    def include_api(
        self,
        api: Any,
        *,
        prefix: str | None = None,
        mount_router: bool = True,
    ) -> Any:
        """Mount a Tigrbl API router onto this app and track it."""
        if api not in self.apis:
            self.apis.append(api)
        if not mount_router:
            return api
        router = getattr(api, "router", api)
        if hasattr(self, "include_router"):
            self.include_router(router, prefix=prefix or "")
        return api

    def include_router(self, router: Any, *args: Any, **kwargs: Any) -> None:
        """Extend ASGI include_router to track Tigrbl APIs."""
        if hasattr(router, "models") and hasattr(router, "initialize"):
            self.include_api(
                router,
                prefix=kwargs.get("prefix"),
                mount_router=False,
            )
        super().include_router(router, *args, **kwargs)

    def include_apis(self, apis: Sequence[Any]) -> None:
        """Mount multiple APIs, supporting optional per-item prefixes."""
        for entry in apis:
            prefix = None
            api = entry
            if isinstance(entry, tuple) and entry:
                api = entry[0]
                if len(entry) > 1:
                    value = entry[1]
                    if isinstance(value, dict):
                        prefix = value.get("prefix")
                    elif isinstance(value, str):
                        prefix = value
            self.include_api(api, prefix=prefix)

    def initialize(
        self,
        *,
        schemas: Iterable[str] | None = None,
        sqlite_attachments: Mapping[str, str] | None = None,
        tables: Iterable[Any] | None = None,
    ):
        """Initialize DDL for the app and any attached APIs."""
        result = _ddl_initialize(
            self,
            schemas=schemas,
            sqlite_attachments=sqlite_attachments,
            tables=tables,
        )

        api_results = []
        for api in self.apis:
            init = getattr(api, "initialize", None)
            if callable(init):
                api_results.append(
                    init(
                        schemas=schemas,
                        sqlite_attachments=sqlite_attachments,
                        tables=tables,
                    )
                )

        awaitables = [r for r in [result, *api_results] if inspect.isawaitable(r)]
        if not awaitables:
            return None

        async def _inner():
            for item in [result, *api_results]:
                if inspect.isawaitable(item):
                    await item

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            asyncio.run(_inner())
            return None

        return loop.create_task(_inner())

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
        self.jsonrpc_prefix = px
        prov = _resolver.resolve_provider(api=self)
        get_db = prov.get_db if prov else None
        router = _mount_jsonrpc(
            self,
            self,
            prefix=px,
            get_db=get_db,
        )
        self._base_routes = list(self.router.routes)
        return router

    def mount_openapi(
        self,
        *,
        path: str = "/openapi.json",
        name: str = "__openapi__",
    ) -> Any:
        """Mount an OpenAPI JSON endpoint onto this instance."""
        return _mount_openapi(self, path=path, name=name)

    def mount_openrpc(
        self,
        *,
        path: str = "/openrpc.json",
        name: str = "openrpc_json",
        tags: list[str] | None = None,
    ) -> Any:
        """Mount an OpenRPC JSON endpoint onto this instance."""
        return _mount_openrpc(self, path=path, name=name, tags=tags)

    def openrpc(self) -> Dict[str, Any]:
        """Build and return the OpenRPC document for this app."""
        return _build_openrpc_spec(self)

    def mount_lens(
        self,
        *,
        path: str = "/lens",
        name: str = "__lens__",
        spec_path: str | None = None,
    ) -> Any:
        """Mount a tigrbl-lens HTML endpoint onto this instance."""
        return _mount_lens(self, path=path, name=name, spec_path=spec_path)

    def attach_diagnostics(
        self, *, prefix: str | None = None, app: Any | None = None
    ) -> Any:
        """Mount diagnostics router onto this app or the provided ``app``."""
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
        if app is None:
            self._base_routes = list(self.router.routes)
        return router

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
            if allow_anon is None:
                allow_anon = False
        if allow_anon is not None:
            self._allow_anon = bool(allow_anon)
        if authorize is not None:
            self._authorize = authorize
        if optional_authn_dep is not None:
            self._optional_authn_dep = optional_authn_dep

        if self._default_api is not None:
            self._default_api.set_auth(
                authn=self._authn,
                allow_anon=self._allow_anon,
                authorize=self._authorize,
                optional_authn_dep=self._optional_authn_dep,
            )
            self._sync_default_api_namespaces()

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
            if t is not None and not t.columns:
                continue
            if t is not None and t not in seen:
                seen.add(t)
                tables.append(t)
        return tables

    # ------------------------- repr -------------------------

    def __repr__(self) -> str:  # pragma: no cover
        return f"<TigrblApp models={list(self.models)} rpc={list(getattr(self.rpc, '__dict__', {}).keys())}>"
