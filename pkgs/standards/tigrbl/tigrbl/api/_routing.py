"""API route registration helpers."""

from __future__ import annotations

from typing import Any, Iterable

from ._route import Route, compile_path


def normalize_prefix(prefix: str) -> str:
    if not prefix:
        return ""
    if not prefix.startswith("/"):
        prefix = "/" + prefix
    return prefix.rstrip("/")


def merge_tags(base_tags: list[str] | None, tags: list[str] | None) -> list[str] | None:
    merged = list(dict.fromkeys((base_tags or []) + (tags or [])))
    return merged or None


def add_api_route(
    router: Any,
    path: str,
    endpoint: Any,
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
    security_dependencies: list[Any] | None = None,
    **_: Any,
) -> None:
    full_path = router.prefix + (path if path.startswith("/") else "/" + path)
    pattern, param_names = compile_path(full_path)
    route = Route(
        methods=frozenset(m.upper() for m in methods),
        path_template=full_path,
        pattern=pattern,
        param_names=param_names,
        handler=endpoint,
        name=name or getattr(endpoint, "__name__", "handler"),
        summary=summary,
        description=description,
        tags=merge_tags(router.tags, tags),
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
        dependencies=list(router.dependencies or []) + list(dependencies or []),
        security_dependencies=list(security_dependencies or []),
    )
    router._routes.append(route)


def route(router: Any, path: str, *, methods: Iterable[str], **kwargs: Any):
    def deco(fn: Any) -> Any:
        add_api_route(router, path, fn, methods=methods, **kwargs)
        return fn

    return deco


def include_router(
    router: Any,
    other: Any,
    *,
    prefix: str = "",
    tags: list[str] | None = None,
    **_: Any,
) -> None:
    if prefix and not prefix.startswith("/"):
        prefix = "/" + prefix
    prefix = prefix.rstrip("/")
    base_prefix = (router.prefix or "") + prefix

    routes = getattr(other, "_routes", None)
    if routes is None:
        routes = getattr(other, "routes", [])

    for r in routes:
        if r.name in ("__openapi__", "__docs__"):
            continue

        route_path = getattr(r, "path_template", None) or getattr(r, "path", "")
        route_handler = getattr(r, "handler", None) or getattr(r, "endpoint", None)
        if not route_path or route_handler is None:
            continue

        route_methods = getattr(r, "methods", None) or {"GET"}
        route_methods = frozenset(str(method).upper() for method in route_methods)

        new_path = base_prefix + route_path
        pattern, param_names = compile_path(new_path)

        route_tags = getattr(r, "tags", None) or []
        merged_tags = list(dict.fromkeys((tags or []) + route_tags)) or None
        router._routes.append(
            Route(
                methods=route_methods,
                path_template=new_path,
                pattern=pattern,
                param_names=param_names,
                handler=route_handler,
                name=getattr(r, "name", None)
                or getattr(route_handler, "__name__", "handler"),
                summary=getattr(r, "summary", None),
                description=getattr(r, "description", None),
                tags=merged_tags,
                deprecated=bool(getattr(r, "deprecated", False)),
                request_schema=getattr(r, "request_schema", None),
                response_schema=getattr(r, "response_schema", None),
                path_param_schemas=getattr(r, "path_param_schemas", None),
                query_param_schemas=getattr(r, "query_param_schemas", None),
                include_in_schema=getattr(r, "include_in_schema", True),
                operation_id=getattr(r, "operation_id", None),
                response_model=getattr(r, "response_model", None),
                request_model=getattr(r, "request_model", None),
                responses=getattr(r, "responses", None),
                status_code=getattr(r, "status_code", None),
                dependencies=list(router.dependencies or [])
                + list(getattr(r, "dependencies", None) or []),
                security_dependencies=list(
                    getattr(r, "security_dependencies", None) or []
                ),
            )
        )
