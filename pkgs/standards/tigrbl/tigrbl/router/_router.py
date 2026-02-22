"""Router primitives backing ``tigrbl.router`` and ``tigrbl.app.App``."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any, Callable
from types import SimpleNamespace

from .router_spec import RouterSpec
from ..app._model_registry import initialize_model_registry
from ..engine import resolver as _resolver
from ..engine.engine_spec import EngineCfg

from tigrbl.router._routing import (
    add_route as _add_route_impl,
    merge_tags,
    normalize_prefix,
    route,
)
from tigrbl.transport.httpx import ensure_httpx_sync_transport

from ._route import Route
from ..system.docs.openapi.metadata import is_metadata_route as _is_metadata_route_impl

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


class Router(RouterSpec):
    """API router with transport, dependency, and model/table registry support."""

    MODELS: tuple[Any, ...] = ()
    TABLES: tuple[Any, ...] = ()
    REST_PREFIX = "/router"
    RPC_PREFIX = "/rpc"
    SYSTEM_PREFIX = "/system"

    def __init__(
        self,
        *,
        engine: EngineCfg | None = None,
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
        self.tags = list(tags or [])
        self.dependencies = list(dependencies or [])
        # Allow dependencies to be replaced at runtime, typically for testing
        # and environment-specific wiring.
        self.dependency_overrides: dict[Callable[..., Any], Callable[..., Any]] = {}
        self.dependency_overrides_provider = self
        self.lifespan_context = _default_lifespan_context

        self._routes: list[Route] = []
        self.routes = self._routes

        self.name = getattr(self, "NAME", "router")
        self.prefix = normalize_prefix(prefix or getattr(self, "PREFIX", ""))
        self.engine = engine if engine is not None else getattr(self, "ENGINE", None)
        self.tags = list(tags or getattr(self, "TAGS", []))
        self.ops = tuple(getattr(self, "OPS", ()))
        self.schemas = SimpleNamespace()
        self.hooks = SimpleNamespace()
        self.security_deps = tuple(getattr(self, "SECURITY_DEPS", ()))
        self.deps = tuple(getattr(self, "DEPS", ()))
        self.response = getattr(self, "RESPONSE", None)
        self.rest_prefix = getattr(self, "REST_PREFIX", "/router")
        self.rpc_prefix = getattr(self, "RPC_PREFIX", "/rpc")
        self.system_prefix = getattr(self, "SYSTEM_PREFIX", "/system")
        self.models = initialize_model_registry(getattr(self, "MODELS", ()))

        default_dependencies = list(self.security_deps) + list(self.deps)
        self.dependencies = list(dependencies or default_dependencies)
        self.tables: dict[str, Any] = {}

        _engine_ctx = engine if engine is not None else getattr(self, "ENGINE", None)
        if _engine_ctx is not None:
            _resolver.register_api(self, _engine_ctx)
            _resolver.resolve_provider(router=self)

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
