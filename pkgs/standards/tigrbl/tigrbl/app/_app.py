# tigrbl/tigrbl/app/_app.py
from __future__ import annotations
from typing import Any

from ..router._routing import include_router
from ..router._router import Router
from ..engine.engine_spec import EngineCfg
from ..engine import resolver as _resolver
from ..engine import install_from_objects
from ..ddl import initialize as _ddl_initialize
from ._model_registry import initialize_table_registry
from .app_spec import AppSpec


class App(AppSpec):
    TITLE = "Tigrbl"
    DESCRIPTION = None
    VERSION = "0.1.0"
    LIFESPAN = None
    ROUTERS = ()
    OPS = ()
    TABLES = ()
    SCHEMAS = ()
    HOOKS = ()
    SECURITY_DEPS = ()
    DEPS = ()
    RESPONSE = None
    JSONRPC_PREFIX = "/rpc"
    SYSTEM_PREFIX = "/system"

    def __init__(self, *, engine: EngineCfg | None = None, **asgi_kwargs: Any) -> None:
        # Manually mirror ``AppSpec`` fields so the dataclass-generated ``repr``
        # and friends have expected attributes while runtime structures remain
        # mutable dictionaries or lists as needed.
        title = asgi_kwargs.pop("title", None)
        if title is not None:
            self.TITLE = title
        description = asgi_kwargs.pop("description", None)
        if description is not None:
            self.DESCRIPTION = description
        version = asgi_kwargs.pop("version", None)
        if version is not None:
            self.VERSION = version
        lifespan = asgi_kwargs.pop("lifespan", None)
        if lifespan is not None:
            self.LIFESPAN = lifespan
        get_db = asgi_kwargs.pop("get_db", None)
        if get_db is not None:
            self.get_db = get_db
        self.title = self.TITLE
        self.description = getattr(self, "DESCRIPTION", None)
        self.version = self.VERSION
        self.engine = engine if engine is not None else getattr(self, "ENGINE", None)
        self.routers = tuple(getattr(self, "ROUTERS", ()))
        self.ops = tuple(getattr(self, "OPS", ()))
        # Runtime registries use mutable containers (dict/namespace), but the
        # dataclass fields expect sequences. Storing a dict here satisfies both.
        self.tables = initialize_table_registry(getattr(self, "TABLES", ()))
        self.models = self.tables
        self.schemas = tuple(getattr(self, "SCHEMAS", ()))
        self.hooks = tuple(getattr(self, "HOOKS", ()))
        self.security_deps = tuple(getattr(self, "SECURITY_DEPS", ()))
        self.deps = tuple(getattr(self, "DEPS", ()))
        self.response = getattr(self, "RESPONSE", None)
        self.jsonrpc_prefix = getattr(self, "JSONRPC_PREFIX", "/rpc")
        self.system_prefix = getattr(self, "SYSTEM_PREFIX", "/system")
        self.lifespan = self.LIFESPAN

        self.router = Router(
            title=self.title,
            version=self.version,
            description=self.description,
            include_docs=True,
            **asgi_kwargs,
        )
        self.openapi_url = self.router.openapi_url
        self.docs_url = self.router.docs_url
        self.swagger_ui_version = self.router.swagger_ui_version
        _engine_ctx = self.engine
        if _engine_ctx is not None:
            _resolver.set_default(_engine_ctx)
            _resolver.resolve_provider()

    def include_router(self, other: Any, **kwargs: Any) -> None:
        return include_router(self.router, other, **kwargs)

    def add_route(self, path: str, endpoint: Any, **kwargs: Any) -> None:
        self.router.add_route(path, endpoint, **kwargs)

    def route(self, path: str, *, methods: Any, **kwargs: Any):
        return self.router.route(path, methods=methods, **kwargs)

    def install_engines(
        self, *, router: Any = None, tables: tuple[Any, ...] | None = None
    ) -> None:
        # If class declared ROUTERS/TABLES, use them unless explicit args are passed.
        routers = (router,) if router is not None else self.ROUTERS
        tables = tables if tables is not None else self.TABLES
        app_target = self.__class__
        if routers:
            for entry in routers:
                install_from_objects(app=app_target, router=entry, tables=tables)
        else:
            install_from_objects(app=app_target, router=None, tables=tables)

    def _collect_tables(self) -> list[Any]:
        seen = set()
        tables = []
        for model in self.router.models.values():
            if not hasattr(model, "__table__"):
                try:  # pragma: no cover - defensive remap
                    from ..table import Base
                    from ..table._base import _materialize_colspecs_to_sqla

                    _materialize_colspecs_to_sqla(model)
                    Base.registry.map_declaratively(model)
                except Exception:
                    pass
            table = getattr(model, "__table__", None)
            if table is not None and not table.columns:
                continue
            if table is not None and table not in seen:
                seen.add(table)
                tables.append(table)
        return tables

    async def _dispatch(self, req: Any):
        return await self.router._dispatch(req)

    async def _call_handler(self, route: Any, req: Any):
        return await self.router._call_handler(route, req)

    initialize = _ddl_initialize
