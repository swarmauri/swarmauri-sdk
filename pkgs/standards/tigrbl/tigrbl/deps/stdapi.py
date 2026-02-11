"""Standard API primitives for Tigrbl.

This module strictly does not use FastAPI.
"""

from __future__ import annotations

import asyncio
import importlib
import importlib.util
import inspect
import json
import mimetypes
import re
import traceback
from dataclasses import dataclass, field
from pathlib import Path as FilePath
from types import SimpleNamespace, UnionType
from typing import (
    Any,
    Callable,
    Iterable,
    Mapping,
    get_args,
    get_origin,
    Annotated,
    Union,
)
from urllib.parse import parse_qs


class HTTPException(Exception):
    def __init__(
        self,
        status_code: int,
        detail: str = "",
        headers: Mapping[str, str] | None = None,
    ) -> None:
        super().__init__(detail)
        self.status_code = int(status_code)
        self.detail = str(detail)
        self.headers = dict(headers or {})


class _Status:
    HTTP_200_OK = 200
    HTTP_201_CREATED = 201
    HTTP_204_NO_CONTENT = 204
    HTTP_400_BAD_REQUEST = 400
    HTTP_401_UNAUTHORIZED = 401
    HTTP_403_FORBIDDEN = 403
    HTTP_404_NOT_FOUND = 404
    HTTP_405_METHOD_NOT_ALLOWED = 405
    HTTP_409_CONFLICT = 409
    HTTP_422_UNPROCESSABLE_ENTITY = 422
    HTTP_429_TOO_MANY_REQUESTS = 429
    HTTP_500_INTERNAL_SERVER_ERROR = 500
    HTTP_501_NOT_IMPLEMENTED = 501
    HTTP_503_SERVICE_UNAVAILABLE = 503
    HTTP_504_GATEWAY_TIMEOUT = 504


status = _Status()


def _json_default(value: Any) -> Any:
    if hasattr(value, "model_dump") and callable(getattr(value, "model_dump")):
        try:
            return value.model_dump()
        except Exception:
            pass

    if isinstance(value, Mapping):
        try:
            return dict(value)
        except Exception:
            pass

    mapping = getattr(value, "_mapping", None)
    if mapping is not None:
        try:
            return dict(mapping)
        except Exception:
            pass

    for attr in ("_asdict", "dict"):
        fn = getattr(value, attr, None)
        if callable(fn):
            try:
                return dict(fn())
            except Exception:
                pass

    table = getattr(value, "__table__", None)
    cols = getattr(table, "columns", None)
    if cols is not None:
        try:
            return {
                getattr(c, "name", str(c)): getattr(value, getattr(c, "name", str(c)))
                for c in cols
            }
        except Exception:
            pass

    try:
        data = vars(value)
    except TypeError:
        return str(value)

    out = {k: v for k, v in data.items() if not str(k).startswith("_")}
    return out if out else str(value)


@dataclass
class Request:
    method: str
    path: str
    headers: dict[str, str]
    query: dict[str, list[str]]
    path_params: dict[str, str]
    body: bytes
    script_name: str = ""
    app: Any | None = None
    state: SimpleNamespace = field(default_factory=SimpleNamespace)
    scope: dict[str, Any] = field(default_factory=dict)

    def json(self) -> Any:
        if not self.body:
            return None
        return json.loads(self.body.decode("utf-8"))

    def query_param(self, name: str, default: str | None = None) -> str | None:
        vals = self.query.get(name)
        if not vals:
            return default
        return vals[0]

    @property
    def query_params(self) -> dict[str, str]:
        return {name: vals[0] for name, vals in self.query.items() if vals}


