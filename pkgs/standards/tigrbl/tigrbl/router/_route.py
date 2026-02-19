"""API route datatypes and path compilation helpers."""

from __future__ import annotations

import inspect
import re
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Annotated, Any, Callable, get_args, get_origin

from ..security.dependencies import Dependency

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
    security_dependencies: list[Any] | None = None
    tigrbl_model: Any | None = None
    tigrbl_alias: str | None = None

    @property
    def path(self) -> str:
        if self.path_template == "/":
            return "/"
        return self.path_template.rstrip("/")

    @property
    def endpoint(self) -> Handler:
        return self.handler

    @property
    def dependant(self) -> Any:
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
            if isinstance(default, Dependency):
                dep_callable = default.dependency

            annotation = param.annotation
            if dep_callable is None and get_origin(annotation) is Annotated:
                for meta in get_args(annotation)[1:]:
                    if isinstance(meta, Dependency):
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


def compile_path(path_template: str) -> tuple[re.Pattern[str], tuple[str, ...]]:
    if not path_template.startswith("/"):
        path_template = "/" + path_template

    # Accept both slashless and trailing-slash variants for non-root routes.
    # This keeps route matching stable for clients that call `/resource` while
    # routers expose `/resource/` (or vice-versa).
    normalized_path = path_template.rstrip("/") or "/"

    param_names: list[str] = []

    def repl(match: re.Match[str]) -> str:
        name = match.group(1)
        param_names.append(name)
        return rf"(?P<{name}>[^/]+)"

    pattern_src = re.sub(r"\{([A-Za-z_][A-Za-z0-9_]*)\}", repl, normalized_path)
    if normalized_path != "/":
        pattern_src += "/?"
    pattern = re.compile("^" + pattern_src + "$")
    return pattern, tuple(param_names)
