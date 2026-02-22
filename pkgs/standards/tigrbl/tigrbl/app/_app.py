# tigrbl/tigrbl/v3/app/_app.py
from __future__ import annotations
from typing import Any

from ..router._api import Router
from ..engine.engine_spec import EngineCfg
from ..engine import resolver as _resolver
from ..engine import install_from_objects
from ..ddl import initialize as _ddl_initialize
from ._model_registry import initialize_model_registry
from .app_spec import AppSpec


class App(AppSpec):
    TITLE = "Tigrbl"
    VERSION = "0.1.0"
    LIFESPAN = None
    ROUTERS = ()
    OPS = ()
    MODELS = ()
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
        self.version = self.VERSION
        self.engine = engine if engine is not None else getattr(self, "ENGINE", None)
        self.routers = tuple(getattr(self, "ROUTERS", ()))
        self.ops = tuple(getattr(self, "OPS", ()))
        # Runtime registries use mutable containers (dict/namespace), but the
        # dataclass fields expect sequences. Storing a dict here satisfies both.
        self.models = initialize_model_registry(getattr(self, "MODELS", ()))
        self.schemas = tuple(getattr(self, "SCHEMAS", ()))
        self.hooks = tuple(getattr(self, "HOOKS", ()))
        self.security_deps = tuple(getattr(self, "SECURITY_DEPS", ()))
        self.deps = tuple(getattr(self, "DEPS", ()))
        self.response = getattr(self, "RESPONSE", None)
        self.jsonrpc_prefix = getattr(self, "JSONRPC_PREFIX", "/rpc")
        self.system_prefix = getattr(self, "SYSTEM_PREFIX", "/system")
        self.lifespan = self.LIFESPAN

        Router.__init__(
            self,
            engine=self.engine,
            title=self.title,
            version=self.version,
            include_docs=False,
            **asgi_kwargs,
        )
        _engine_ctx = self.engine
        if _engine_ctx is not None:
            _resolver.set_default(_engine_ctx)
            _resolver.resolve_provider()

    def install_engines(
        self, *, router: Any = None, models: tuple[Any, ...] | None = None
    ) -> None:
        # If class declared ROUTERS/MODELS, use them unless explicit args are passed.
        routers = (router,) if router is not None else self.ROUTERS
        models = models if models is not None else self.MODELS
        if routers:
            for a in routers:
                install_from_objects(app=self, router=a, models=models)
        else:
            install_from_objects(app=self, router=None, models=models)

    def _collect_tables(self) -> list[Any]:
        seen = set()
        tables = []
        for model in self.models.values():
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
        return await Router._dispatch(self, req)

    async def _call_handler(self, route: Any, req: Any):
        return await Router._call_handler(self, route, req)

    initialize = _ddl_initialize


for _router_method_name in (
    "__call__",
    "_execute_dependency_tokens",
    "_execute_route_dependencies",
    "_invoke_dependency",
    "_is_metadata_route",
    "_merge_tags",
    "_normalize_prefix",
    "_request_from_asgi",
    "_request_from_wsgi",
    "_resolve_handler_kwargs",
    "_route_match_priority",
    "_router_call",
    "add_api_route",
    "add_route",
    "call_handler",
    "delete",
    "dispatch",
    "get",
    "patch",
    "post",
    "put",
    "route",
):
    setattr(App, _router_method_name, getattr(Router, _router_method_name))
