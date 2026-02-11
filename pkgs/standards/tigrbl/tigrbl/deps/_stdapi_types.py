"""Core stdapi primitives used by the router implementation."""

from __future__ import annotations

import inspect
import json
import mimetypes
import re
from dataclasses import dataclass, field
from types import SimpleNamespace
from typing import Annotated, Any, Callable, Mapping, get_args, get_origin


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
            data, ensure_ascii=False, separators=(",", ":"), default=str
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
            content, ensure_ascii=False, separators=(",", ":"), default=str
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
        """Starlette-compatible path attribute."""
        return self.path_template

    @property
    def endpoint(self) -> Handler:
        """Starlette-compatible endpoint attribute."""
        return self.handler

    @property
    def dependant(self) -> Any:
        """FastAPI-style dependency metadata shim for compatibility tests."""

        def _param(name: str) -> SimpleNamespace:
            return SimpleNamespace(name=name)

        path_param_names = set(self.param_names)
        path_params = [_param(name) for name in self.param_names]
        query_params: list[SimpleNamespace] = []
        dependencies: list[SimpleNamespace] = []

        signature = inspect.signature(self.handler)
        for param in signature.parameters.values():
            if param.name in path_param_names:
                continue

            dep_callable = None
            default = param.default
            if isinstance(default, _Dependency):
                dep_callable = default.dependency

            annotation = param.annotation
            if dep_callable is None and get_origin(annotation) is Annotated:
                for meta in get_args(annotation)[1:]:
                    if isinstance(meta, _Dependency):
                        dep_callable = meta.dependency
                        break

            if dep_callable is not None:
                dependencies.append(_param(param.name))
                continue

            if param.kind in {
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                inspect.Parameter.KEYWORD_ONLY,
            }:
                query_params.append(_param(param.name))

        for dep in self.dependencies or []:
            dep_fn = getattr(dep, "dependency", dep)
            dep_name = getattr(dep_fn, "__name__", None) or "dependency"
            dependencies.append(_param(dep_name))

        return SimpleNamespace(
            path_params=path_params,
            query_params=query_params,
            dependencies=dependencies,
        )


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
