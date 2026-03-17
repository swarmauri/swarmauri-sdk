from __future__ import annotations

from dataclasses import replace
from types import SimpleNamespace
from typing import Any, Callable, Optional, Set, Tuple

from pydantic import BaseModel
from tigrbl_concrete._concrete._router import Router
from tigrbl_core._spec import OpSpec
from tigrbl_core._spec.binding_spec import HttpJsonRpcBindingSpec, HttpRestBindingSpec
from tigrbl_core.config.constants import CANON
from tigrbl_core.schema import _build_list_params, _build_schema, namely_model

from tigrbl_concrete._mapping.op_resolver import resolve as resolve_ops
from tigrbl_base._base._rpc_map import register_and_attach as register_rpc

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


def _has_rpc_binding(specs: Tuple[OpSpec, ...]) -> bool:
    for spec in specs:
        for binding in tuple(getattr(spec, "bindings", ()) or ()):
            if isinstance(binding, HttpJsonRpcBindingSpec):
                return True
    return False


def _attach_model_rpc_call(model: type, specs: Tuple[OpSpec, ...]) -> None:
    """Attach ``model.rpc_call(...)`` when the model exposes RPC bindings."""
    if hasattr(model, "rpc_call") and callable(getattr(model, "rpc_call")):
        return
    if not _has_rpc_binding(specs):
        return

    async def _model_rpc_call(
        method: str,
        payload: Any = None,
        *,
        db: Any | None = None,
        request: Any = None,
        ctx: dict[str, Any] | None = None,
    ) -> Any:
        from .router.rpc import rpc_call as _rpc_call

        return await _rpc_call(
            model,
            model,
            method,
            payload,
            db=db,
            request=request,
            ctx=ctx,
        )

    setattr(model, "rpc_call", _model_rpc_call)


def bind(
    model: type,
    *,
    router: Any | None = None,
    only_keys: Optional[Set[MappingKey]] = None,
) -> Tuple[OpSpec, ...]:
    specs = tuple(_filter_specs(tuple(resolve_ops(model)), only_keys))
    specs = _normalize_bindings(model, specs)
    _ensure_model_namespaces(model)

    _build_default_schemas(model, specs)
    _build_default_hooks_and_handlers(model, specs)

    all_specs, by_key, by_alias = _index_specs(specs)
    model.ops = SimpleNamespace(all=all_specs, by_key=by_key, by_alias=by_alias)
    model.opspecs = model.ops

    register_rpc(model, specs)

    _materialize_rest_router(model, specs, router=router)
    _attach_model_rpc_call(model, specs)

    return all_specs


def _ensure_alias_namespace(root: SimpleNamespace, alias: str) -> SimpleNamespace:
    existing = getattr(root, alias, None)
    if isinstance(existing, SimpleNamespace):
        return existing
    namespace = SimpleNamespace()
    setattr(root, alias, namespace)
    return namespace


def _default_schema_for(
    model: type,
    spec: OpSpec,
) -> tuple[type[BaseModel] | None, type[BaseModel] | None]:
    target = str(spec.target or "").lower()
    if target == "create":
        return _build_schema(model, verb="create"), _build_schema(model, verb="read")
    if target == "read":
        return _build_schema(model, verb="read"), _build_schema(model, verb="read")
    if target in {"update", "replace", "merge"}:
        return _build_schema(model, verb=target), _build_schema(model, verb="read")
    if target == "delete":
        return _build_schema(model, verb="delete"), _build_schema(model, verb="read")
    if target == "list":
        return _build_list_params(model), _build_schema(model, verb="read")
    return None, _build_schema(model, verb="read")


def _schema_alias_name(model: type, alias: str, kind: str) -> str:
    token = alias[:1].upper() + alias[1:]
    return f"{model.__name__}{token}{kind}"


def _alias_schema(
    model: type, alias: str, schema: type[BaseModel], kind: str
) -> type[BaseModel]:
    if getattr(schema, "__name__", "") == _schema_alias_name(model, alias, kind):
        return schema
    return namely_model(
        schema,
        name=_schema_alias_name(model, alias, kind),
        doc=f"{alias} {kind.lower()} schema for {model.__name__}",
    )


def _build_default_schemas(model: type, specs: Tuple[OpSpec, ...]) -> None:
    schemas_root = getattr(model, "schemas", SimpleNamespace())
    for spec in specs:
        alias_ns = _ensure_alias_namespace(schemas_root, spec.alias)
        if getattr(alias_ns, "in_", None) is None or getattr(
            getattr(alias_ns, "in_", None), "model_fields", None
        ) in (None, {}):
            req, _ = _default_schema_for(model, spec)
            if req is not None:
                setattr(
                    alias_ns, "in_", _alias_schema(model, spec.alias, req, "Request")
                )
        if getattr(alias_ns, "out", None) is None or getattr(
            getattr(alias_ns, "out", None), "model_fields", None
        ) in (None, {}):
            _, resp = _default_schema_for(model, spec)
            if resp is not None:
                setattr(
                    alias_ns, "out", _alias_schema(model, spec.alias, resp, "Response")
                )


