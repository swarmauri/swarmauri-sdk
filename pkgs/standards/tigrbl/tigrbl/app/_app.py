# tigrbl/tigrbl/v3/app/_app.py
from __future__ import annotations
import inspect
from typing import Any

from ..router._api import Router
from ..engine.engine_spec import EngineCfg
from ..engine import resolver as _resolver
from ..engine import install_from_objects
from ..ddl import initialize as _ddl_initialize
from ._model_registry import initialize_model_registry
from .app_spec import AppSpec
from ..router._route import Route
from ..runtime.dependencies import (
    execute_dependency_tokens as _execute_dependency_tokens_impl,
    execute_route_dependencies as _execute_route_dependencies_impl,
)
from ..router.resolve import resolve_handler_kwargs as _resolve_handler_kwargs_impl
from ..runtime.status.exceptions import HTTPException
from ..runtime.status.mappings import status
from ..system.docs.openapi.metadata import is_metadata_route as _is_metadata_route_impl
from ..transport import Request, Response
from ..transport.gw import asgi_app as _asgi_app_impl, wsgi_app as _wsgi_app_impl


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

    def __call__(self, *args: Any, **kwargs: Any):
        return self._router_call(*args, **kwargs)

    def _router_call(self, *args: Any, **kwargs: Any):
        del kwargs
        if len(args) == 2 and isinstance(args[0], dict) and callable(args[1]):
            return self._wsgi_app(args[0], args[1])
        if len(args) == 1 and isinstance(args[0], dict):
            scope = args[0]

            async def _asgi2_instance(receive: Any, send: Any) -> None:
                await self._asgi_app(scope, receive, send)

            return _asgi2_instance
        if len(args) == 3 and isinstance(args[0], dict):
            return self._asgi_app(args[0], args[1], args[2])
        raise TypeError("Invalid ASGI/WSGI invocation")

    def _wsgi_app(self, environ: dict[str, Any], start_response: Any) -> list[bytes]:
        return _wsgi_app_impl(self, environ, start_response)

    async def _asgi_app(self, scope: dict[str, Any], receive: Any, send: Any) -> None:
        await _asgi_app_impl(self, scope, receive, send)

    def _request_from_wsgi(self, environ: dict[str, Any]) -> Request:
        from tigrbl.transport.request import request_from_wsgi

        return request_from_wsgi(self, environ)

    def _request_from_asgi(self, scope: dict[str, Any], body: bytes) -> Request:
        from tigrbl.transport.request import request_from_asgi

        return request_from_asgi(self, scope, body)

    def _route_match_priority(self, route: Route) -> tuple[int, int, int]:
        is_metadata = int(getattr(route, "name", "") in {"__openapi__", "__docs__"})
        dynamic_segments = route.path_template.count("{")
        path_length = -len(route.path_template)
        return (-is_metadata, dynamic_segments, path_length)

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
        path_matches = [r for r in self._routes if r.pattern.match(req.path)]
        if req.method.upper() == "OPTIONS" and path_matches:
            allowed_methods = {
                method.upper()
                for route in path_matches
                for method in getattr(route, "methods", ())
            }
            allowed_methods.add("OPTIONS")
            return Response(
                status_code=204,
                headers={"allow": ",".join(sorted(allowed_methods))},
                body=b"",
            )

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
            {"detail": "Not Found"}, status_code=status.HTTP_404_NOT_FOUND
        )

    async def call_handler(self, route: Route, req: Request) -> Response:
        dependency_cleanups: list[Any] = []
        setattr(req.state, "_dependency_cleanups", dependency_cleanups)
        try:
            await _execute_route_dependencies_impl(self, route, req)
            kwargs = await self._resolve_handler_kwargs(route, req)
            kwargs = await _execute_dependency_tokens_impl(self, kwargs, req)
            out = route.handler(**kwargs)
            if inspect.isawaitable(out):
                out = await out
        except HTTPException as he:
            return Response.json(
                {"detail": he.detail}, status_code=he.status_code, headers=he.headers
            )
        finally:
            for cleanup in reversed(dependency_cleanups):
                result = cleanup()
                if inspect.isawaitable(result):
                    await result

        if isinstance(out, Response):
            return out
        code = route.status_code if route.status_code is not None else 200
        return Response.json(out, status_code=code)

    async def _dispatch(self, req: Any):
        return await self.dispatch(req)

    async def _call_handler(self, route: Any, req: Any):
        return await self.call_handler(route, req)

    def _is_metadata_route(self, route: Route) -> bool:
        return _is_metadata_route_impl(self, route)

    async def _resolve_handler_kwargs(
        self, route: Route, req: Request
    ) -> dict[str, Any]:
        return await _resolve_handler_kwargs_impl(self, route, req)

    initialize = _ddl_initialize


for _router_method_name in (
    "_merge_tags",
    "_normalize_prefix",
    "add_api_route",
    "add_route",
    "delete",
    "get",
    "patch",
    "post",
    "put",
    "route",
):
    setattr(App, _router_method_name, getattr(Router, _router_method_name))
