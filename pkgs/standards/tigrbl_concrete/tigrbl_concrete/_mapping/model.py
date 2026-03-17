from __future__ import annotations

from dataclasses import replace
import inspect
from functools import wraps
import re
from types import SimpleNamespace
from typing import Any, Optional, Set, Tuple

from pydantic import BaseModel

from tigrbl_concrete._concrete._router import Router
from tigrbl_core._spec import OpSpec
from tigrbl_core._spec.binding_spec import (
    HttpJsonRpcBindingSpec,
    HttpRestBindingSpec,
    resolve_rest_nested_prefix,
)
from tigrbl_core.config.constants import CANON
from tigrbl_core.config.constants import HOOK_DECLS_ATTR
from tigrbl_core._spec.op_utils import _maybe_await, _unwrap
from tigrbl_core.schema.builder import _build_schema
from tigrbl_core.schema.builder import _strip_parent_fields
from tigrbl_core.schema.utils import _make_bulk_rows_model
from tigrbl_base._base._schema_base import SchemaBase
from tigrbl_typing.phases import HOOK_PHASES

from tigrbl_concrete._mapping.op_resolver import resolve as resolve_ops
from tigrbl_base._base._rpc_map import register_and_attach as register_rpc

from .model_helpers import _ensure_model_namespaces, _filter_specs, _index_specs

MappingKey = tuple[str, str]

_BULK_ROW_TARGETS = set()


def _bulk_rows_verb(spec: OpSpec) -> str:
    """Return the canonical verb key used for request/response model naming."""
    return spec.alias


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
    all_specs = _materialize_handlers(model, specs)
    _bind_model_hooks(model, specs)
    _materialize_schemas(model, specs)

    register_rpc(model, specs)

    _materialize_rest_router(model, specs, router=router)

    return all_specs


def _materialize_handlers(model: type, specs: Tuple[OpSpec, ...]) -> Tuple[OpSpec, ...]:
    specs = _normalize_bindings(model, tuple(specs))
    _ensure_model_namespaces(model)
    all_specs, by_key, by_alias = _index_specs(specs)
    model.ops = SimpleNamespace(all=all_specs, by_key=by_key, by_alias=by_alias)
    model.opspecs = model.ops
    _attach_model_rpc_call(model, specs)
    return all_specs


def _resolve_schema_arg(model: type, arg: Any) -> Any:
    if arg is None:
        return None
    if isinstance(arg, str):
        alias, _, kind = arg.partition(".")
        kind = kind or "out"
        ns = getattr(getattr(model, "schemas", SimpleNamespace()), alias, None)
        if ns is None:
            raise KeyError(f"Unknown schema alias '{alias}' on {model.__name__}")
        return getattr(ns, "in_" if kind == "in" else "out", None)
    if inspect.isclass(arg):
        return arg
    alias = getattr(arg, "alias", None)
    kind = getattr(arg, "kind", "out")
    if alias:
        ns = getattr(getattr(model, "schemas", SimpleNamespace()), alias, None)
        if ns is None:
            raise KeyError(f"Unknown schema alias '{alias}' on {model.__name__}")
        return getattr(ns, "in_" if kind == "in" else "out", None)
    if callable(arg):
        return arg(model)
    return arg


