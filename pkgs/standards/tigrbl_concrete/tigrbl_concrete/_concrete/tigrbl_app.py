# tigrbl/_concrete/tigrbl_app.py
from __future__ import annotations

import asyncio
import copy
import inspect
from dataclasses import replace
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
from .tigrbl_router import TigrblRouter
from ._routing import add_route as _add_route_impl
from tigrbl_core._spec.op_spec import OpSpec
from tigrbl_core._spec.binding_spec import HttpRestBindingSpec
from tigrbl_core._spec.engine_spec import EngineCfg
from tigrbl_concrete._concrete import engine_resolver as _resolver
from tigrbl_concrete.ddl import initialize as _ddl_initialize
from tigrbl_concrete._mapping.router.common import (
    AttrDict,
    _default_prefix,
)
from tigrbl_concrete._mapping.router.rpc import rpc_call as _rpc_call
from tigrbl_concrete._mapping.model import rebind as _rebind, bind as _bind
from tigrbl_concrete.system import mount_diagnostics as _mount_diagnostics
from tigrbl_concrete.system import mount_lens as _mount_lens
from tigrbl_concrete.system import mount_openapi as _mount_openapi
from tigrbl_concrete.system import mount_openrpc as _mount_openrpc
from tigrbl_concrete.system import mount_swagger as _mount_swagger
from tigrbl_concrete.system import build_openrpc_spec as _build_openrpc_spec
from tigrbl_concrete.system.docs import build_openapi as _build_openapi
from ._op_registry import get_registry
from ._table_registry import TableRegistry
from tigrbl_core._spec.app_spec import AppSpec
from tigrbl_core._spec.app_spec import _seqify, normalize_app_spec
from tigrbl_core.config.constants import TIGRBL_GET_DB_ATTR
from tigrbl_concrete.system.favicon import FAVICON_PATH, mount_favicon
from tigrbl_concrete.system.docs.runtime_ops import register_runtime_route
from tigrbl_concrete._mapping.model_helpers import _OpSpecGroup


# optional compat: legacy transactional decorator
try:
    from .compat.transactional import transactional as _txn_decorator
except Exception:  # pragma: no cover
    _txn_decorator = None