@dataclass
class Response:
    status_code: int = 200
    headers: list[tuple[str, str]] = field(default_factory=list)
    body: bytes = b""

    @staticmethod
    def _status_text(code: int) -> str:
        return {
            200: "OK",
            201: "Created",
            204: "No Content",
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            405: "Method Not Allowed",
            422: "Unprocessable Entity",
            500: "Internal Server Error",
        }.get(code, "OK")

    def status_line(self) -> str:
        return f"{self.status_code} {self._status_text(self.status_code)}"

    @classmethod
    def json(
        cls,
        data: Any,
        status_code: int = 200,
        headers: Mapping[str, str] | None = None,
    ) -> "Response":
        payload = json.dumps(
            data, ensure_ascii=False, separators=(",", ":"), default=_json_default
        ).encode("utf-8")
        hdrs = [("content-type", "application/json; charset=utf-8")]
        for k, v in (headers or {}).items():
            hdrs.append((k.lower(), v))
        return cls(status_code=status_code, headers=hdrs, body=payload)

    @classmethod
    def html(
        cls,
        html: str,
        status_code: int = 200,
        headers: Mapping[str, str] | None = None,
    ) -> "Response":
        payload = html.encode("utf-8")
        hdrs = [("content-type", "text/html; charset=utf-8")]
        for k, v in (headers or {}).items():
            hdrs.append((k.lower(), v))
        return cls(status_code=status_code, headers=hdrs, body=payload)

    @classmethod
    def text(
        cls,
        text: str,
        status_code: int = 200,
        headers: Mapping[str, str] | None = None,
    ) -> "Response":
        payload = text.encode("utf-8")
        hdrs = [("content-type", "text/plain; charset=utf-8")]
        for k, v in (headers or {}).items():
            hdrs.append((k.lower(), v))
        return cls(status_code=status_code, headers=hdrs, body=payload)


class JSONResponse(Response):
    def __init__(self, content: Any, status_code: int = 200) -> None:
        payload = json.dumps(
            content, ensure_ascii=False, separators=(",", ":"), default=_json_default
        ).encode("utf-8")
        super().__init__(
            status_code=status_code,
            headers=[("content-type", "application/json; charset=utf-8")],
            body=payload,
        )


class HTMLResponse(Response):
    def __init__(self, content: str, status_code: int = 200) -> None:
        super().__init__(
            status_code=status_code,
            headers=[("content-type", "text/html; charset=utf-8")],
            body=content.encode("utf-8"),
        )


class PlainTextResponse(Response):
    def __init__(self, content: str, status_code: int = 200) -> None:
        super().__init__(
            status_code=status_code,
            headers=[("content-type", "text/plain; charset=utf-8")],
            body=content.encode("utf-8"),
        )


class FileResponse(Response):
    def __init__(self, path: str, media_type: str | None = None) -> None:
        with open(path, "rb") as handle:
            payload = handle.read()
        content_type = (
            media_type or mimetypes.guess_type(path)[0] or "application/octet-stream"
        )
        super().__init__(
            status_code=200,
            headers=[("content-type", content_type)],
            body=payload,
        )


class HTTPAuthorizationCredentials:
    def __init__(self, scheme: str, credentials: str) -> None:
        self.scheme = scheme
        self.credentials = credentials


class HTTPBearer:
    def __init__(self, auto_error: bool = True) -> None:
        self.auto_error = auto_error

    def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        header = request.headers.get("authorization")
        if not header:
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden"
                )
            return None
        try:
            scheme, credentials = header.split(" ", 1)
        except ValueError:
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden"
                )
            return None
        return HTTPAuthorizationCredentials(scheme=scheme, credentials=credentials)


class _Dependency:
    def __init__(self, dependency: Callable[..., Any]) -> None:
        self.dependency = dependency


def Depends(fn: Callable[..., Any]) -> _Dependency:
    return _Dependency(fn)


def Security(fn: Callable[..., Any]) -> _Dependency:
    return _Dependency(fn)


@dataclass
class Param:
    default: Any = None
    alias: str | None = None
    required: bool = False
    location: str = "query"


def Body(default: Any = None, **kwargs: Any) -> Param:
    return Param(
        default=default,
        alias=kwargs.get("alias"),
        required=default is ...,
        location="body",
    )


def Query(default: Any = None, **kwargs: Any) -> Param:
    return Param(
        default=default,
        alias=kwargs.get("alias"),
        required=default is ...,
        location="query",
    )


def Path(default: Any = None, **kwargs: Any) -> Param:
    return Param(
        default=default,
        alias=kwargs.get("alias"),
        required=default is ...,
        location="path",
    )


def Header(default: Any = None, **kwargs: Any) -> Param:
    return Param(
        default=default,
        alias=kwargs.get("alias"),
        required=default is ...,
        location="header",
    )


Handler = Callable[..., Any]