def _materialize_schemas(model: type, specs: Tuple[OpSpec, ...]) -> None:
    schemas = getattr(model, "schemas", None)
    if not isinstance(schemas, SimpleNamespace):
        schemas = SimpleNamespace()
        setattr(model, "schemas", schemas)

    declared = SchemaBase.collect(model)
    for alias, kinds in (declared or {}).items():
        alias_ns = getattr(schemas, alias, None)
        if not isinstance(alias_ns, SimpleNamespace):
            alias_ns = SimpleNamespace()
            setattr(schemas, alias, alias_ns)
        if "in" in kinds:
            setattr(alias_ns, "in_", kinds["in"])
        if "out" in kinds:
            setattr(alias_ns, "out", kinds["out"])

    raw_nested = resolve_rest_nested_prefix(model) or ""
    nested_vars = set(re.findall(r"{(\w+)}", raw_nested))

    for spec in specs:
        alias_ns = getattr(schemas, spec.alias, None)
        if not isinstance(alias_ns, SimpleNamespace):
            alias_ns = SimpleNamespace()
            setattr(schemas, spec.alias, alias_ns)

        if not hasattr(alias_ns, "in_"):
            request_model = None
            if spec.target != "custom":
                request_model = _build_schema(
                    model,
                    verb=spec.target,
                    name=f"{model.__name__}{spec.alias.replace('_', ' ').title().replace(' ', '')}Request",
                )
            setattr(alias_ns, "in_", request_model)

        if not hasattr(alias_ns, "out"):
            response_item_model = _build_schema(
                model,
                verb=spec.target,
                name=f"{model.__name__}{spec.alias.replace('_', ' ').title().replace(' ', '')}Response",
            )
            setattr(alias_ns, "out", response_item_model)

        if spec.request_model is not None:
            setattr(alias_ns, "in_", _resolve_schema_arg(model, spec.request_model))
        if spec.response_model is not None:
            setattr(alias_ns, "out", _resolve_schema_arg(model, spec.response_model))

        if nested_vars and not spec.alias.startswith("bulk_"):
            in_model = getattr(alias_ns, "in_", None)
            setattr(
                alias_ns,
                "in_",
                _strip_nested_parent_fields(model, spec.target, in_model, nested_vars),
            )

    for spec in specs:
        if spec.alias == spec.target:
            continue
        alias_ns = getattr(schemas, spec.alias, None)
        target_ns = getattr(schemas, spec.target, None)
        if not isinstance(alias_ns, SimpleNamespace):
            continue
        if (
            isinstance(target_ns, SimpleNamespace)
            and spec.request_model is None
            and getattr(target_ns, "in_", None) is not None
        ):
            setattr(alias_ns, "in_", getattr(target_ns, "in_"))
        if (
            isinstance(target_ns, SimpleNamespace)
            and spec.response_model is None
            and getattr(target_ns, "out", None) is not None
        ):
            setattr(alias_ns, "out", getattr(target_ns, "out"))

        # Keep explicit schema overrides as-is so OpenAPI components preserve
        # developer-provided model names (e.g., ``EchoIn``/``EchoOut``).

        # Bulk routes keep explicit object request/response models produced by
        # ``_build_schema`` so OpenAPI component names remain stable.


def _is_array_schema_model(schema_model: Any) -> bool:
    if not hasattr(schema_model, "model_json_schema"):
        return False
    try:
        schema = schema_model.model_json_schema()
    except Exception:
        return False
    return schema.get("type") == "array"


def _strip_nested_parent_fields(
    model: type,
    verb: str,
    schema_model: Any,
    drop: set[str],
) -> Any:
    if not (
        schema_model
        and inspect.isclass(schema_model)
        and issubclass(schema_model, BaseModel)
    ):
        return schema_model

    if _is_array_schema_model(schema_model):
        root = getattr(schema_model, "model_fields", {}).get("root")
        ann = getattr(root, "annotation", None) if root is not None else None
        origin = getattr(ann, "__origin__", None)
        args = getattr(ann, "__args__", ())
        if origin is list and args:
            inner = args[0]
            if inspect.isclass(inner) and issubclass(inner, BaseModel):
                pruned = _strip_parent_fields(inner, drop=drop)
                return _make_bulk_rows_model(model, verb, pruned)

    return _strip_parent_fields(schema_model, drop=drop)


