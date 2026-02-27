from __future__ import annotations

from typing import Any

from ..app._model_registry import initialize_table_registry
from ..specs.app_spec import AppSpec
from ..ddl import initialize as _ddl_initialize
from ..engine import install_from_objects
from ..mapping import engine_resolver as _resolver
from ..specs.engine_spec import EngineCfg
from ..router import Router
from ..router._routing import (
    include_router as _include_router_impl,
    merge_tags as _merge_tags_impl,
    normalize_prefix as _normalize_prefix_impl,
)
from ..runtime.gw.executor import RawEnvelopeExecutor
from ..runtime.gw.raw import GwRawEnvelope


class App(AppSpec):
    TITLE = "Tigrbl"
    VERSION = "0.1.0"
    LIFESPAN = None
    ROUTERS = ()
    OPS = ()
    TABLES = ()
    SCHEMAS = ()
    HOOKS = ()
    DESCRIPTION = None
    OPENAPI_URL = "/openapi.json"
    DOCS_URL = "/docs"
    DEBUG = False
    SWAGGER_UI_VERSION = "5.31.0"
    SECURITY_DEPS = ()
    DEPS = ()
    RESPONSE = None
    JSONRPC_PREFIX = "/rpc"
    SYSTEM_PREFIX = "/system"

    def __init__(self, *, engine: EngineCfg | None = None, **asgi_kwargs: Any) -> None:
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
        description = asgi_kwargs.pop("description", None)
        if description is None:
            description = getattr(self, "DESCRIPTION", None)
        openapi_url = asgi_kwargs.pop("openapi_url", None)
        if openapi_url is None:
            openapi_url = getattr(self, "OPENAPI_URL", "/openapi.json")
        docs_url = asgi_kwargs.pop("docs_url", None)
        if docs_url is None:
            docs_url = getattr(self, "DOCS_URL", "/docs")
        debug = asgi_kwargs.pop("debug", None)
        if debug is None:
            debug = bool(getattr(self, "DEBUG", False))
        swagger_ui_version = asgi_kwargs.pop("swagger_ui_version", None)
        if swagger_ui_version is None:
            swagger_ui_version = getattr(self, "SWAGGER_UI_VERSION", "5.31.0")
        include_docs = asgi_kwargs.pop("include_docs", None)
        if include_docs is None:
            include_docs = bool(getattr(self, "INCLUDE_DOCS", False))
        self.title = self.TITLE
        self.version = self.VERSION
        self.description = description
        self.openapi_url = openapi_url
        self.docs_url = docs_url
        self.debug = debug
        self.swagger_ui_version = swagger_ui_version
        self.engine = engine if engine is not None else getattr(self, "ENGINE", None)
        self.routers = tuple(getattr(self, "ROUTERS", ()))
        self.ops = tuple(getattr(self, "OPS", ()))
        self.tables = initialize_table_registry(getattr(self, "TABLES", ()))
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
            description=self.description,
            openapi_url=self.openapi_url,
            docs_url=self.docs_url,
            debug=self.debug,
            swagger_ui_version=self.swagger_ui_version,
            include_docs=include_docs,
            **asgi_kwargs,
        )
        self.executor = RawEnvelopeExecutor(app=self)
        _engine_ctx = self.engine
        if _engine_ctx is not None:
            _resolver.set_default(_engine_ctx)
            _resolver.resolve_provider()

    @property
    def router(self) -> "App":
        return self

    def install_engines(
        self, *, router: Any = None, tables: tuple[Any, ...] | None = None
    ) -> None:
        routers = (router,) if router is not None else self.ROUTERS
        tables = tables if tables is not None else self.TABLES
        if routers:
            for a in routers:
                install_from_objects(app=self, router=a, tables=tables)
        else:
            install_from_objects(app=self, router=None, tables=tables)

    async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> None:
        env = GwRawEnvelope(kind="asgi3", scope=scope, receive=receive, send=send)
        await self.executor.invoke(env)

    def _normalize_prefix(self, prefix: str) -> str:
        return _normalize_prefix_impl(prefix)

    def _merge_tags(self, tags: list[str] | None) -> list[str] | None:
        return _merge_tags_impl(getattr(self, "tags", None), tags)

    def include_router(self, router: Any, *, prefix: str | None = None) -> Any:
        routed = getattr(router, "router", router)
        _include_router_impl(self, routed, prefix=prefix or "")
        return router

    initialize = _ddl_initialize
