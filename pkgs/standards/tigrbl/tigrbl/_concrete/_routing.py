from __future__ import annotations

from typing import Any, Callable

from ._route import Route, compile_path


def normalize_prefix(prefix: str) -> str:
    p = (prefix or "").strip()
    if not p:
        return ""
    if not p.startswith("/"):
        p = "/" + p
    if p != "/":
        p = p.rstrip("/")
    return p


def merge_tags(base_tags: list[str], route_tags: list[str] | None) -> list[str] | None:
    if route_tags is None:
        return list(base_tags) if base_tags else None
    merged = list(base_tags or [])
    for tag in route_tags:
        if tag not in merged:
            merged.append(tag)
    return merged


def add_route(
    router: Any,
    path: str,
    endpoint: Any,
    *,
    methods: list[str] | tuple[str, ...],
    **kwargs: Any,
) -> None:
    full_path = f"{normalize_prefix(getattr(router, 'prefix', ''))}{path or ''}" or "/"
    pattern, param_names = compile_path(full_path)
    route = Route(
        methods=frozenset(methods),
        path_template=full_path,
        pattern=pattern,
        param_names=param_names,
        handler=endpoint,
        name=kwargs.get("name") or getattr(endpoint, "__name__", "<lambda>"),
        summary=kwargs.get("summary"),
        description=kwargs.get("description"),
        tags=kwargs.get("tags"),
        deprecated=bool(kwargs.get("deprecated", False)),
        request_schema=kwargs.get("request_schema"),
        response_schema=kwargs.get("response_schema"),
        path_param_schemas=kwargs.get("path_param_schemas"),
        query_param_schemas=kwargs.get("query_param_schemas"),
        include_in_schema=kwargs.get("include_in_schema", True),
        operation_id=kwargs.get("operation_id"),
        response_model=kwargs.get("response_model"),
        request_model=kwargs.get("request_model"),
        responses=kwargs.get("responses"),
        status_code=kwargs.get("status_code"),
        dependencies=kwargs.get("dependencies"),
        security_dependencies=kwargs.get("security_dependencies"),
        tigrbl_model=kwargs.get("tigrbl_model"),
        tigrbl_alias=kwargs.get("tigrbl_alias"),
    )
    routes = getattr(router, "_routes", None)
    if routes is None:
        routes = []
        setattr(router, "_routes", routes)
        setattr(router, "routes", routes)
    routes.append(route)


def include_router(router: Any, child: Any, *, prefix: str = "") -> None:
    mount_prefix = normalize_prefix(prefix)
    children = getattr(router, "_child_routers", None)
    if children is None:
        children = []
        setattr(router, "_child_routers", children)
    children.append((mount_prefix, child))

    for r in getattr(child, "routes", []) or []:
        add_route(
            router,
            f"{mount_prefix}{getattr(r, 'path', '')}",
            getattr(r, "endpoint", None),
            methods=list(getattr(r, "methods", ()) or ("GET",)),
            name=getattr(r, "name", None),
            include_in_schema=getattr(r, "include_in_schema", True),
            response_model=getattr(r, "response_model", None),
            request_model=getattr(r, "request_model", None),
            status_code=getattr(r, "status_code", None),
            summary=getattr(r, "summary", None),
            description=getattr(r, "description", None),
            tags=getattr(r, "tags", None),
            operation_id=getattr(r, "operation_id", None),
            deprecated=getattr(r, "deprecated", False),
            request_schema=getattr(r, "request_schema", None),
            response_schema=getattr(r, "response_schema", None),
            path_param_schemas=getattr(r, "path_param_schemas", None),
            query_param_schemas=getattr(r, "query_param_schemas", None),
            dependencies=getattr(r, "dependencies", None),
            security_dependencies=getattr(r, "security_dependencies", None),
            responses=getattr(r, "responses", None),
            tigrbl_model=getattr(r, "tigrbl_model", None),
            tigrbl_alias=getattr(r, "tigrbl_alias", None),
        )


def route(
    router: Any, path: str, *, methods: Any, **kwargs: Any
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    methods_list = list(methods or ["GET"])

    def _decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        add_route(router, path, fn, methods=methods_list, **kwargs)
        return fn

    return _decorator


__all__ = ["add_route", "include_router", "merge_tags", "normalize_prefix", "route"]
