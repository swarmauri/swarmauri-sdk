from __future__ import annotations

from typing import Any

from ..app._model_registry import initialize_table_registry
from .._spec.app_spec import AppSpec
from ..ddl import initialize as _ddl_initialize
from ..engine import install_from_objects
from ..mapping import engine_resolver as _resolver
from .._spec.engine_spec import EngineCfg
from ..router._routing import (
    include_router as _include_router_impl,
    merge_tags as _merge_tags_impl,
    normalize_prefix as _normalize_prefix_impl,
)
from ..runtime.gw.executor import RawEnvelopeExecutor
from ..runtime.gw.raw import GwRawEnvelope


class App(AppSpec):
    @staticmethod
    def _merge_seq_attr(
        app: type,
        attr: str,
        *,
        include_inherited: bool = False,
        reverse: bool = False,
    ) -> tuple[Any, ...]:
        values: list[Any] = []
        mro = reversed(app.__mro__) if reverse else app.__mro__
        for base in mro:
            if include_inherited:
                if not hasattr(base, attr):
                    continue
                seq = getattr(base, attr) or ()
            else:
                seq = base.__dict__.get(attr, ()) or ()
            try:
                values.extend(seq)
            except TypeError:  # pragma: no cover - non-iterable
                values.append(seq)
        return tuple(values)

    @classmethod
    def _collect_mro_spec(cls) -> AppSpec:
        sentinel = object()
        title: Any = sentinel
        version: Any = sentinel
        engine: Any | None = sentinel  # type: ignore[assignment]
        response: Any = sentinel
        jsonrpc_prefix: Any = sentinel
        system_prefix: Any = sentinel
        lifespan: Any = sentinel

        for base in cls.__mro__:
            if "TITLE" in base.__dict__ and title is sentinel:
                title = base.__dict__["TITLE"]
            if "VERSION" in base.__dict__ and version is sentinel:
                version = base.__dict__["VERSION"]
            if "ENGINE" in base.__dict__ and engine is sentinel:
                engine = base.__dict__["ENGINE"]
            if "RESPONSE" in base.__dict__ and response is sentinel:
                response = base.__dict__["RESPONSE"]
            if "JSONRPC_PREFIX" in base.__dict__ and jsonrpc_prefix is sentinel:
                jsonrpc_prefix = base.__dict__["JSONRPC_PREFIX"]
            if "SYSTEM_PREFIX" in base.__dict__ and system_prefix is sentinel:
                system_prefix = base.__dict__["SYSTEM_PREFIX"]
            if "LIFESPAN" in base.__dict__ and lifespan is sentinel:
                lifespan = base.__dict__["LIFESPAN"]

        if title is sentinel:
            title = "Tigrbl"
        if version is sentinel:
            version = "0.1.0"
        if engine is sentinel:
            engine = None
        if response is sentinel:
            response = None
        if jsonrpc_prefix is sentinel:
            jsonrpc_prefix = "/rpc"
        if system_prefix is sentinel:
            system_prefix = "/system"
        if lifespan is sentinel:
            lifespan = None

        include_inherited_routers = "ROUTERS" not in cls.__dict__
        return AppSpec(
            title=title,
            version=version,
            engine=engine,
            routers=cls._merge_seq_attr(
                cls,
                "ROUTERS",
                include_inherited=include_inherited_routers,
                reverse=include_inherited_routers,
            ),
            ops=cls._merge_seq_attr(cls, "OPS"),
            tables=cls._merge_seq_attr(cls, "TABLES"),
            schemas=cls._merge_seq_attr(cls, "SCHEMAS"),
            hooks=cls._merge_seq_attr(cls, "HOOKS"),
            security_deps=cls._merge_seq_attr(cls, "SECURITY_DEPS"),
            deps=cls._merge_seq_attr(cls, "DEPS"),
            response=response,
            jsonrpc_prefix=jsonrpc_prefix,
            system_prefix=system_prefix,
            middlewares=cls._merge_seq_attr(cls, "MIDDLEWARES"),
            lifespan=lifespan,
        )

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
        collected_spec = self.__class__._collect_mro_spec()

        title = asgi_kwargs.pop("title", None)
        if title is not None:
            self.TITLE = title
        else:
            title = collected_spec.title
        version = asgi_kwargs.pop("version", None)
        if version is not None:
            self.VERSION = version
        else:
            version = collected_spec.version
        lifespan = asgi_kwargs.pop("lifespan", None)
        if lifespan is not None:
            self.LIFESPAN = lifespan
        else:
            lifespan = collected_spec.lifespan
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
        self.title = title
        self.version = version
        self.description = description
        self.openapi_url = openapi_url
        self.docs_url = docs_url
        self.debug = debug
        self.swagger_ui_version = swagger_ui_version
        self.engine = engine if engine is not None else collected_spec.engine
        self.routers = tuple(collected_spec.routers)
        self.ops = tuple(collected_spec.ops)
        self.tables = initialize_table_registry(collected_spec.tables)
        self.schemas = tuple(collected_spec.schemas)
        self.hooks = tuple(collected_spec.hooks)
        self.security_deps = tuple(collected_spec.security_deps)
        self.deps = tuple(collected_spec.deps)
        self.response = collected_spec.response
        self.jsonrpc_prefix = collected_spec.jsonrpc_prefix
        self.system_prefix = collected_spec.system_prefix
        self.lifespan = lifespan

        from ._router import Router

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
