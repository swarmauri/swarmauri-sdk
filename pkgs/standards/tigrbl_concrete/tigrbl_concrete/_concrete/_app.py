from __future__ import annotations

from typing import Any

from tigrbl_kernel import _default_kernel
from ._table_registry import TableRegistry
from tigrbl_base._base import AppBase
from tigrbl_concrete.ddl import initialize as _ddl_initialize
from ._engine import Engine
from tigrbl_concrete._concrete import engine_resolver as _resolver
from tigrbl_core._spec.app_spec import AppSpec
from tigrbl_core._spec.engine_spec import EngineCfg
from ._routing import (
    include_router as _include_router_impl,
    merge_tags as _merge_tags_impl,
    normalize_prefix as _normalize_prefix_impl,
)
from tigrbl_runtime.runtime import Runtime
from tigrbl_typing.gw.raw import GwRawEnvelope


class App(AppBase):
    @classmethod
    def collect(cls) -> AppSpec:
        """Collect and normalize AppSpec configuration for this App class."""
        return AppSpec.collect(cls)

    @classmethod
    def _collect_mro_spec(cls) -> AppSpec:
        return cls.collect()

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
        collected_spec = self.__class__.bind_spec(collected_spec, parent=self)

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
        self.tables = TableRegistry(tables=collected_spec.tables)
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
        # Router.__init__ seeds several attributes from class-level defaults.
        # Re-apply merged AppSpec values so MRO-collected app configuration
        # remains the source of truth for the app instance.
        self.routers = tuple(collected_spec.routers)
        self.ops = tuple(collected_spec.ops)
        self.tables = TableRegistry(tables=collected_spec.tables)
        self.schemas = tuple(collected_spec.schemas)
        self.hooks = tuple(collected_spec.hooks)
        self.security_deps = tuple(collected_spec.security_deps)
        self.deps = tuple(collected_spec.deps)
        self.response = collected_spec.response
        self.jsonrpc_prefix = collected_spec.jsonrpc_prefix
        self.system_prefix = collected_spec.system_prefix

        _engine_ctx = self.engine
        if _engine_ctx is not None:
            _resolver.set_default(_engine_ctx)
            _resolver.resolve_provider()

        self.runtime = Runtime(
            default_executor=getattr(self, "DEFAULT_EXECUTOR", "numba_packed")
        )
        self._compiled_plan: tuple[Any, Any | None] | None = None

    @property
    def router(self) -> "App":
        return self

    def install_engines(
        self, *, router: Any = None, tables: tuple[Any, ...] | None = None
    ) -> None:
        routers = (router,) if router is not None else self.ROUTERS
        tables = tables if tables is not None else self.TABLES
        install_app = self if (routers or tuple(tables)) else None
        if routers:
            for a in routers:
                Engine.install_from_objects(
                    app=install_app, router=a, tables=tuple(tables)
                )
        else:
            Engine.install_from_objects(
                app=install_app, router=None, tables=tuple(tables)
            )

    async def invoke(self, env: GwRawEnvelope) -> None:
        plan, packed_plan = self._get_compiled_plan()
        ctx: dict[str, Any] = {
            "app": self,
            "router": self,
            "raw": env,
            "env": env,
            "kernel_plan": plan,
            "plan": plan,
            "packed_plan": packed_plan,
            "temp": {},
        }
        await self.runtime.invoke(
            env=env,
            ctx=ctx,
            plan=plan,
            packed_plan=packed_plan,
        )

    def _invalidate_runtime_plan(self) -> None:
        self._compiled_plan = None
        try:
            _default_kernel.invalidate_kernelz_payload(self)
        except Exception:
            pass

    def _get_compiled_plan(self) -> tuple[Any, Any | None]:
        compiled = self._compiled_plan
        if compiled is not None:
            return compiled
        compiled = self.runtime.compile(self)
        self._compiled_plan = compiled
        return compiled

    def warm_runtime(self) -> None:
        self._compiled_plan = self.runtime.compile(self)

    async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> None:
        path = scope.get("path")
        if isinstance(path, str):
            seen_paths = getattr(self, "_seen_paths", None)
            if not isinstance(seen_paths, set):
                seen_paths = set()
                setattr(self, "_seen_paths", seen_paths)
            seen_paths.add(path)
        env = GwRawEnvelope(kind="asgi3", scope=scope, receive=receive, send=send)
        await self.invoke(env)

    def _normalize_prefix(self, prefix: str) -> str:
        return _normalize_prefix_impl(prefix)

    def _merge_tags(self, tags: list[str] | None) -> list[str] | None:
        return _merge_tags_impl(getattr(self, "tags", None), tags)

    def include_router(self, router: Any, *, prefix: str | None = None) -> Any:
        routed = getattr(router, "router", router)
        _include_router_impl(self, routed, prefix=prefix or "")
        self._invalidate_runtime_plan()
        return router

    initialize = _ddl_initialize