@dataclass(frozen=True)
class Route:
    methods: frozenset[str]
    path_template: str
    pattern: re.Pattern[str]
    param_names: tuple[str, ...]
    handler: Handler
    name: str
    summary: str | None = None
    description: str | None = None
    tags: list[str] | None = None
    deprecated: bool = False
    request_schema: dict[str, Any] | None = None
    response_schema: dict[str, Any] | None = None
    path_param_schemas: dict[str, dict[str, Any]] | None = None
    query_param_schemas: dict[str, dict[str, Any]] | None = None
    include_in_schema: bool = True
    operation_id: str | None = None
    response_model: Any | None = None
    request_model: Any | None = None
    responses: dict[int, dict[str, Any]] | None = None
    status_code: int | None = None
    dependencies: list[Any] | None = None

    @property
    def path(self) -> str:
        """FastAPI-compatible route path alias."""
        return self.path_template


def _compile_path(path_template: str) -> tuple[re.Pattern[str], tuple[str, ...]]:
    if not path_template.startswith("/"):
        path_template = "/" + path_template

    param_names: list[str] = []

    def repl(match: re.Match[str]) -> str:
        name = match.group(1)
        param_names.append(name)
        return rf"(?P<{name}>[^/]+)"

    pattern_src = re.sub(r"\{([A-Za-z_][A-Za-z0-9_]*)\}", repl, path_template)
    pattern = re.compile("^" + pattern_src + "$")
    return pattern, tuple(param_names)


def _coerce_foreign_response(value: Any) -> Response | None:
    if isinstance(value, Response):
        return value

    status_code = getattr(value, "status_code", None)
    body = getattr(value, "body", None)
    if not isinstance(status_code, int) or not isinstance(body, (bytes, bytearray)):
        return None

    headers_obj = getattr(value, "headers", None)
    hdrs: list[tuple[str, str]] = []
    if isinstance(headers_obj, Mapping):
        hdrs = [(str(k).lower(), str(v)) for k, v in headers_obj.items()]
    else:
        raw_headers = getattr(value, "raw_headers", None)
        if isinstance(raw_headers, (list, tuple)):
            for item in raw_headers:
                if not isinstance(item, (list, tuple)) or len(item) != 2:
                    continue
                k, v = item
                if isinstance(k, (bytes, bytearray)):
                    k = k.decode("latin-1")
                if isinstance(v, (bytes, bytearray)):
                    v = v.decode("latin-1")
                hdrs.append((str(k).lower(), str(v)))

    return Response(status_code=status_code, headers=hdrs, body=bytes(body))


def _match_route_path(route: Route, path: str) -> re.Match[str] | None:
    match = route.pattern.match(path)
    if match:
        return match

    if path != "/" and path.endswith("/"):
        return route.pattern.match(path.rstrip("/"))

    if path != "/":
        return route.pattern.match(path + "/")

    return None


