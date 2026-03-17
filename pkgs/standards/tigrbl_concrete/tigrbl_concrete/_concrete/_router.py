"""Router primitives backing ``tigrbl.Router`` and ``tigrbl.App``."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any, Callable
from types import SimpleNamespace

from tigrbl_base._base import RouterBase
from tigrbl_concrete._concrete import engine_resolver as _resolver
from tigrbl_core._spec.app_spec import _seqify
from tigrbl_core._spec.engine_spec import EngineCfg
from ._table_registry import TableRegistry

from ._routing import (
    add_route as _add_route_impl,
    include_router as _include_router_impl,
    merge_tags,
    normalize_prefix,
    route,
)
from ._httpx import ensure_httpx_sync_transport

from ._route import Route
from tigrbl_concrete.system.docs.openapi.metadata import (
    is_metadata_route as _is_metadata_route_impl,
)

Handler = Callable[..., Any]


def _rest_get(router: Any, path: str, **kwargs: Any):
    return router.route(path, methods=["GET"], **kwargs)


def _rest_post(router: Any, path: str, **kwargs: Any):
    return router.route(path, methods=["POST"], **kwargs)


def _rest_put(router: Any, path: str, **kwargs: Any):
    return router.route(path, methods=["PUT"], **kwargs)


def _rest_patch(router: Any, path: str, **kwargs: Any):
    return router.route(path, methods=["PATCH"], **kwargs)


def _rest_delete(router: Any, path: str, **kwargs: Any):
    return router.route(path, methods=["DELETE"], **kwargs)


@asynccontextmanager
async def _default_lifespan_context(app: Any):
    yield


class Router(RouterBase):
    """API router with transport, dependency, and model/table registry support."""

    TABLES: tuple[Any, ...] = ()
    REST_PREFIX = "/router"
    RPC_PREFIX = "/rpc"
    SYSTEM_PREFIX = "/system"

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

    def __init__(
        self,
        *,
        engine: EngineCfg | None = None,
        get_db: Callable[..., Any] | None = None,
        title: str = "API",
        version: str = "0.1.0",
        description: str | None = None,
        openapi_url: str = "/openapi.json",
        docs_url: str = "/docs",
        debug: bool = False,
        swagger_ui_version: str = "5.31.0",
        prefix: str = "",
        tags: list[str] | None = None,
        dependencies: list[Any] | None = None,
        include_docs: bool = False,
    ) -> None:
        self.title = title
        self.version = version
        self.description = description
        self.openapi_url = openapi_url
        self.docs_url = docs_url
        self.debug = debug
        self.swagger_ui_version = swagger_ui_version
        class_prefix = getattr(self, "PREFIX", "")
        self.prefix = normalize_prefix(prefix or class_prefix)
        self.tags = list(_seqify(tags))
        self.dependencies = list(_seqify(dependencies))
        # Allow dependencies to be replaced at runtime, typically for testing
        # and environment-specific wiring.
        self.dependency_overrides: dict[Callable[..., Any], Callable[..., Any]] = {}
        self.dependency_overrides_provider = self
        self.lifespan_context = _default_lifespan_context
        if get_db is not None:
            self.get_db = get_db

        self._routes: list[Route] = []
        self.routes = self._routes

        self.name = getattr(self, "NAME", "router")
        self.prefix = normalize_prefix(prefix or getattr(self, "PREFIX", ""))
        self.engine = engine if engine is not None else getattr(self, "ENGINE", None)
        self.tags = list(
            _seqify(tags if tags is not None else getattr(self, "TAGS", ()))
        )
        self.ops = _seqify(getattr(self, "OPS", ()))
        self.schemas = SimpleNamespace()
        self.hooks = SimpleNamespace()
        self.security_deps = _seqify(getattr(self, "SECURITY_DEPS", ()))
        self.deps = _seqify(getattr(self, "DEPS", ()))
        self.response = getattr(self, "RESPONSE", None)
        self.rest_prefix = getattr(self, "REST_PREFIX", "/router")
        self.rpc_prefix = getattr(self, "RPC_PREFIX", "/rpc")
        self.system_prefix = getattr(self, "SYSTEM_PREFIX", "/system")
        self.tables = TableRegistry(
            tables=Router._collect_declared_tables(self.__class__)
        )
        self._table_registry = self.tables
        self._table_regsitry = self.tables

        default_dependencies = list(self.security_deps) + list(self.deps)
        self.dependencies = list(
            _seqify(dependencies if dependencies is not None else default_dependencies)
        )

        _engine_ctx = engine if engine is not None else getattr(self, "ENGINE", None)
        if _engine_ctx is not None:
            _resolver.register_router(self, _engine_ctx)
            _resolver.resolve_provider(router=self)

    def _include_table_impl(
        self,
        table: type,
        *,
        app: Any | None = None,
        prefix: str | None = None,
        mount_router: bool = True,
    ) -> tuple[type, Any]:
        from tigrbl_concrete._mapping.router.include import include_table

        return include_table(
            self,
            table,
            app=app,
            prefix=prefix,
            mount_router=mount_router,
        )

    def _include_tables_impl(
        self,
        tables: tuple[type, ...] | list[type],
        *,
        app: Any | None = None,
        base_prefix: str | None = None,
        mount_router: bool = True,
    ) -> dict[str, Any]:
        from tigrbl_concrete._mapping.router.include import include_tables

        return include_tables(
            self,
            tables,
            app=app,
            base_prefix=base_prefix,
            mount_router=mount_router,
        )

    def _normalize_prefix(self, prefix: str) -> str:
        return normalize_prefix(prefix)

    def __hash__(self) -> int:
        return id(self)

    def __eq__(self, other: object) -> bool:
        return self is other

    @property
    def router(self) -> "Router":
        return self

    def add_route(
        self,
        path: str,
        endpoint: Any,
        *,
        methods: list[str] | tuple[str, ...],
        **kwargs: Any,
    ) -> None:
        _add_route_impl(self, path, endpoint, methods=methods, **kwargs)

    def _merge_tags(self, tags: list[str] | None) -> list[str] | None:
        return merge_tags(self.tags, tags)

    def include_router(self, router: Any, *, prefix: str | None = None) -> Any:
        routed = getattr(router, "router", router)
        _include_router_impl(self, routed, prefix=prefix or "")
        return router

    def route(
        self, path: str, *, methods: Any, **kwargs: Any
    ) -> Callable[[Handler], Handler]:
        return route(self, path, methods=methods, **kwargs)

    def get(self, path: str, **kwargs: Any) -> Callable[[Handler], Handler]:
        return _rest_get(self, path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> Callable[[Handler], Handler]:
        return _rest_post(self, path, **kwargs)

    def put(self, path: str, **kwargs: Any) -> Callable[[Handler], Handler]:
        return _rest_put(self, path, **kwargs)

    def patch(self, path: str, **kwargs: Any) -> Callable[[Handler], Handler]:
        return _rest_patch(self, path, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> Callable[[Handler], Handler]:
        return _rest_delete(self, path, **kwargs)

    def __call__(self, *args: Any, **kwargs: Any):
        del args, kwargs
        raise TypeError(
            "Router is no longer a transport entrypoint; mount it on TigrblApp."
        )

    async def _execute_route_dependencies(self, route: Route, req: Any) -> None:
        del route, req
        raise RuntimeError("Route dependencies are executed by the runtime/app layer.")

    def _is_metadata_route(self, route: Route) -> bool:
        return _is_metadata_route_impl(self, route)

    async def _execute_dependency_tokens(
        self, kwargs: dict[str, Any], req: Any
    ) -> dict[str, Any]:
        del kwargs, req
        raise RuntimeError("Dependency tokens are executed by the runtime/app layer.")

    async def _invoke_dependency(self, dep: Callable[..., Any], req: Any) -> Any:
        del dep, req
        raise RuntimeError("Dependencies are invoked by the runtime/app layer.")


ensure_httpx_sync_transport()


__all__ = ["Router"]