class TigrblApp(_App):
    """
    Monolithic facade that owns:
      • containers (tables, schemas, handlers, hooks, rpc, rest, routers, columns, table_config, core proxies)
      • table inclusion (REST + RPC wiring)
      • JSON-RPC / diagnostics mounting
      • (optional) legacy-friendly helpers (transactional decorator, auth flags)

    It composes v3 primitives; you can still use the functions directly if you prefer.
    """

    TITLE = "TigrblApp"
    VERSION = "0.1.0"
    LIFESPAN = None
    MIDDLEWARES: Sequence[Any] = ()
    ROUTERS: Sequence[Any] = ()
    TABLES: Sequence[Any] = ()

    # --- optional auth knobs recognized by some middlewares/dispatchers (kept for back-compat) ---
    _authn: Any = None
    _allow_anon: bool = True
    _authorize: Any = None
    _optional_authn_dep: Any = None
    _allow_anon_ops: set[str] = set()
    _event_handlers: Dict[str, list[Callable[..., Any]]]

    mount_favicon = mount_favicon

    @staticmethod
    def _collect_declared_tables(owner: type) -> tuple[Any, ...]:
        collected: list[Any] = []
        seen: set[int] = set()
        for base in owner.__mro__:
            if "TABLES" not in base.__dict__:
                continue
            for table in tuple(base.__dict__.get("TABLES", ()) or ()):
                marker = id(table)
                if marker in seen:
                    continue
                seen.add(marker)
                collected.append(table)
        return tuple(collected)

    @classmethod
    def from_spec(cls, spec: AppSpec) -> "TigrblApp":
        """Materialize an app instance from an :class:`~tigrbl.AppSpec`."""
        spec = normalize_app_spec(spec)
        spec_tables = tuple(spec.tables or ())
        app = cls(
            engine=spec.engine,
            routers=tuple(spec.routers or ()),
            jsonrpc_prefix=spec.jsonrpc_prefix,
            system_prefix=spec.system_prefix,
            title=spec.title,
            version=spec.version,
            lifespan=spec.lifespan,
        )
        table_registry = TableRegistry(tables=spec_tables)
        app._table_registry = table_registry
        app.tables = AttrDict(table_registry)

        async def _initialize_from_spec() -> None:
            initialized = app.initialize(tables=spec_tables)
            if inspect.isawaitable(initialized):
                await initialized

        app.add_event_handler("startup", _initialize_from_spec)

        has_jsonrpc_binding = any(
            getattr(binding, "proto", "") == "http.jsonrpc"
            for table in tuple(spec.tables or ())
            for op_spec in tuple(getattr(table, "__tigrbl_ops__", ()) or ())
            for binding in tuple(getattr(op_spec, "bindings", ()) or ())
        )
        if has_jsonrpc_binding:
            app._ensure_default_router()
            existing_paths = {
                getattr(route, "path", None) for route in getattr(app, "routes", ())
            }
            if (
                spec.jsonrpc_prefix not in existing_paths
                and f"{spec.jsonrpc_prefix}/" not in existing_paths
            ):
                app.add_route(
                    spec.jsonrpc_prefix,
                    lambda *_args, **_kwargs: None,
                    methods=["POST"],
                )
        return app

    def __init__(
        self,
        *,
        engine: EngineCfg | None = None,
        routers: Sequence[Any] | None = None,
        mount_system: bool | None = None,
        profile: str | None = None,
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
            asgi_kwargs["title"] = title
        version = asgi_kwargs.pop("version", None)
        if version is not None:
            self.VERSION = version
            asgi_kwargs["version"] = version
        lifespan = asgi_kwargs.pop("lifespan", None)
        if lifespan is not None:
            self.LIFESPAN = lifespan
            asgi_kwargs["lifespan"] = lifespan
        super().__init__(engine=engine, **asgi_kwargs)
        self._authn = None
        self._allow_anon = True
        self._authorize = None
        self._optional_authn_dep = None
        self._allow_anon_ops: set[str] = set()
        self._middlewares: list[tuple[Any, dict[str, Any]]] = []
        self.middlewares = _seqify(getattr(self, "MIDDLEWARES", ()))
        declared_tables = self._collect_declared_tables(self.__class__)
        self._table_registry = TableRegistry(tables=declared_tables)
        self._favicon_path = favicon_path
        for mw in self.middlewares:
            mw_cls = getattr(mw, "cls", mw.__class__)
            self.add_middleware(mw_cls, **getattr(mw, "kwargs", {}))
        self._default_router: TigrblRouter | None = None
        self.jsonrpc_prefix = (
            jsonrpc_prefix
            if jsonrpc_prefix is not None
            else getattr(
                self,
                "jsonrpc_prefix",
                getattr(self, "JSONRPC_PREFIX", "/rpc"),
            )
        )
        self.system_prefix = (
            system_prefix
            if system_prefix is not None
            else getattr(
                self,
                "system_prefix",
                getattr(self, "SYSTEM_PREFIX", "/system"),
            )
        )
        if mount_system is None:
            mount_system = str(profile or "").lower() != "minimal"
        self.mount_system = bool(mount_system)

        # public containers (mirrors used by bindings.router)
        self.schemas = SimpleNamespace()
        self.handlers = SimpleNamespace()
        self.hooks = _seqify(getattr(self, "HOOKS", ()))
        self.state = SimpleNamespace()
        self.rpc = SimpleNamespace()
        self.rest = SimpleNamespace()
        self.routers: Dict[str, Any] = {}
        self.tables = AttrDict(self._table_registry)
        self.columns: Dict[str, Tuple[str, ...]] = {}
        self.table_config: Dict[str, Dict[str, Any]] = {}
        self.core = SimpleNamespace()
        self.core_raw = SimpleNamespace()
        self._install_favicon()
        initial_routers = list(_seqify(getattr(self, "ROUTERS", ())))
        self._event_handlers = {
            "startup": [],
            "shutdown": [],
        }

        # Router-level hooks map (merged into each table at include-time; precedence handled in bindings.hooks)
        self._router_hooks_map = copy.deepcopy(router_hooks) if router_hooks else None
        if self.mount_system:
            self.mount_openapi(path="/openapi.json")
            _mount_swagger(self, path="/docs")
            self.attach_diagnostics(prefix=self.system_prefix)
            self.mount_openrpc(path="/openrpc.json")
            self.mount_lens(path="/lens", spec_path="/openrpc.json")
        if routers:
            initial_routers.extend(list(routers))
        if initial_routers:
            self.include_routers(initial_routers)
        self._base_routes = list(self.routes)

        declared_table_models = []
        seen_declared_table_ids: set[int] = set()
        for model in self._table_registry.values():
            if not isinstance(model, type):
                continue
            model_id = id(model)
            if model_id in seen_declared_table_ids:
                continue
            seen_declared_table_ids.add(model_id)
            declared_table_models.append(model)
        if declared_table_models:
            self.include_tables(declared_table_models)

        if (
            self._has_local_op_declarations()
            and self.__class__.__name__ not in self._table_registry
        ):
            self.include_table(self.__class__)

    def _has_local_op_declarations(self) -> bool:
        """Return True when the app subclass declares op_alias/op_ctx operations."""
        app_cls = self.__class__
        if getattr(app_cls, "__tigrbl_ops__", ()):
            return True

        for attr in app_cls.__dict__.values():
            fn = getattr(attr, "__func__", attr)
            if getattr(fn, "__tigrbl_op_spec__", None) is not None:
                return True
            if getattr(fn, "__tigrbl_op_decl__", None) is not None:
                return True
        return False

    @property
    def event_handlers(self) -> Dict[str, list[Callable[..., Any]]]:
        """Expose registered startup and shutdown callbacks by event name."""
        return self._event_handlers

    @property
    def on_startup(self) -> list[Callable[..., Any]]:
        """Compatibility alias for startup handlers list."""
        return self._event_handlers["startup"]

    @property
    def on_shutdown(self) -> list[Callable[..., Any]]:
        """Compatibility alias for shutdown handlers list."""
        return self._event_handlers["shutdown"]

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
        self.mount_favicon(file_path=self._favicon_path)

    # ------------------------- internal helpers -------------------------

    @staticmethod
    def _merge_router_hooks_into_table(table: type, hooks_map: Any) -> None:
        """
        Install Router-level hooks on the table so the binder can see them.
        Accepted shapes:
            {phase: [fn, ...]}                           # global, all aliases
            {alias: {phase: [fn, ...]}, "*": {...}}      # per-alias + wildcard
        If the table already has __tigrbl_router_hooks__, we shallow-merge keys.
        """
        if not hooks_map:
            return
        existing = getattr(table, "__tigrbl_router_hooks__", None)
        if existing is None:
            setattr(table, "__tigrbl_router_hooks__", copy.deepcopy(hooks_map))
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
                    # fallback: prefer table-local value, then append router-level
                    if isinstance(merged[k], list):
                        merged[k] = list(merged[k]) + list(v or [])
                    else:
                        merged[k] = v
        setattr(table, "__tigrbl_router_hooks__", merged)

    # ------------------------- primary operations -------------------------

    def _ensure_default_router(self) -> TigrblRouter:
        """Create and register the app-scoped default Router when needed."""
        if self._default_router is None:
            self._default_router = TigrblRouter(
                engine=self.engine,
                jsonrpc_prefix=self.jsonrpc_prefix,
                system_prefix=self.system_prefix,
                router_hooks=self._router_hooks_map,
                dependencies=list(getattr(self, "dependencies", ()) or ()),
            )
            # Mirror current app auth knobs onto the default Router.
            self._default_router.set_auth(
                authn=self._authn,
                allow_anon=self._allow_anon,
                authorize=self._authorize,
                optional_authn_dep=self._optional_authn_dep,
            )
            self.include_router(self._default_router)
        return self._default_router

    def include_table(
        self, table: type, *, prefix: str | None = None, mount_router: bool = True
    ) -> Tuple[type, Any]:
        """
        Include a table through an internal ``TigrblRouter`` mounted on this app.
        """
        default_router = self._ensure_default_router()

        result = default_router.include_table(
            table,
            prefix=prefix,
            mount_router=False,
        )
        if mount_router:
            _, router = result
            if router is not None:
                mount_prefix = prefix if prefix is not None else _default_prefix(table)
                self.include_router(router, prefix=mount_prefix)
        self._sync_default_router_namespaces()
        self._auto_mount_jsonrpc_if_bound()
        return result

    def include_tables(
        self,
        tables: Sequence[type],
        *,
        base_prefix: str | None = None,
        mount_router: bool = True,
    ) -> Dict[str, Any]:
        default_router = self._ensure_default_router()

        result = default_router.include_tables(
            tables,
            base_prefix=base_prefix,
            mount_router=False,
        )
        if mount_router:
            for table in tables:
                router = getattr(
                    getattr(table, "rest", SimpleNamespace()),
                    "router",
                    None,
                )
                if router is None:
                    continue
                mount_prefix = (
                    f"{base_prefix}{_default_prefix(table)}"
                    if base_prefix is not None
                    else _default_prefix(table)
                )
                self.include_router(router, prefix=mount_prefix)
        self._sync_default_router_namespaces()
        self._auto_mount_jsonrpc_if_bound()
        return result

    def _auto_mount_jsonrpc_if_bound(self) -> None:
        has_rpc_binding = any(
            getattr(binding, "proto", "") == "http.jsonrpc"
            for table in tuple(getattr(self, "tables", {}).values())
            for op_spec in tuple(getattr(getattr(table, "ops", None), "all", ()) or ())
            for binding in tuple(getattr(op_spec, "bindings", ()) or ())
        )
        if has_rpc_binding:
            self.mount_jsonrpc()

    def _ensure_system_route_model(self) -> type:
        model_name = "__tigrbl_system_routes__"
        model = self.tables.get(model_name)
        if model is None:
            model = type("TigrblSystemRoutes", (), {})
            model.resource_name = "system_routes"
            model.hooks = SimpleNamespace()
            model.ops = SimpleNamespace(by_alias={})
            model.opspecs = SimpleNamespace(all=())
            self.tables[model_name] = model
        return model

    def _sync_default_router_namespaces(self) -> None:
        """Mirror the auto-created Router registries onto the app facade."""
        if self._default_router is None:
            return
        existing_tables = dict(getattr(self, "tables", {}) or {})
        self.schemas = self._default_router.schemas
        self.handlers = self._default_router.handlers
        self.hooks = self._default_router.hooks
        self.rpc = self._default_router.rpc
        self.rest = self._default_router.rest
        self.routers = self._default_router.routers
        self._table_registry = self._default_router.tables
        self.tables = self._default_router.tables
        self.columns = self._default_router.columns
        self.table_config = self._default_router.table_config
        self.core = self._default_router.core
        self.core_raw = self._default_router.core_raw

        # Preserve app-level system models (for docs/metadata runtime ops) that
        # may have been mounted before the default router existed.
        for model_name, model in existing_tables.items():
            self.tables.setdefault(model_name, model)
            self._default_router.tables.setdefault(model_name, model)

    def include_router(
        self,
        router: Any,
        *,
        prefix: str | None = None,
        mount_router: bool = True,
    ) -> Any:
        """Mount a Router and mirror mounted routes into runtime op metadata."""

        def _normalize_mount_prefix(value: str | None) -> str:
            if not value:
                return ""
            token = str(value).strip()
            if not token:
                return ""
            if not token.startswith("/"):
                token = f"/{token}"
            return token.rstrip("/")

        def _apply_mount_prefix_to_model_bindings(
            model: type, mount_prefix: str
        ) -> None:
            if not mount_prefix:
                return

            ops_ns = getattr(model, "ops", None)
            specs = tuple(getattr(ops_ns, "all", ()) or ())
            if not specs:
                return

            updated_specs: list[Any] = []
            changed = False
            for spec in specs:
                bindings = tuple(getattr(spec, "bindings", ()) or ())
                updated_bindings: list[Any] = []
                local_changed = False
                for binding in bindings:
                    if not isinstance(binding, HttpRestBindingSpec):
                        updated_bindings.append(binding)
                        continue

                    path = str(binding.path or "")
                    if not path.startswith("/"):
                        path = f"/{path}"
                    prefixed_path = (
                        path
                        if path == mount_prefix or path.startswith(f"{mount_prefix}/")
                        else f"{mount_prefix}{path}"
                    )
                    if prefixed_path != binding.path:
                        local_changed = True
                        updated_bindings.append(replace(binding, path=prefixed_path))
                    else:
                        updated_bindings.append(binding)

                if local_changed:
                    changed = True
                    updated_specs.append(
                        replace(spec, bindings=tuple(updated_bindings))
                    )
                else:
                    updated_specs.append(spec)

            if not changed:
                return

            updated_all = tuple(updated_specs)
            by_alias: dict[str, _OpSpecGroup] = {}
            grouped_specs: dict[str, list[Any]] = {}
            by_key: dict[tuple[str, str], Any] = {}
            for spec in updated_all:
                grouped_specs.setdefault(spec.alias, []).append(spec)
                by_key[(spec.alias, spec.target)] = spec

            for alias, specs_for_alias in grouped_specs.items():
                by_alias[alias] = _OpSpecGroup(tuple(specs_for_alias))

            updated_ops_ns = SimpleNamespace(
                all=updated_all, by_alias=by_alias, by_key=by_key
            )
            model.ops = updated_ops_ns
            model.opspecs = updated_ops_ns

        mount_prefix = _normalize_mount_prefix(
            prefix if prefix is not None else getattr(router, "prefix", None)
        )

        if isinstance(self.routers, dict):
            key = (
                getattr(router, "name", None)
                or getattr(router, "__name__", None)
                or str(id(router))
            )
            existing = self.routers.get(key)
            if existing is not router:
                if existing is None:
                    self.routers[key] = router
                else:
                    self.routers[f"{key}:{id(router)}"] = router
        else:
            if router not in self.routers:
                self.routers.append(router)
        router_engine = getattr(router, "engine", None)
        if router_engine is not None and getattr(self, "engine", None) is None:
            self.engine = router_engine
            if _resolver.resolve_provider() is None:
                _resolver.set_default(router_engine)

        router_tables = getattr(router, "tables", None)
        if isinstance(router_tables, dict) and router_tables:
            resolved_tables: Dict[str, type] = {}
            core_ns = getattr(router, "core", None)
            for name, table in router_tables.items():
                model = table if isinstance(table, type) else None
                if model is None and core_ns is not None:
                    core_proxy = getattr(core_ns, name, None)
                    model = getattr(core_proxy, "_model", None)
                if isinstance(model, type):
                    resolved_tables[name] = model
                    resolved_tables.setdefault(getattr(model, "__name__", name), model)

            for name, table in resolved_tables.items():
                self.tables.setdefault(name, table)
            if self._default_router is not None and self._default_router is not router:
                for name, table in resolved_tables.items():
                    self._default_router.tables.setdefault(name, table)

        if self._default_router is not None and self._default_router is not router:
            incoming_get_db = getattr(router, "get_db", None)
            default_get_db = getattr(self._default_router, "get_db", None)
            if callable(incoming_get_db) and not callable(default_get_db):
                self._default_router.get_db = incoming_get_db
                for model in tuple(getattr(self, "tables", {}).values()):
                    if not isinstance(model, type):
                        continue
                    if not callable(getattr(model, TIGRBL_GET_DB_ATTR, None)):
                        setattr(model, TIGRBL_GET_DB_ATTR, incoming_get_db)

        route_models: Dict[str, type] = {}
        for route in getattr(router, "routes", ()):
            model = getattr(route, "tigrbl_model", None)
            if not isinstance(model, type):
                continue
            if not isinstance(model, type):
                continue
            model_name = getattr(model, "__name__", None)
            if isinstance(model_name, str) and model_name:
                route_models.setdefault(model_name, model)

        if route_models:
            for table in route_models.values():
                _apply_mount_prefix_to_model_bindings(table, mount_prefix)
            for name, table in route_models.items():
                self.tables.setdefault(name, table)
            if self._default_router is not None and self._default_router is not router:
                for name, table in route_models.items():
                    self._default_router.tables.setdefault(name, table)

        for route in getattr(router, "routes", ()):
            if getattr(route, "tigrbl_model", None) is not None:
                continue
            endpoint = getattr(route, "endpoint", None)
            path = getattr(route, "path", None)
            methods = tuple(
                sorted(
                    str(method).upper()
                    for method in (getattr(route, "methods", ()) or ())
                    if str(method).upper() not in {"HEAD", "OPTIONS"}
                )
            )
            if not callable(endpoint) or not isinstance(path, str) or not methods:
                continue
            full_path = (
                path
                if not mount_prefix
                else path
                if path == mount_prefix or path.startswith(f"{mount_prefix}/")
                else f"{mount_prefix}{path if path.startswith('/') else '/' + path}"
            )
            alias = f"route_{'_'.join(methods).lower()}_{full_path.strip('/').replace('/', '_').replace('{', '').replace('}', '') or 'root'}"
            register_runtime_route(
                self,
                path=full_path,
                methods=methods,
                alias=alias,
                endpoint=endpoint,
            )

        if not mount_router:
            return router
        super().include_router(router, prefix=prefix)
        return router

    def add_router_route(self, path: str, endpoint: Any, **kwargs: Any) -> None:
        """Register a route directly on this app instance."""
        _add_route_impl(self, path, endpoint, **kwargs)

    def add_route(self, path: str, endpoint: Any, **kwargs: Any) -> None:
        """Register a route directly on this app instance."""
        _add_route_impl(self, path, endpoint, **kwargs)

    def include_routers(self, routers: Sequence[Any]) -> None:
        """Mount multiple Routers, supporting optional per-item prefixes."""
        for entry in routers:
            prefix = None
            router = entry
            if isinstance(entry, tuple) and entry:
                router = entry[0]
                if len(entry) > 1:
                    value = entry[1]
                    if isinstance(value, dict):
                        prefix = value.get("prefix")
                    elif isinstance(value, str):
                        prefix = value
            self.include_router(router, prefix=prefix)

    def initialize(
        self,
        *,
        schemas: Iterable[str] | None = None,
        sqlite_attachments: Mapping[str, str] | None = None,
        tables: Iterable[Any] | None = None,
    ):
        """Initialize DDL for the app and any attached Routers."""
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
            try:
                asyncio.get_running_loop()
            except RuntimeError:
                result = None
            else:

                async def _noop() -> None:
                    return None

                result = _noop()

        router_results = []
        attached_routers = list(
            self.routers.values() if isinstance(self.routers, dict) else self.routers
        )
        for router in attached_routers:
            init = getattr(router, "initialize", None)
            if callable(init):
                try:
                    router_results.append(
                        init(
                            schemas=schemas,
                            sqlite_attachments=sqlite_attachments,
                        )
                    )
                except ValueError as exc:
                    if str(exc) != "Engine provider is not configured":
                        raise

        awaitables = [r for r in [result, *router_results] if inspect.isawaitable(r)]
        if not awaitables:
            try:
                asyncio.get_running_loop()
            except RuntimeError:
                return None

            async def _noop() -> None:
                return None

            return _noop()

        async def _inner():
            for item in [result, *router_results]:
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
        table_or_name: type | str,
        method: str,
        payload: Any = None,
        *,
        db: Any | None = None,
        request: Any = None,
        ctx: Optional[Dict[str, Any]] = None,
    ) -> Any:
        return await _rpc_call(
            self, table_or_name, method, payload, db=db, request=request, ctx=ctx
        )

    # ------------------------- extras / mounting -------------------------

    def mount_jsonrpc(self, *, prefix: str | None = None) -> Any:
        if prefix is not None:
            self.jsonrpc_prefix = prefix

        router = self._ensure_default_router()
        existing_paths = {getattr(route, "path", None) for route in self.routes}
        base_prefix = self.jsonrpc_prefix.rstrip("/") or "/"
        candidate_paths = (
            base_prefix,
            f"{base_prefix}/" if base_prefix != "/" else "/",
        )
        for path in candidate_paths:
            if path in existing_paths:
                continue
            self.add_route(path, lambda *_args, **_kwargs: None, methods=["POST"])
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

    def openapi(self) -> Dict[str, Any]:
        """Build and return the OpenAPI document for this app."""
        return _build_openapi(self)

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
        prov = _resolver.resolve_provider(router=self)
        get_db = prov.get_db if prov else None
        router = _mount_diagnostics(self, get_db=get_db)
        include_self = getattr(self, "include_router", None)
        if callable(include_self):
            include_self(router, prefix=px)
        if app is not None and app is not self:
            include_other = getattr(app, "include_router", None)
            if callable(include_other):
                include_other(router, prefix=px)
        runtime = getattr(self, "runtime", None)
        kernel = getattr(runtime, "kernel", None)
        invalidate = getattr(kernel, "invalidate_kernelz_payload", None)
        if callable(invalidate):
            invalidate(self)
            if app is not None and app is not self:
                invalidate(app)
        if app is None:
            self._base_routes = list(self.routes)
        return router

    # ------------------------- registry passthroughs -------------------------

    def registry(self, table: type):
        """Return the per-table OpspecRegistry."""
        return get_registry(table)

    def bind(self, table: type) -> Tuple[OpSpec, ...]:
        """Bind/rebuild a table in place (without mounting)."""
        self._merge_router_hooks_into_table(table, self._router_hooks_map)
        return _bind(table)

    def rebind(
        self, table: type, *, changed_keys: Optional[set[tuple[str, str]]] = None
    ) -> Tuple[OpSpec, ...]:
        """Targeted rebuild of a bound table."""
        return _rebind(table, changed_keys=changed_keys)

    # ------------------------- legacy helpers -------------------------

    def transactional(self, *dargs, **dkw):
        """
        Legacy-friendly decorator: @router.transactional(...)
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

        if self._default_router is not None:
            self._default_router.set_auth(
                authn=self._authn,
                allow_anon=self._allow_anon,
                authorize=self._authorize,
                optional_authn_dep=self._optional_authn_dep,
            )
            self._sync_default_router_namespaces()

        # Security refresh is handled by the default router's set_auth call above.

    def _refresh_security(self) -> None:
        """Re-seed auth deps on tables and rebuild routers."""
        # Reset router to baseline and allow_anon ops cache
        self.routes = list(getattr(self, "_base_routes", self.routes))
        self._allow_anon_ops = set()
        default_router = self._ensure_default_router()
        for table in self._table_registry.values():
            default_router.include_table(table, mount_router=False)
            router = getattr(getattr(table, "rest", SimpleNamespace()), "router", None)
            if router is None:
                continue
            self.include_router(router, prefix=_default_prefix(table))
        self._sync_default_router_namespaces()

    def _collect_tables(self):
        # dedupe; handle multiple DeclarativeBases (multiple metadatas)
        seen = set()
        tables = []
        for m in self._table_registry.values():
            t = getattr(m, "__table__", None)
            if t is not None and not t.columns:
                continue
            if t is not None and t not in seen:
                seen.add(t)
                tables.append(t)
        return tables

    # ------------------------- repr -------------------------

    def __repr__(self) -> str:  # pragma: no cover
        return f"<TigrblApp tables={list(self._table_registry)} rpc={list(getattr(self.rpc, '__dict__', {}).keys())}>"
