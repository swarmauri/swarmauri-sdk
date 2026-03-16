from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Optional, Set, Tuple

from tigrbl_concrete._concrete._router import Router
from tigrbl_core._spec import OpSpec
from tigrbl_core._spec.binding_spec import HttpRestBindingSpec
from tigrbl_core.config.constants import CANON

from tigrbl_concrete._mapping.op_resolver import resolve as resolve_ops

from .model_helpers import _ensure_model_namespaces, _filter_specs, _index_specs

MappingKey = tuple[str, str]

_DEFAULT_METHODS: dict[str, tuple[str, ...]] = {
    "create": ("POST",),
    "read": ("GET",),
    "update": ("PATCH",),
    "replace": ("PUT",),
    "merge": ("PATCH",),
    "delete": ("DELETE",),
    "list": ("GET",),
    "clear": ("DELETE",),
    "bulk_create": ("POST",),
    "bulk_update": ("PATCH",),
    "bulk_replace": ("PUT",),
    "bulk_merge": ("PATCH",),
    "bulk_delete": ("DELETE",),
    "custom": ("POST",),
}


def bind(
    model: type,
    *,
    router: Any | None = None,
    only_keys: Optional[Set[MappingKey]] = None,
) -> Tuple[OpSpec, ...]:
    specs = tuple(_filter_specs(tuple(resolve_ops(model)), only_keys))
    _ensure_model_namespaces(model)
    all_specs, by_key, by_alias = _index_specs(specs)
    model.ops = SimpleNamespace(all=all_specs, by_key=by_key, by_alias=by_alias)
    model.opspecs = model.ops

    _materialize_rest_router(model, specs, router=router)

    return all_specs


def _default_path_suffix(spec: OpSpec) -> str | None:
    if spec.target.startswith("bulk_"):
        return None
    if spec.alias != spec.target and spec.target in CANON:
        return f"/{spec.alias}"
    return None


def _path_for_spec(model: type, spec: OpSpec) -> str:
    resource = getattr(model, "resource_name", None) or getattr(
        model, "__resource__", model.__name__.lower()
    )
    suffix = (
        spec.path_suffix if spec.path_suffix is not None else _default_path_suffix(spec)
    )
    suffix = (suffix or "").strip()
    if suffix and not suffix.startswith("/"):
        suffix = f"/{suffix}"

    member_target = {"read", "update", "replace", "merge", "delete"}
    if spec.arity == "member" or spec.target in member_target:
        return f"/{resource}/{{item_id}}{suffix}"
    return f"/{resource}{suffix}"


def _rest_bindings_for_spec(
    model: type, spec: OpSpec
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    bindings: list[tuple[str, tuple[str, ...]]] = []
    for binding in tuple(getattr(spec, "bindings", ()) or ()):  # pragma: no branch
        if not isinstance(binding, HttpRestBindingSpec):
            continue
        methods = tuple(str(method).upper() for method in binding.methods)
        bindings.append((binding.path, methods))

    if bindings:
        return tuple(bindings)

    methods = tuple(spec.http_methods or _DEFAULT_METHODS.get(spec.target, ("POST",)))
    return (
        (_path_for_spec(model, spec), tuple(str(method).upper() for method in methods)),
    )


def _materialize_rest_router(
    model: type,
    specs: Tuple[OpSpec, ...],
    *,
    router: Any | None,
) -> None:
    model_rest = getattr(model, "rest", None)
    model_router = getattr(model_rest, "router", None)
    if model_router is None:
        model_router = Router(dependencies=getattr(router, "rest_dependencies", None))
        if model_rest is None:
            model.rest = SimpleNamespace(router=model_router)
        else:
            model_rest.router = model_router

    existing_routes = {
        (
            str(getattr(route, "path", "")),
            tuple(
                sorted(
                    str(method).upper()
                    for method in getattr(route, "methods", ()) or ()
                )
            ),
        )
        for route in tuple(getattr(model_router, "routes", ()) or ())
    }

    for spec in specs:
        for path, methods in _rest_bindings_for_spec(model, spec):
            route_key = (path, tuple(sorted(methods)))
            if route_key in existing_routes:
                continue

            async def _placeholder_endpoint(
                *_args: Any, **_kwargs: Any
            ) -> dict[str, str]:
                return {
                    "detail": "Route materialized; handler unavailable in concrete binder.",
                }

            _placeholder_endpoint.__name__ = f"{model.__name__}_{spec.alias}_route"
            model_router.add_route(
                path=path,
                endpoint=_placeholder_endpoint,
                methods=list(methods),
                tigrbl_model=model,
                tigrbl_alias=spec.alias,
                include_in_schema=False,
            )
            existing_routes.add(route_key)


def rebind(
    model: type,
    *,
    router: Any | None = None,
    changed_keys: Optional[Set[MappingKey]] = None,
) -> Tuple[OpSpec, ...]:
    return bind(model, router=router, only_keys=changed_keys)


__all__ = ["bind", "rebind"]