class APIRouter:
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
        self.prefix = self._normalize_prefix(prefix)
        self.tags = list(tags or [])
        self.dependencies = list(dependencies or [])

        self._routes: list[Route] = []
        self.routes = self._routes

        if include_docs:
            self._install_builtin_routes()

    def _normalize_prefix(self, prefix: str) -> str:
        if not prefix:
            return ""
        if not prefix.startswith("/"):
            prefix = "/" + prefix
        return prefix.rstrip("/")

    def add_api_route(
        self,
        path: str,
        endpoint: Handler,
        *,
        methods: Iterable[str],
        name: str | None = None,
        summary: str | None = None,
        description: str | None = None,
        tags: list[str] | None = None,
        deprecated: bool = False,
        request_schema: dict[str, Any] | None = None,
        response_schema: dict[str, Any] | None = None,
        path_param_schemas: dict[str, dict[str, Any]] | None = None,
        query_param_schemas: dict[str, dict[str, Any]] | None = None,
        include_in_schema: bool = True,
        operation_id: str | None = None,
        response_model: Any | None = None,
        request_model: Any | None = None,
        responses: dict[int, dict[str, Any]] | None = None,
        status_code: int | None = None,
        dependencies: list[Any] | None = None,
        **_: Any,
    ) -> None:
        full_path = self.prefix + (path if path.startswith("/") else "/" + path)
        pattern, param_names = _compile_path(full_path)
        route = Route(
            methods=frozenset(m.upper() for m in methods),
            path_template=full_path,
            pattern=pattern,
            param_names=param_names,
            handler=endpoint,
            name=name or getattr(endpoint, "__name__", "handler"),
            summary=summary,
            description=description,
            tags=self._merge_tags(tags),
            deprecated=deprecated,
            request_schema=request_schema,
            response_schema=response_schema,
            path_param_schemas=path_param_schemas,
            query_param_schemas=query_param_schemas,
            include_in_schema=include_in_schema,
            operation_id=operation_id,
            response_model=response_model,
            request_model=request_model,
            responses=responses,
            status_code=status_code,
            dependencies=list(dependencies or []),
        )
        self._routes.append(route)

    def _merge_tags(self, tags: list[str] | None) -> list[str] | None:
        merged = list(dict.fromkeys((self.tags or []) + (tags or [])))
        return merged or None

    def route(
        self, path: str, *, methods: Iterable[str], **kwargs: Any
    ) -> Callable[[Handler], Handler]:
        def deco(fn: Handler) -> Handler:
            self.add_api_route(path, fn, methods=methods, **kwargs)
            return fn

        return deco

    def get(self, path: str, **kwargs: Any) -> Callable[[Handler], Handler]:
        return self.route(path, methods=["GET"], **kwargs)

    def post(self, path: str, **kwargs: Any) -> Callable[[Handler], Handler]:
        return self.route(path, methods=["POST"], **kwargs)

    def put(self, path: str, **kwargs: Any) -> Callable[[Handler], Handler]:
        return self.route(path, methods=["PUT"], **kwargs)

    def patch(self, path: str, **kwargs: Any) -> Callable[[Handler], Handler]:
        return self.route(path, methods=["PATCH"], **kwargs)

    def delete(self, path: str, **kwargs: Any) -> Callable[[Handler], Handler]:
        return self.route(path, methods=["DELETE"], **kwargs)

    def include_router(
        self,
        other: "APIRouter",
        *,
        prefix: str = "",
        tags: list[str] | None = None,
        **_: Any,
    ) -> None:
        if prefix and not prefix.startswith("/"):
            prefix = "/" + prefix
        prefix = prefix.rstrip("/")

        for route in other._routes:
            if route.name in ("__openapi__", "__docs__"):
                continue
            new_path = prefix + route.path_template
            pattern, param_names = _compile_path(new_path)
            merged_tags = list(dict.fromkeys((tags or []) + (route.tags or []))) or None
            self._routes.append(
                Route(
                    methods=route.methods,
                    path_template=new_path,
                    pattern=pattern,
                    param_names=param_names,
                    handler=route.handler,
                    name=route.name,
                    summary=route.summary,
                    description=route.description,
                    tags=merged_tags,
                    deprecated=route.deprecated,
                    request_schema=route.request_schema,
                    response_schema=route.response_schema,
                    path_param_schemas=route.path_param_schemas,
                    query_param_schemas=route.query_param_schemas,
                    include_in_schema=route.include_in_schema,
                    operation_id=route.operation_id,
                    response_model=route.response_model,
                    request_model=route.request_model,
                    responses=route.responses,
                    status_code=route.status_code,
                    dependencies=list(route.dependencies or []),
                )
            )

    def __call__(self, *args: Any, **kwargs: Any):
        # ASGI2 style: app(scope) -> awaitable(receive, send)
        if len(args) == 1 and isinstance(args[0], dict) and "type" in args[0]:
            scope = args[0]

            async def _instance(receive: Callable, send: Callable) -> None:
                await self._asgi_app(scope, receive, send)

            return _instance

        if len(args) == 2 and isinstance(args[0], dict) and callable(args[1]):
            return self._wsgi_app(args[0], args[1])
        if len(args) == 3 and isinstance(args[0], dict) and "type" in args[0]:
            return self._asgi_app(args[0], args[1], args[2])
        raise TypeError("Invalid ASGI/WSGI invocation")

    def _wsgi_app(
        self, environ: dict[str, Any], start_response: Callable[..., Any]
    ) -> list[bytes]:
        try:
            req = self._request_from_wsgi(environ)
            resp = asyncio.run(self._dispatch(req))
        except Exception as exc:  # pragma: no cover - defensive
            if self.debug:
                tb = traceback.format_exc()
                resp = Response.json(
                    {"detail": str(exc), "traceback": tb}, status_code=500
                )
            else:
                resp = Response.json(
                    {"detail": "Internal Server Error"}, status_code=500
                )

        start_response(resp.status_line(), resp.headers)
        return [resp.body]

    async def _asgi_app(
        self, scope: dict[str, Any], receive: Callable, send: Callable
    ) -> None:
        if scope.get("type") != "http":
            await send(
                {
                    "type": "http.response.start",
                    "status": 500,
                    "headers": [],
                }
            )
            await send({"type": "http.response.body", "body": b""})
            return
        body = b""
        more_body = True
        while more_body:
            message = await receive()
            body += message.get("body", b"")
            more_body = message.get("more_body", False)
        req = self._request_from_asgi(scope, body)
        resp = await self._dispatch(req)
        await send(
            {
                "type": "http.response.start",
                "status": resp.status_code,
                "headers": [
                    (k.encode("latin-1"), v.encode("latin-1")) for k, v in resp.headers
                ],
            }
        )
        await send({"type": "http.response.body", "body": resp.body})

    def _request_from_wsgi(self, environ: dict[str, Any]) -> Request:
        method = (environ.get("REQUEST_METHOD") or "GET").upper()
        path = environ.get("PATH_INFO") or "/"
        script_name = environ.get("SCRIPT_NAME") or ""

        headers: dict[str, str] = {}
        for k, v in environ.items():
            if k.startswith("HTTP_"):
                hk = k[5:].replace("_", "-").lower()
                headers[hk] = str(v)
        if "CONTENT_TYPE" in environ:
            headers["content-type"] = str(environ["CONTENT_TYPE"])

        query = parse_qs(environ.get("QUERY_STRING") or "", keep_blank_values=True)

        try:
            length = int(environ.get("CONTENT_LENGTH") or "0")
        except ValueError:
            length = 0
        body = environ["wsgi.input"].read(length) if length > 0 else b""

        return Request(
            method=method,
            path=path,
            headers=headers,
            query=query,
            path_params={},
            body=body,
            script_name=script_name,
            app=self,
        )

    def _request_from_asgi(self, scope: dict[str, Any], body: bytes) -> Request:
        method = (scope.get("method") or "GET").upper()
        path = scope.get("path") or "/"
        headers: dict[str, str] = {
            k.decode("latin-1").lower(): v.decode("latin-1")
            for k, v in scope.get("headers", [])
        }
        query = parse_qs(
            scope.get("query_string", b"").decode("latin-1"), keep_blank_values=True
        )
        return Request(
            method=method,
            path=path,
            headers=headers,
            query=query,
            path_params={},
            body=body,
            script_name=scope.get("root_path") or "",
            app=self,
            scope=scope,
        )

    async def _dispatch(self, req: Request) -> Response:
        candidates = [r for r in self._routes if req.method in r.methods]
        for route in candidates:
            match = _match_route_path(route, req.path)
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
            return await self._call_handler(route, req2)

        for route in self._routes:
            if _match_route_path(route, req.path):
                allowed = ",".join(sorted(route.methods))
                return Response.json(
                    {"detail": "Method Not Allowed"},
                    status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                    headers={"allow": allowed},
                )

        return Response.json(
            {"detail": "Not Found"}, status_code=status.HTTP_404_NOT_FOUND
        )

    async def _call_handler(self, route: Route, req: Request) -> Response:
        dependency_cleanups: list[Callable[[], Any]] = []
        setattr(req.state, "_dependency_cleanups", dependency_cleanups)
        try:
            kwargs = await self._resolve_handler_kwargs(route, req)
            out = route.handler(**kwargs)
            if inspect.isawaitable(out):
                out = await out
        except HTTPException as he:
            return Response.json(
                {"detail": he.detail},
                status_code=he.status_code,
                headers=he.headers,
            )
        finally:
            for cleanup in reversed(dependency_cleanups):
                try:
                    result = cleanup()
                    if inspect.isawaitable(result):
                        await result
                except Exception:
                    pass

        out_response = _coerce_foreign_response(out)
        if out_response is not None:
            if (
                route.status_code is not None
                and out_response.status_code == status.HTTP_200_OK
            ):
                out_response.status_code = route.status_code
            return out_response

        default_status = route.status_code or status.HTTP_200_OK
        if out is None:
            empty_status = route.status_code or status.HTTP_204_NO_CONTENT
            return Response(status_code=empty_status, headers=[], body=b"")
        if isinstance(out, (dict, list, int, float, bool)):
            return Response.json(out, status_code=default_status)
        if isinstance(out, str):
            return Response.text(out, status_code=default_status)
        if isinstance(out, (bytes, bytearray)):
            return Response(
                status_code=default_status,
                headers=[("content-type", "application/octet-stream")],
                body=bytes(out),
            )

        return Response.json(out, status_code=default_status)

    async def _resolve_handler_kwargs(
        self, route: Route, req: Request
    ) -> dict[str, Any]:
        sig = inspect.signature(route.handler)
        kwargs: dict[str, Any] = {}
        body_cache: Any | None = None

        for name, param in sig.parameters.items():
            base_annotation, extras = _split_annotated(param.annotation)
            dependency_marker = _annotation_marker(extras, _Dependency)
            param_marker = _annotation_marker(extras, Param)
            if param.kind is inspect.Parameter.VAR_KEYWORD:
                kwargs.update(req.path_params)
                continue
            if name in req.path_params:
                kwargs[name] = req.path_params[name]
                continue
            if _is_request_annotation(base_annotation) or name == "request":
                kwargs[name] = req
                continue
            default = param.default
            if isinstance(default, _Dependency) or dependency_marker is not None:
                dep = default.dependency if isinstance(default, _Dependency) else None
                dep = dep or dependency_marker.dependency
                kwargs[name] = await self._invoke_dependency(dep, req)
                continue
            if isinstance(default, Param) or param_marker is not None:
                marker = default if isinstance(default, Param) else param_marker
                value, found = _extract_param_value(marker, req, name, body_cache)
                if found:
                    coerced = _coerce_annotation(value, base_annotation)
                    kwargs[name] = coerced
                    if marker.location == "body":
                        body_cache = coerced
                    continue
                if marker.required:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail=f"Missing required parameter: {marker.alias or name}",
                    )
                kwargs[name] = marker.default
                continue
            if default is inspect._empty:
                if body_cache is None:
                    body_cache = _load_body(req)
                if isinstance(body_cache, dict) and name in body_cache:
                    kwargs[name] = _coerce_annotation(body_cache[name], base_annotation)
                    continue
            if default is not inspect._empty:
                kwargs[name] = default
        return kwargs

    async def _invoke_dependency(self, dep: Callable[..., Any], req: Request) -> Any:
        sig = inspect.signature(dep)
        kwargs: dict[str, Any] = {}
        for name, param in sig.parameters.items():
            base_annotation, extras = _split_annotated(param.annotation)
            param_marker = _annotation_marker(extras, Param)
            if _is_request_annotation(base_annotation) or name == "request":
                kwargs[name] = req
                continue
            if isinstance(param.default, Param) or param_marker is not None:
                marker = (
                    param.default if isinstance(param.default, Param) else param_marker
                )
                value, found = _extract_param_value(marker, req, name, None)
                if found:
                    kwargs[name] = value
                    continue
                if marker.required:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail=f"Missing required parameter: {marker.alias or name}",
                    )
                kwargs[name] = marker.default
                continue
            if name in req.path_params:
                kwargs[name] = req.path_params[name]
                continue
            if name in req.query_params:
                kwargs[name] = req.query_params[name]
                continue
            if param.default is inspect._empty:
                continue
            kwargs[name] = param.default
        out = dep(**kwargs)
        if inspect.isgenerator(out):
            try:
                value = next(out)
            except StopIteration:
                return None

            cleanups = getattr(req.state, "_dependency_cleanups", None)
            if isinstance(cleanups, list):
                cleanups.append(out.close)
            return value

        if inspect.isasyncgen(out):
            try:
                value = await anext(out)
            except StopAsyncIteration:
                return None

            cleanups = getattr(req.state, "_dependency_cleanups", None)
            if isinstance(cleanups, list):
                cleanups.append(out.aclose)
            return value

        if inspect.isawaitable(out):
            out = await out
        return out

    def openapi(self) -> dict[str, Any]:
        paths: dict[str, Any] = {}
        components: dict[str, Any] = {}

        for route in self._routes:
            if not route.include_in_schema:
                continue

            path_item = paths.setdefault(route.path_template, {})
            for method in sorted(route.methods):
                status_code = route.status_code or status.HTTP_200_OK
                responses: dict[str, Any] = {}
                if route.responses:
                    for code, meta in route.responses.items():
                        entry: dict[str, Any] = {
                            "description": meta.get("description", "") or "",
                        }
                        model = meta.get("model")
                        if model is not None:
                            entry["content"] = {
                                "application/json": {
                                    "schema": _schema_from_model(model)
                                }
                            }
                        responses[str(code)] = entry
                if str(status_code) not in responses:
                    entry: dict[str, Any] = {"description": "Successful Response"}
                    schema = route.response_schema
                    if schema is None and route.response_model is not None:
                        schema = _schema_from_model(route.response_model)
                    if schema is not None:
                        entry["content"] = {"application/json": {"schema": schema}}
                    responses[str(status_code)] = entry

                op: dict[str, Any] = {
                    "operationId": route.operation_id or route.name,
                    "responses": responses,
                }
                if route.summary:
                    op["summary"] = route.summary
                if route.description:
                    op["description"] = route.description
                if route.tags:
                    op["tags"] = route.tags
                if route.deprecated:
                    op["deprecated"] = True

                params: list[dict[str, Any]] = []
                for param_name in route.param_names:
                    schema = (route.path_param_schemas or {}).get(param_name) or {
                        "type": "string"
                    }
                    params.append(
                        {
                            "name": param_name,
                            "in": "path",
                            "required": True,
                            "schema": schema,
                        }
                    )

                for qname, qschema in (route.query_param_schemas or {}).items():
                    params.append(
                        {
                            "name": qname,
                            "in": "query",
                            "required": bool(qschema.get("required", False)),
                            "schema": {
                                k: v for k, v in qschema.items() if k != "required"
                            },
                        }
                    )

                if params:
                    op["parameters"] = params

                request_schema = route.request_schema
                if request_schema is None and route.request_model is not None:
                    request_schema = _schema_from_model(route.request_model)
                if request_schema is not None:
                    op["requestBody"] = {
                        "required": True,
                        "content": {"application/json": {"schema": request_schema}},
                    }

                sec = _security_from_dependencies(route.dependencies or [])
                if sec:
                    op["security"] = sec
                    components.setdefault("securitySchemes", {}).update(
                        _security_schemes_from_dependencies(route.dependencies or [])
                    )

                path_item[method.lower()] = op

        doc: dict[str, Any] = {
            "openapi": "3.1.0",
            "info": {"title": self.title, "version": self.version},
            "paths": paths,
        }
        if components:
            doc["components"] = components
        if self.description:
            doc["info"]["description"] = self.description
        return doc

    def _install_builtin_routes(self) -> None:
        def _openapi_handler(request: Request) -> Response:
            return Response.json(self.openapi())

        self.add_api_route(
            self.openapi_url,
            _openapi_handler,
            methods=["GET"],
            name="__openapi__",
            include_in_schema=False,
        )

        def _docs_handler(request: Request) -> Response:
            return Response.html(self._swagger_ui_html(request))

        self.add_api_route(
            self.docs_url,
            _docs_handler,
            methods=["GET"],
            name="__docs__",
            include_in_schema=False,
        )

    def _swagger_ui_html(self, req: Request) -> str:
        base = (req.script_name or "").rstrip("/")
        spec_url = f"{base}{self.openapi_url if self.openapi_url.startswith('/') else '/' + self.openapi_url}"

        version = self.swagger_ui_version
        return f"""<!doctype html>
<html>
  <head>
    <meta charset=\"utf-8\" />
    <title>{self.title} — API Docs</title>
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <link rel=\"stylesheet\" href=\"https://unpkg.com/swagger-ui-dist@{version}/swagger-ui.css\" />
  </head>
  <body>
    <div id=\"swagger-ui\"></div>
    <script src=\"https://unpkg.com/swagger-ui-dist@{version}/swagger-ui-bundle.js\"></script>
    <script src=\"https://unpkg.com/swagger-ui-dist@{version}/swagger-ui-standalone-preset.js\"></script>
    <script>
      window.onload = function () {{
        window.ui = SwaggerUIBundle({{
          url: "{spec_url}",
          dom_id: "#swagger-ui",
          presets: [
            SwaggerUIBundle.presets.apis,
            SwaggerUIStandalonePreset
          ],
          layout: "StandaloneLayout"
        }});
      }};
    </script>
  </body>
</html>
"""


