"""Router primitives backing ``tigrbl.router`` and ``tigrbl.app.App``."""

from __future__ import annotations

import inspect
from contextlib import asynccontextmanager
from typing import Any, Callable
from types import SimpleNamespace

from .router_spec import RouterSpec
from ..app._model_registry import initialize_model_registry
from ..engine import resolver as _resolver
from ..engine.engine_spec import EngineCfg

from tigrbl.router._routing import (
    add_api_route as _add_api_route_impl,
    merge_tags,
    normalize_prefix,
    route,
)
from tigrbl.router.resolve import resolve_handler_kwargs as _resolve_handler_kwargs_impl
from tigrbl.runtime.dependencies import (
    execute_dependency_tokens as _execute_dependency_tokens_impl,
    execute_route_dependencies as _execute_route_dependencies_impl,
    invoke_dependency as _invoke_dependency_impl,
)
from tigrbl.transport import Response
from tigrbl.runtime.status.exceptions import HTTPException
from tigrbl.runtime.status.mappings import status
from tigrbl.transport.httpx import ensure_httpx_sync_transport

from ._route import Route
from ..system.docs.openapi.metadata import is_metadata_route as _is_metadata_route_impl
from ..transport import Request

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

    def add_api_route(self, path: str, endpoint: Handler, **kwargs: Any) -> None:
        self.add_route(path, endpoint, **kwargs)

    def add_route(
        self,
        path: str,
        endpoint: Any,
        *,
        methods: list[str] | tuple[str, ...],
        **kwargs: Any,
    ) -> None:
        _add_api_route_impl(self, path, endpoint, methods=methods, **kwargs)

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
        return self._router_call(*args, **kwargs)

    def _router_call(self, *args: Any, **kwargs: Any):
        """Dispatch entrypoint supporting WSGI and ASGI call conventions.

        The router is designed to be directly mountable on WSGI *or* ASGI
        servers without additional glue code.

        Supported invocation forms
        --------------------------
        WSGI (PEP 3333)
            ``router(environ: dict, start_response: Callable) -> list[bytes]``

        ASGI 3 (single callable)
            ``router(scope: dict, receive: Callable, send: Callable) -> Awaitable[None]``

        ASGI 2 (callable factory)
            ``router(scope: dict) -> Callable[[receive, send], Awaitable[None]]``

        The protocol is inferred from positional arguments.
        """

        del kwargs
        if len(args) == 2 and isinstance(args[0], dict) and callable(args[1]):
            return self._wsgi_app(args[0], args[1])
        if len(args) == 1 and isinstance(args[0], dict):
            scope = args[0]

            async def _asgi2_instance(receive: Callable, send: Callable) -> None:
                await self._asgi_app(scope, receive, send)

            return _asgi2_instance
        if len(args) == 3 and isinstance(args[0], dict):
            return self._asgi_app(args[0], args[1], args[2])
        raise TypeError("Invalid ASGI/WSGI invocation")

    def _request_from_wsgi(self, environ: dict[str, Any]) -> Request:
        from tigrbl.transport.request import (
            request_from_wsgi as _request_from_wsgi_impl,
        )

        return _request_from_wsgi_impl(self, environ)

    def _request_from_asgi(self, scope: dict[str, Any], body: bytes) -> Request:
        from tigrbl.transport.request import (
            request_from_asgi as _request_from_asgi_impl,
        )

        return _request_from_asgi_impl(self, scope, body)

    def _route_match_priority(self, route: Route) -> tuple[int, int, int]:
        return _route_match_priority(route)

    @staticmethod
    def _is_http_response_like(obj: Any) -> bool:
        return (
            hasattr(obj, "status_code")
            and hasattr(obj, "headers")
            and (
                hasattr(obj, "body")
                or hasattr(obj, "body_iterator")
                or hasattr(obj, "render")
                or hasattr(obj, "path")
            )
        )

    async def dispatch(self, req: Request) -> Response:
        """Route an incoming request to the best matching handler."""

        path_matches = [r for r in self._routes if r.pattern.match(req.path)]

        if req.method.upper() == "OPTIONS" and path_matches:
            return _build_options_response(req, path_matches)

        candidates = [r for r in path_matches if req.method in r.methods]
        candidates.sort(key=self._route_match_priority)
        for candidate in candidates:
            match = candidate.pattern.match(req.path)
            if not match:
                continue
            req2 = Request(
                method=req.method,
                path=req.path,
                headers=req.headers,
                query=req.query,
                path_params={k: v for k, v in match.groupdict().items()},
                body=req.body,
                script_name=req.script_name,
                app=self,
                state=req.state,
                scope=req.scope,
            )
            return await self.call_handler(candidate, req2)

        # If the path exists for any method, return a 405 + Allow header.
        if path_matches:
            allowed = {
                method.upper()
                for candidate in path_matches
                for method in getattr(candidate, "methods", ())
            }
            allowed.add("OPTIONS")
            return Response.json(
                {"detail": "Method Not Allowed"},
                status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                headers={"allow": ",".join(sorted(allowed))},
            )

        return Response.json(
            {"detail": "Not Found"},
            status_code=status.HTTP_404_NOT_FOUND,
        )

    async def call_handler(self, route: Route, req: Request) -> Response:
        """Resolve dependencies, invoke the handler, and normalize its output."""

        dependency_cleanups: list[Callable[[], Any]] = []
        setattr(req.state, "_dependency_cleanups", dependency_cleanups)
        try:
            await self._execute_route_dependencies(route, req)
            kwargs = await self._resolve_handler_kwargs(route, req)
            kwargs = await self._execute_dependency_tokens(kwargs, req)
            out = route.handler(**kwargs)
            if inspect.isawaitable(out):
                out = await out
        except HTTPException as he:
            return Response.json(
                {"detail": he.detail},
                status_code=he.status_code,
                headers=he.headers,
            )
        except Exception as exc:
            # Normalize exception objects that provide ``status_code`` + ``detail``
            # into HTTP JSON responses.
            if hasattr(exc, "status_code") and hasattr(exc, "detail"):
                return Response.json(
                    {"detail": getattr(exc, "detail")},
                    status_code=getattr(exc, "status_code"),
                    headers=getattr(exc, "headers", None),
                )
            raise
        finally:
            for cleanup in reversed(dependency_cleanups):
                try:
                    result = cleanup()
                    if inspect.isawaitable(result):
                        await result
                except Exception:
                    pass

        if isinstance(out, Response):
            return out

        if self._is_http_response_like(out):
            body = bytes(getattr(out, "body", b"") or b"")
            if not body and hasattr(out, "body_iterator"):
                chunks: list[bytes] = []
                body_iter = getattr(out, "body_iterator")
                if body_iter is not None:
                    if hasattr(body_iter, "__aiter__"):
                        async for chunk in body_iter:
                            chunks.append(
                                chunk.encode("utf-8")
                                if isinstance(chunk, str)
                                else bytes(chunk)
                            )
                    else:
                        for chunk in body_iter:
                            chunks.append(
                                chunk.encode("utf-8")
                                if isinstance(chunk, str)
                                else bytes(chunk)
                            )
                    body = b"".join(chunks)
            if not body and hasattr(out, "path"):
                path = getattr(out, "path")
                if isinstance(path, str):
                    with open(path, "rb") as fp:
                        body = fp.read()
            raw_headers = getattr(out, "headers", {})
            if hasattr(raw_headers, "items"):
                headers = list(raw_headers.items())
            else:
                headers = list(raw_headers)
            media_type = getattr(out, "media_type", None)
            if media_type and not any(k.lower() == "content-type" for k, _ in headers):
                headers.append(("content-type", media_type))
            return Response(
                status_code=getattr(out, "status_code", 200),
                headers=headers,
                body=body,
            )

        code = route.status_code if route.status_code is not None else 200
        if out is None:
            if code == 204:
                return Response(
                    status_code=204,
                    headers=[("content-length", "0")],
                    body=b"",
                )
            return Response.json(None, status_code=code)
        if isinstance(out, (str, bytes, bytearray)):
            return Response(
                status_code=code,
                headers=[("content-type", "application/octet-stream")],
                body=bytes(out),
            )
        return Response.json(out, status_code=code)

    async def _dispatch(self, req: Request):
        return await self.dispatch(req)

    async def _call_handler(self, route: Route, req: Request):
        return await self.call_handler(route, req)

    async def _execute_route_dependencies(self, route: Route, req: Request) -> None:
        return await _execute_route_dependencies_impl(self, route, req)

    def _is_metadata_route(self, route: Route) -> bool:
        return _is_metadata_route_impl(self, route)

    async def _resolve_handler_kwargs(
        self, route: Route, req: Request
    ) -> dict[str, Any]:
        return await _resolve_handler_kwargs_impl(self, route, req)

    async def _execute_dependency_tokens(
        self, kwargs: dict[str, Any], req: Request
    ) -> dict[str, Any]:
        return await _execute_dependency_tokens_impl(self, kwargs, req)

    async def _invoke_dependency(self, dep: Callable[..., Any], req: Request) -> Any:
        return await _invoke_dependency_impl(self, dep, req)


def _route_match_priority(route: Route) -> tuple[int, int, int]:
    is_metadata = int(getattr(route, "name", "") in {"__openapi__", "__docs__"})
    dynamic_segments = route.path_template.count("{")
    path_length = -len(route.path_template)
    return (-is_metadata, dynamic_segments, path_length)


def _build_options_response(req: Request, routes: list[Route]) -> Response:
    """Build an automatic OPTIONS response for a matched path."""
    allowed_methods = {
        method.upper() for route in routes for method in getattr(route, "methods", ())
    }
    allowed_methods.add("OPTIONS")
    allow_value = ",".join(sorted(allowed_methods))

    headers: dict[str, str] = {"allow": allow_value}

    origin = req.headers.get("origin")
    if origin:
        headers["access-control-allow-origin"] = origin
        headers["vary"] = "origin"

    request_headers = req.headers.get("access-control-request-headers")
    if request_headers:
        headers["access-control-allow-headers"] = request_headers

    if origin and request_headers:
        headers["vary"] = "origin,access-control-request-headers"

    headers["access-control-allow-methods"] = allow_value

    return Response(status_code=204, headers=headers, body=b"")


ensure_httpx_sync_transport()


__all__ = ["Router"]