def _handler_atom_step(model: type, target: str) -> Callable[[Any], Any]:
    from tigrbl_atoms.atoms import get as get_atom

    subject_by_target = {
        "create": "handler_create",
        "read": "handler_read",
        "update": "handler_update",
        "replace": "handler_replace",
        "merge": "handler_merge",
        "delete": "handler_delete",
        "list": "handler_list",
        "clear": "handler_clear",
        "bulk_create": "handler_bulk_create",
        "bulk_update": "handler_bulk_update",
        "bulk_replace": "handler_bulk_replace",
        "bulk_merge": "handler_bulk_merge",
        "bulk_delete": "handler_bulk_delete",
    }

    subject = subject_by_target.get(target, "handler_noop")
    _, atom_runner = get_atom("sys", subject)

    async def _step(ctx: Any) -> Any:
        await atom_runner(model, ctx)
        return getattr(ctx, "result", None)

    _step.__name__ = target
    _step.__qualname__ = target
    _step.__module__ = "tigrbl_ops_oltp.crud.ops"
    _step.__tigrbl_label = f"hook:wire:tigrbl:core:crud:ops:{target}@HANDLER"
    return _step


def _build_default_hooks_and_handlers(model: type, specs: Tuple[OpSpec, ...]) -> None:
    hooks_root = getattr(model, "hooks", SimpleNamespace())
    handlers_root = getattr(model, "handlers", SimpleNamespace())

    for spec in specs:
        alias_hooks = _ensure_alias_namespace(hooks_root, spec.alias)
        alias_handlers = _ensure_alias_namespace(handlers_root, spec.alias)

        if getattr(alias_hooks, "HANDLER", None):
            continue

        step = _handler_atom_step(model, str(spec.target or spec.alias))
        setattr(alias_hooks, "HANDLER", [step])
        setattr(alias_handlers, "raw", step)
        setattr(alias_handlers, "handler", step)
        setattr(alias_handlers, "core", step)
        setattr(alias_handlers, "core_raw", step)


def _normalize_bindings(model: type, specs: Tuple[OpSpec, ...]) -> Tuple[OpSpec, ...]:
    normalized: list[OpSpec] = []
    for spec in specs:
        merged = list(tuple(getattr(spec, "bindings", ()) or ()))
        if spec.expose_routes:
            for path, methods in _rest_bindings_for_spec(model, spec):
                binding = HttpRestBindingSpec(
                    proto="http.rest",
                    methods=tuple(str(method).upper() for method in methods),
                    path=path,
                )
                if binding not in merged:
                    merged.append(binding)

        if spec.expose_rpc:
            rpc_binding = HttpJsonRpcBindingSpec(
                proto="http.jsonrpc",
                rpc_method=f"{model.__name__}.{spec.alias}",
            )
            if rpc_binding not in merged:
                merged.append(rpc_binding)

        normalized.append(replace(spec, bindings=tuple(merged)))

    return tuple(normalized)


def _default_path_suffix(spec: OpSpec) -> str | None:
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

    if not spec.expose_routes:
        return ()

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
            (
                getattr(route, "name", "").split(".", 1)[1]
                if "." in str(getattr(route, "name", ""))
                else getattr(route, "name", "")
            ),
        )
        for route in tuple(getattr(model_router, "routes", ()) or ())
    }

    aliases = {spec.alias for spec in specs}
    suppressed_aliases = set()
    if "bulk_create" in aliases:
        suppressed_aliases.add("create")
    if "bulk_delete" in aliases:
        suppressed_aliases.add("clear")

    for spec in specs:
        if spec.alias in suppressed_aliases:
            continue
        for path, methods in _rest_bindings_for_spec(model, spec):
            route_key = (path, tuple(sorted(methods)), spec.alias)
            if route_key in existing_routes:
                continue

            async def _placeholder_endpoint(
                *_args: Any, **_kwargs: Any
            ) -> dict[str, str]:
                return {
                    "detail": "Route materialized; handler unavailable in concrete binder.",
                }

            _placeholder_endpoint.__name__ = f"{model.__name__}_{spec.alias}_route"
            alias_ns = getattr(
                getattr(model, "schemas", SimpleNamespace()), spec.alias, None
            )
            request_model = (
                getattr(alias_ns, "in_", None) if alias_ns is not None else None
            )
            response_model = (
                getattr(alias_ns, "out", None) if alias_ns is not None else None
            )
            model_router.add_route(
                path=path,
                endpoint=_placeholder_endpoint,
                methods=list(methods),
                name=f"{model.__name__}.{spec.alias}",
                tigrbl_model=model,
                tigrbl_alias=spec.alias,
                include_in_schema=True,
                request_model=request_model,
                response_model=response_model,
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
