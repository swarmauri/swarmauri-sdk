"""Shared concrete routing helpers.

These helpers replaced the removed ``tigrbl.router`` module.
"""

from __future__ import annotations

from typing import Any, Callable, Sequence

from ._route import Route, compile_path

Handler = Callable[..., Any]


def normalize_prefix(prefix: str | None) -> str:
    if not prefix:
        return ""
    normalized = prefix.strip()
    if not normalized:
        return ""
    if not normalized.startswith("/"):
        normalized = f"/{normalized}"
    return "" if normalized == "/" else normalized.rstrip("/")


def merge_tags(
    router_tags: Sequence[str] | None, route_tags: Sequence[str] | None
) -> list[str] | None:
    if not router_tags and not route_tags:
        return None
    merged: list[str] = []
    for tag in tuple(router_tags or ()) + tuple(route_tags or ()):
        if tag not in merged:
            merged.append(tag)
    return merged


def add_route(
    router: Any,
    path: str,
    endpoint: Handler,
    *,
    methods: Sequence[str],
    **kwargs: Any,
) -> None:
    prefix = normalize_prefix(getattr(router, "prefix", ""))
    raw_path = path if path.startswith("/") else f"/{path}"
    path_template = f"{prefix}{raw_path}" if prefix else raw_path
    pattern, param_names = compile_path(path_template)

    normalized_methods = frozenset(m.upper() for m in methods)
    route = Route(
        methods=normalized_methods,
        path_template=path_template,
        pattern=pattern,
        param_names=param_names,
        handler=endpoint,
        name=kwargs.pop("name", getattr(endpoint, "__name__", "endpoint")),
        summary=kwargs.pop("summary", None),
        description=kwargs.pop("description", None),
        tags=kwargs.pop("tags", None),
        deprecated=kwargs.pop("deprecated", False),
        request_schema=kwargs.pop("request_schema", None),
        response_schema=kwargs.pop("response_schema", None),
        path_param_schemas=kwargs.pop("path_param_schemas", None),
        query_param_schemas=kwargs.pop("query_param_schemas", None),
        include_in_schema=kwargs.pop("include_in_schema", True),
        operation_id=kwargs.pop("operation_id", None),
        response_model=kwargs.pop("response_model", None),
        request_model=kwargs.pop("request_model", None),
        responses=kwargs.pop("responses", None),
        status_code=kwargs.pop("status_code", None),
        dependencies=kwargs.pop("dependencies", None),
        security_dependencies=kwargs.pop("security_dependencies", None),
        tigrbl_model=kwargs.pop("tigrbl_model", None),
        tigrbl_alias=kwargs.pop("tigrbl_alias", None),
    )

    routes = getattr(router, "routes", None)
    if routes is None:
        routes = []
        router.routes = routes
    routes.append(route)


def include_router(parent: Any, child: Any, *, prefix: str = "") -> None:
    mount_prefix = normalize_prefix(prefix)
    child_prefix = normalize_prefix(getattr(child, "prefix", ""))
    combined = normalize_prefix(f"{mount_prefix}{child_prefix}")

    for route in tuple(getattr(child, "routes", ())):
        path_template = route.path_template
        if combined:
            path_template = f"{combined}{path_template}"
        pattern, param_names = compile_path(path_template)
        parent_route = Route(
            methods=route.methods,
            path_template=path_template,
            pattern=pattern,
            param_names=param_names,
            handler=route.handler,
            name=route.name,
            summary=route.summary,
            description=route.description,
            tags=merge_tags(getattr(parent, "tags", None), route.tags),
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
            dependencies=route.dependencies,
            security_dependencies=route.security_dependencies,
            tigrbl_model=route.tigrbl_model,
            tigrbl_alias=route.tigrbl_alias,
        )
        parent.routes.append(parent_route)


def route(
    router: Any, path: str, *, methods: Sequence[str], **kwargs: Any
) -> Callable[[Handler], Handler]:
    def decorator(fn: Handler) -> Handler:
        add_route(router, path, fn, methods=methods, **kwargs)
        return fn

    return decorator