def _bind_model_hooks(model: type, specs: Tuple[OpSpec, ...]) -> None:
    visible_aliases = {spec.alias for spec in specs}
    spec_by_alias: dict[str, OpSpec] = {}
    for spec in specs:
        spec_by_alias.setdefault(spec.alias, spec)

    if not visible_aliases:
        return

    hooks_root = getattr(model, "hooks", None)
    if hooks_root is None:
        hooks_root = SimpleNamespace()
        model.hooks = hooks_root

    alias_map = _mro_alias_map(model)
    collected = _collect_decorated_hooks(model, visible_aliases, alias_map)
    _merge_hooks_map(
        collected, getattr(model, "__tigrbl_hooks__", {}) or {}, visible_aliases
    )
    _merge_hooks_map(
        collected,
        getattr(model, "__tigrbl_router_hooks__", {}) or {},
        visible_aliases,
    )

    for alias in visible_aliases:
        alias_ns = getattr(hooks_root, alias, None)
        if alias_ns is None:
            alias_ns = SimpleNamespace()
            setattr(hooks_root, alias, alias_ns)
        phase_map = collected.get(alias, {})
        for phase in HOOK_PHASES:
            setattr(alias_ns, phase, list(phase_map.get(phase, ())))

        if not getattr(alias_ns, "HANDLER", ()):
            op_spec = spec_by_alias.get(alias)
            op_handler = (
                getattr(op_spec, "handler", None) if op_spec is not None else None
            )
            label = f"hook:wire:tigrbl:core:crud:ops:{alias}@HANDLER"

            async def _default_handler_step(ctx: Any) -> Any:
                if callable(op_handler):
                    result = op_handler(model, ctx)
                    if inspect.isawaitable(result):
                        return await result
                    return result
                return None

            if op_spec is not None and getattr(op_spec, "target", None):
                _default_handler_step.__qualname__ = str(op_spec.target)

            setattr(_default_handler_step, "__tigrbl_label", label)

            alias_ns.HANDLER = [_default_handler_step]


def _mro_alias_map(model: type) -> dict[str, str]:
    merged: dict[str, str] = {}
    for base in reversed(model.__mro__):
        merged.update(getattr(base, "__tigrbl_aliases__", {}) or {})
    return merged


def _collect_decorated_hooks(
    model: type,
    visible_aliases: set[str],
    alias_map: dict[str, str],
) -> dict[str, dict[str, list[Any]]]:
    out: dict[str, dict[str, list[Any]]] = {}
    for base in reversed(model.__mro__):
        for attr in vars(base).values():
            func = _unwrap(attr)
            decls = getattr(func, HOOK_DECLS_ATTR, None)
            if not decls:
                continue
            for decl in decls:
                phase_name = _phase_name(decl.phase)
                for op in _resolve_hook_ops(decl.ops, visible_aliases, alias_map):
                    out.setdefault(op, {}).setdefault(phase_name, []).append(
                        _wrap_ctx_hook(model, decl.fn, phase_name)
                    )
    return out


def _resolve_hook_ops(
    ops: Any,
    visible_aliases: set[str],
    alias_map: dict[str, str],
) -> tuple[str, ...]:
    if ops == "*":
        return tuple(visible_aliases)
    if isinstance(ops, str):
        values = (ops,)
    else:
        values = tuple(ops or ())
    resolved: list[str] = []
    for value in values:
        alias = value if value in visible_aliases else alias_map.get(value, value)
        if alias in visible_aliases:
            resolved.append(alias)
    return tuple(resolved)


def _wrap_ctx_hook(model: type, fn: Any, phase: str):
    @wraps(fn)
    async def _step(ctx: Any) -> Any:
        if phase in {"POST_COMMIT", "POST_RESPONSE"}:
            seeded = ctx.get("result")
            if seeded is None:
                seeded = ctx.get("obj")
            if seeded is None:
                seeded = ctx.get("objs")
            if seeded is None:
                seeded = {}
            elif hasattr(seeded, "__table__"):
                seeded = {
                    col.name: getattr(seeded, col.name)
                    for col in seeded.__table__.columns
                }
            ctx["result"] = seeded

        if phase == "POST_RESPONSE":
            response = ctx.get("response")
            if response is not None and getattr(response, "result", None) is None:
                response.result = ctx.get("result")
        bound = fn.__get__(model, model)
        if inspect.iscoroutinefunction(bound):
            return await bound(ctx)
        return await _maybe_await(bound(ctx))

    return _step