__all__ = [
    "APIRouter",
    "FastAPI",
    "Router",
    "Request",
    "Response",
    "JSONResponse",
    "HTMLResponse",
    "PlainTextResponse",
    "FileResponse",
    "HTTPException",
    "Depends",
    "Security",
    "Path",
    "Query",
    "Body",
    "Header",
    "HTTPBearer",
    "HTTPAuthorizationCredentials",
    "status",
]


Router = APIRouter


class FastAPI(APIRouter):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.setdefault("include_docs", True)
        super().__init__(*args, **kwargs)


FAVICON_PATH = FilePath(__file__).with_name("favicon.svg")


def _ensure_httpx_sync_transport() -> None:
    spec = importlib.util.find_spec("httpx")
    if spec is None:
        return
    httpx = importlib.import_module("httpx")
    if hasattr(httpx.ASGITransport, "__enter__"):
        return

    def __enter__(self) -> Any:
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        return None

    httpx.ASGITransport.__enter__ = __enter__
    httpx.ASGITransport.__exit__ = __exit__


_ensure_httpx_sync_transport()


def _schema_from_model(model: Any) -> dict[str, Any]:
    try:
        import pydantic

        if isinstance(model, type) and issubclass(model, pydantic.BaseModel):
            return model.model_json_schema()  # type: ignore[no-any-return]
    except Exception:
        pass

    origin = getattr(model, "__origin__", None)
    if origin in (list, tuple, set):
        item = model.__args__[0] if getattr(model, "__args__", None) else Any
        return {"type": "array", "items": _schema_from_model(item)}
    return {"type": "object"}


