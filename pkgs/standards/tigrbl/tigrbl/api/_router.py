"""Router primitives backing ``tigrbl.api.Api`` and ``tigrbl.app.App``.

This compatibility router surface is slated for deprecation in favor of the
higher-level ``Api``/``App`` interfaces.
"""

from __future__ import annotations

import inspect
from typing import Any, Callable

from tigrbl.api._routing import (
    add_api_route,
    include_router,
    merge_tags,
    normalize_prefix,
    route,
)
from tigrbl.core.router_runtime import (
    _invoke_dependency,
    _resolve_handler_kwargs,
    _resolve_route_dependencies,
    call_handler,
    dispatch,
    is_metadata_route,
)
from tigrbl.transport.asgi_wsgi import (
    asgi_app as _asgi_app_impl,
    request_from_asgi as _request_from_asgi_impl,
    request_from_wsgi as _request_from_wsgi_impl,
    router_call as _router_call_impl,
    wsgi_app as _wsgi_app_impl,
)
from tigrbl.transport.httpx import ensure_httpx_sync_transport

from ._route import Route
from ..system.docs.openapi import build_openapi, mount_openapi
from ..system.docs.swagger import mount_swagger
from ..transport.request import Request
from ..transport.rest.decorators import (
    delete as rest_delete,
    get as rest_get,
    patch as rest_patch,
    post as rest_post,
    put as rest_put,
)

Handler = Callable[..., Any]


class Router:
    def __init__(
        self,
        *,
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
        self.prefix = normalize_prefix(prefix)
        self.tags = list(tags or [])
        self.dependencies = list(dependencies or [])
        # FastAPI compatibility shims used by test clients and dependency
        # override helpers.
        self.dependency_overrides: dict[Callable[..., Any], Callable[..., Any]] = {}
        self.dependency_overrides_provider = self
        self._event_handlers: dict[str, list[Callable[..., Any]]] = {
            "startup": [],
            "shutdown": [],
        }

        self._routes: list[Route] = []
        self.routes = self._routes

        if include_docs:
            self._install_builtin_routes()

    @property
    def event_handlers(self) -> dict[str, list[Callable[..., Any]]]:
        """Expose registered startup and shutdown callbacks by event name."""
        return self._event_handlers

    @property
    def on_startup(self) -> list[Callable[..., Any]]:
        """Provide direct access to startup callbacks for lifecycle runners."""
        return self._event_handlers["startup"]

    @property
    def on_shutdown(self) -> list[Callable[..., Any]]:
        """Provide direct access to shutdown callbacks for lifecycle runners."""
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

    def _normalize_prefix(self, prefix: str) -> str:
        return normalize_prefix(prefix)

    def add_api_route(self, path: str, endpoint: Handler, **kwargs: Any) -> None:
        return add_api_route(self, path, endpoint, **kwargs)

    def _merge_tags(self, tags: list[str] | None) -> list[str] | None:
        return merge_tags(self.tags, tags)

    def route(
        self, path: str, *, methods: Any, **kwargs: Any
    ) -> Callable[[Handler], Handler]:
        return route(self, path, methods=methods, **kwargs)

    def get(self, path: str, **kwargs: Any) -> Callable[[Handler], Handler]:
        return rest_get(self, path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> Callable[[Handler], Handler]:
        return rest_post(self, path, **kwargs)

    def put(self, path: str, **kwargs: Any) -> Callable[[Handler], Handler]:
        return rest_put(self, path, **kwargs)

    def patch(self, path: str, **kwargs: Any) -> Callable[[Handler], Handler]:
        return rest_patch(self, path, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> Callable[[Handler], Handler]:
        return rest_delete(self, path, **kwargs)

    def include_router(self, other: "Router", **kwargs: Any) -> None:
        return include_router(self, other, **kwargs)

    def __call__(self, *args: Any, **kwargs: Any):
        return _router_call_impl(self, *args, **kwargs)

    def _wsgi_app(
        self, environ: dict[str, Any], start_response: Callable[..., Any]
    ) -> list[bytes]:
        return _wsgi_app_impl(self, environ, start_response)

    async def _asgi_app(
        self, scope: dict[str, Any], receive: Callable, send: Callable
    ) -> None:
        await _asgi_app_impl(self, scope, receive, send)

    def _request_from_wsgi(self, environ: dict[str, Any]) -> Request:
        return _request_from_wsgi_impl(self, environ)

    def _request_from_asgi(self, scope: dict[str, Any], body: bytes) -> Request:
        return _request_from_asgi_impl(self, scope, body)

    def _route_match_priority(self, route: Route) -> tuple[int, int, int]:
        return _route_match_priority(route)

    async def _dispatch(self, req: Request):
        return await dispatch(self, req)

    async def _call_handler(self, route: Route, req: Request):
        return await call_handler(self, route, req)

    async def _resolve_route_dependencies(self, route: Route, req: Request) -> None:
        return await _resolve_route_dependencies(self, route, req)

    def _is_metadata_route(self, route: Route) -> bool:
        return is_metadata_route(self, route)

    async def _resolve_handler_kwargs(
        self, route: Route, req: Request
    ) -> dict[str, Any]:
        return await _resolve_handler_kwargs(self, route, req)

    async def _invoke_dependency(self, dep: Callable[..., Any], req: Request) -> Any:
        return await _invoke_dependency(self, dep, req)

    def openapi(self) -> dict[str, Any]:
        return build_openapi(self)

    def _install_builtin_routes(self) -> None:
        mount_openapi(self, path=self.openapi_url)
        mount_swagger(self, path=self.docs_url)

    def _swagger_ui_html(self, request: Request) -> str:
        docs_route = next(
            (route for route in self._routes if route.name == "__docs__"), None
        )
        if docs_route is None:
            mount_swagger(self, path=self.docs_url)
            docs_route = next(
                (route for route in self._routes if route.name == "__docs__"), None
            )
        if docs_route is None:
            raise RuntimeError("Unable to resolve mounted swagger docs route.")

        response = docs_route.handler(request)
        body = getattr(response, "body", b"")
        if isinstance(body, bytes):
            return body.decode("utf-8")
        return str(body)


def _route_match_priority(route: Route) -> tuple[int, int, int]:
    is_metadata = int(getattr(route, "name", "") in {"__openapi__", "__docs__"})
    dynamic_segments = route.path_template.count("{")
    path_length = -len(route.path_template)
    return (-is_metadata, dynamic_segments, path_length)


ensure_httpx_sync_transport()


APIRouter = Router