def _merge_hooks_map(
    target: dict[str, dict[str, list[Any]]],
    source: Any,
    visible_aliases: set[str],
) -> None:
    if not isinstance(source, dict):
        return
    for alias, phase_map in source.items():
        if alias == "*":
            aliases = tuple(visible_aliases)
        else:
            aliases = (str(alias),)
        if not isinstance(phase_map, dict):
            continue
        for resolved_alias in aliases:
            phases = target.setdefault(resolved_alias, {})
            for phase, hooks in phase_map.items():
                phase_name = _phase_name(phase)
                bucket = phases.setdefault(phase_name, [])
                for hook in tuple(hooks or ()):
                    fn = getattr(hook, "fn", hook)
                    if callable(fn):
                        bucket.append(_adapt_hook_callable(fn, phase_name))


def _phase_name(phase: Any) -> str:
    value = getattr(phase, "value", phase)
    return str(value)


def _adapt_hook_callable(fn: Any, phase: str):
    @wraps(fn)
    async def _step(ctx: Any) -> Any:
        sig = inspect.signature(fn)
        positional = [
            p
            for p in sig.parameters.values()
            if p.kind
            in (
                inspect.Parameter.POSITIONAL_ONLY,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
            )
        ]
        if len(positional) <= 1 and not any(
            p.kind == inspect.Parameter.VAR_POSITIONAL for p in sig.parameters.values()
        ):
            return await _maybe_await(fn(ctx))

        io_key = "payload" if phase.startswith("PRE_") else "result"
        if phase.startswith("ON_"):
            io_key = "error"
        return await _maybe_await(
            fn(
                ctx.get(io_key),
                db=ctx.get("db"),
                request=ctx.get("request"),
                ctx=ctx,
            )
        )

    return _step


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
    nested_prefix = (resolve_rest_nested_prefix(model) or "").rstrip("/")
    suffix = (
        spec.path_suffix if spec.path_suffix is not None else _default_path_suffix(spec)
    )
    suffix = (suffix or "").strip()
    if suffix and not suffix.startswith("/"):
        suffix = f"/{suffix}"

    member_target = {"read", "update", "replace", "merge", "delete"}
    if nested_prefix:
        base = nested_prefix
        if not base.endswith(f"/{resource}"):
            base = f"{base}/{resource}"
        if spec.arity == "member" or spec.target in member_target:
            return f"{base}/{{item_id}}{suffix}"
        return f"{base}{suffix}"

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
                *_args: Any, _alias: str = spec.alias, **_kwargs: Any
            ) -> Any:
                handler = getattr(model, _alias, None)
                if not callable(handler):
                    return {
                        "detail": "Route materialized; handler unavailable in concrete binder.",
                    }
                ctx = {
                    "request": _kwargs.get("request"),
                    "path_params": _kwargs,
                    "payload": _kwargs.get("body", {}),
                }
                result = handler(model, ctx)
                if inspect.isawaitable(result):
                    result = await result
                return result

            _placeholder_endpoint.__name__ = f"{model.__name__}_{spec.alias}_route"
            alias_ns = getattr(
                getattr(model, "schemas", SimpleNamespace()),
                spec.alias,
                SimpleNamespace(),
            )
            model_router.add_route(
                path=path,
                endpoint=_placeholder_endpoint,
                methods=list(methods),
                name=f"{model.__name__}.{spec.alias}",
                tigrbl_model=model,
                tigrbl_alias=spec.alias,
                request_model=getattr(alias_ns, "in_", None),
                response_model=getattr(alias_ns, "out", None),
                include_in_schema=True,
                status_code=201 if spec.target == "create" else None,
            )
            existing_routes.add(route_key)


def rebind(
    model: type,
    *,
    router: Any | None = None,
    changed_keys: Optional[Set[MappingKey]] = None,
) -> Tuple[OpSpec, ...]:
    return bind(model, router=router, only_keys=changed_keys)


__all__ = ["bind", "rebind", "_materialize_handlers"]
