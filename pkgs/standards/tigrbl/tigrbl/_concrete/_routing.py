"""Shared route registration helpers for concrete app and router classes."""

from __future__ import annotations

from dataclasses import replace
from types import SimpleNamespace
from typing import Any, Callable, Sequence

from .._spec.binding_spec import HttpRestBindingSpec

from ._route import Route, compile_path

Handler = Callable[..., Any]


def normalize_prefix(prefix: str) -> str:
    value = (prefix or "").strip()
    if not value:
        return ""
    if not value.startswith("/"):
        value = f"/{value}"
    return value.rstrip("/") or ""


def merge_tags(
    base: Sequence[str] | None, extra: Sequence[str] | None
) -> list[str] | None:
    if base is None and extra is None:
        return None
    merged = list(base or ())
    for tag in extra or ():
        if tag not in merged:
            merged.append(tag)
    return merged


def add_route(
    owner: Any,
    path: str,
    endpoint: Handler,
    *,
    methods: Sequence[str],
    **kwargs: Any,
) -> None:
    method_set = frozenset(str(m).upper() for m in methods)
    if not method_set:
        raise ValueError("methods must include at least one HTTP verb")

    base_prefix = normalize_prefix(getattr(owner, "prefix", ""))
    if not path.startswith("/"):
        path = f"/{path}"
    full_path = f"{base_prefix}{path}" if base_prefix else path
    normalized_path = full_path.rstrip("/") or "/"
    pattern, param_names = compile_path(normalized_path)

    route = Route(
        methods=method_set,
        path_template=normalized_path,
        pattern=pattern,
        param_names=param_names,
        handler=endpoint,
        name=kwargs.pop("name", getattr(endpoint, "__name__", "route")),
        summary=kwargs.pop("summary", None),
        description=kwargs.pop("description", None),
        tags=merge_tags(getattr(owner, "tags", None), kwargs.pop("tags", None)),
        deprecated=bool(kwargs.pop("deprecated", False)),
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
    owner.routes.append(route)


def include_router(owner: Any, router: Any, *, prefix: str = "") -> None:
    nested_prefix = normalize_prefix(prefix)
    for route in getattr(router, "routes", ()):
        path = route.path_template
        if nested_prefix:
            path = f"{nested_prefix}{path}" if path != "/" else nested_prefix
        add_route(
            owner,
            path,
            route.handler,
            methods=tuple(route.methods),
            name=route.name,
            summary=route.summary,
            description=route.description,
            tags=route.tags,
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
        _sync_rest_binding(
            model=route.tigrbl_model,
            alias=route.tigrbl_alias,
            path=path,
            methods=tuple(route.methods),
        )


def _sync_rest_binding(
    *,
    model: Any,
    alias: Any,
    path: str,
    methods: Sequence[str],
) -> None:
    if not (isinstance(model, type) and isinstance(alias, str) and methods):
        return

    op_ns = getattr(model, "opspecs", None)
    all_specs = tuple(getattr(op_ns, "all", ()) or ())
    if not all_specs:
        return

    normalized_path = path if path.startswith("/") else f"/{path}"
    binding = HttpRestBindingSpec(
        proto="http.rest",
        methods=tuple(str(method).upper() for method in methods),
        path=normalized_path,
    )

    patched = []
    changed = False
    for spec in all_specs:
        if getattr(spec, "alias", None) != alias:
            patched.append(spec)
            continue
        existing = tuple(getattr(spec, "bindings", ()) or ())
        if binding in existing:
            patched.append(spec)
            continue
        patched.append(replace(spec, bindings=(*existing, binding)))
        changed = True

    if not changed:
        return

    by_alias: dict[str, tuple[Any, ...]] = {}
    by_key: dict[tuple[str, str], Any] = {}
    for spec in patched:
        spec_alias = getattr(spec, "alias", None)
        if isinstance(spec_alias, str):
            by_alias.setdefault(spec_alias, tuple())
            by_alias[spec_alias] = (*by_alias[spec_alias], spec)
        key = (getattr(spec, "alias", None), getattr(spec, "target", None))
        if isinstance(key[0], str) and isinstance(key[1], str):
            by_key[key] = spec

    model.opspecs = model.ops = SimpleNamespace(
        all=tuple(patched),
        by_alias=by_alias,
        by_key=by_key,
    )


def route(
    owner: Any,
    path: str,
    *,
    methods: Sequence[str],
    **kwargs: Any,
) -> Callable[[Handler], Handler]:
    def _decorator(handler: Handler) -> Handler:
        add_route(owner, path, handler, methods=methods, **kwargs)
        return handler

    return _decorator


__all__ = ["add_route", "include_router", "merge_tags", "normalize_prefix", "route"]