def _split_annotated(annotation: Any) -> tuple[Any, tuple[Any, ...]]:
    if get_origin(annotation) is Annotated:
        args = get_args(annotation)
        if args:
            return args[0], tuple(args[1:])
    return annotation, ()


def _annotation_marker(extras: Iterable[Any], marker_type: type[Any]) -> Any | None:
    for extra in extras:
        if isinstance(extra, marker_type):
            return extra
    return None


def _is_request_annotation(annotation: Any) -> bool:
    if annotation is Request:
        return True
    if isinstance(annotation, str):
        normalized = annotation.strip().strip("\"'")
        return normalized.rsplit(".", maxsplit=1)[-1] == "Request"
    return False


def _load_body(req: Request) -> Any:
    try:
        return req.json()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid JSON: {exc}",
        ) from exc


def _coerce_annotation(value: Any, annotation: Any) -> Any:
    if annotation in (inspect._empty, Any, None):
        return value

    origin = get_origin(annotation)
    args = get_args(annotation)

    if origin in (list, tuple, set) and isinstance(value, list):
        inner = args[0] if args else Any
        coerced = [_coerce_annotation(item, inner) for item in value]
        if origin is tuple:
            return tuple(coerced)
        if origin is set:
            return set(coerced)
        return coerced

    if origin in (UnionType, Union):
        for arg in args:
            if arg is type(None) and value is None:
                return None
            try:
                return _coerce_annotation(value, arg)
            except Exception:
                continue
        return value

    validator = getattr(annotation, "model_validate", None)
    if callable(validator):
        return validator(value)

    if isinstance(annotation, type) and isinstance(value, annotation):
        return value

    return value


