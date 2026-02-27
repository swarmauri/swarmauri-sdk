from __future__ import annotations

from typing import Any, Callable

from ._concrete._route import Route, compile_path

Handler = Callable[..., Any]


def normalize_prefix(prefix: str) -> str:
    if not prefix:
        return ""
    cleaned = prefix if prefix.startswith("/") else f"/{prefix}"
    return "" if cleaned == "/" else cleaned.rstrip("/")


def merge_tags(
    base_tags: list[str] | None, route_tags: list[str] | None
) -> list[str] | None:
    if not base_tags and not route_tags:
        return None
    merged: list[str] = []
    for tag in [*(base_tags or []), *(route_tags or [])]:
        if tag not in merged:
            merged.append(tag)
    return merged


def add_route(
    router: Any,
    path: str,
    endpoint: Handler,
    *,
    methods: list[str] | tuple[str, ...],
    **kwargs: Any,
) -> None:
    full_path = _join_paths(getattr(router, "prefix", ""), path)
    pattern, param_names = compile_path(full_path)
    route = Route(
        methods=frozenset(m.upper() for m in methods),
        path_template=full_path,
        pattern=pattern,
        param_names=param_names,
        handler=endpoint,
        name=kwargs.pop("name", getattr(endpoint, "__name__", "handler")),
        summary=kwargs.pop("summary", None),
        description=kwargs.pop("description", None),
        tags=merge_tags(getattr(router, "tags", None), kwargs.pop("tags", None)),
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
    router.routes.append(route)


def include_router(parent: Any, child: Any, *, prefix: str = "") -> None:
    mount_prefix = normalize_prefix(prefix)
    for child_route in getattr(child, "routes", []):
        child_path = child_route.path_template
        merged_path = _join_paths(mount_prefix, child_path)
        pattern, param_names = compile_path(merged_path)
        parent.routes.append(
            Route(
                methods=child_route.methods,
                path_template=merged_path,
                pattern=pattern,
                param_names=param_names,
                handler=child_route.handler,
                name=child_route.name,
                summary=child_route.summary,
                description=child_route.description,
                tags=merge_tags(getattr(parent, "tags", None), child_route.tags),
                deprecated=child_route.deprecated,
                request_schema=child_route.request_schema,
                response_schema=child_route.response_schema,
                path_param_schemas=child_route.path_param_schemas,
                query_param_schemas=child_route.query_param_schemas,
                include_in_schema=child_route.include_in_schema,
                operation_id=child_route.operation_id,
                response_model=child_route.response_model,
                request_model=child_route.request_model,
                responses=child_route.responses,
                status_code=child_route.status_code,
                dependencies=child_route.dependencies,
                security_dependencies=child_route.security_dependencies,
                tigrbl_model=child_route.tigrbl_model,
                tigrbl_alias=child_route.tigrbl_alias,
            )
        )


def route(router: Any, path: str, *, methods: Any, **kwargs: Any):
    def _decorator(fn: Handler) -> Handler:
        add_route(router, path, fn, methods=list(methods), **kwargs)
        return fn

    return _decorator


def _join_paths(prefix: str, path: str) -> str:
    pfx = normalize_prefix(prefix)
    route_path = path if path.startswith("/") else f"/{path}"
    out = f"{pfx}{route_path}" if pfx else route_path
    return out or "/"


__all__ = ["add_route", "include_router", "merge_tags", "normalize_prefix", "route"]