def _extract_param_value(
    marker: Param, req: Request, param_name: str, body_cache: Any | None
) -> tuple[Any, bool]:
    alias = marker.alias or param_name
    if marker.location == "query":
        if alias in req.query_params:
            return req.query_params[alias], True
        return None, False
    if marker.location == "header":
        key = alias.lower()
        if key in req.headers:
            return req.headers.get(key), True
        return None, False
    if marker.location == "path":
        if alias in req.path_params:
            return req.path_params[alias], True
        return None, False
    if marker.location == "body":
        value = body_cache if body_cache is not None else _load_body(req)
        if value is None:
            return None, False
        return value, True
    return None, False


def _security_from_dependencies(deps: Iterable[Any]) -> list[dict[str, list[str]]]:
    security: list[dict[str, list[str]]] = []
    for dependency in _extract_security_dependencies(deps):
        if isinstance(dependency, HTTPBearer):
            security.append({"HTTPBearer": []})
    return security


def _security_schemes_from_dependencies(deps: Iterable[Any]) -> dict[str, Any]:
    schemes: dict[str, Any] = {}
    for dependency in _extract_security_dependencies(deps):
        if isinstance(dependency, HTTPBearer):
            schemes["HTTPBearer"] = {"type": "http", "scheme": "bearer"}
    return schemes


def _extract_security_dependencies(deps: Iterable[Any]) -> Iterable[Any]:
    seen: set[int] = set()
    for dep in deps:
        yield from _iter_security_dependencies(dep, seen)


def _iter_security_dependencies(dep: Any, seen: set[int]) -> Iterable[Any]:
    if dep is None:
        return

    dep_id = id(dep)
    if dep_id in seen:
        return
    seen.add(dep_id)

    dependency = getattr(dep, "dependency", None)
    if dependency is not None:
        yield from _iter_security_dependencies(dependency, seen)
        return

    yield dep

    if not callable(dep):
        return

    try:
        signature = inspect.signature(dep)
    except (TypeError, ValueError):
        return

    for param in signature.parameters.values():
        default = param.default
        if default is inspect._empty:
            continue
        yield from _iter_security_dependencies(default, seen)
