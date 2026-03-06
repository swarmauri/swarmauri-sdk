from __future__ import annotations

from dataclasses import replace
from types import SimpleNamespace
from typing import Any

from tigrbl_core._spec.binding_spec import HttpJsonRpcBindingSpec, HttpRestBindingSpec

from . import columns as _columns_binding
from . import handlers as _handlers_binding
from . import hooks as _hooks_binding
from . import rest as _rest_binding
from . import rpc as _rpc_binding
from . import schemas as _schemas_binding
from .model_helpers import (
    _drop_old_entries,
    _ensure_model_namespaces,
    _index_specs,
)
from .model_registry import (
    _ensure_op_ctx_attach_hook,
    _ensure_registry_listener,
)
from .context import MappingContext


def _normalize_bindings(model: type, specs: list[Any]) -> tuple[Any, ...]:
    rest_by_alias: dict[str, list[HttpRestBindingSpec]] = {}
    rest_router = getattr(getattr(model, "rest", SimpleNamespace()), "router", None)
    for route in tuple(getattr(rest_router, "routes", ()) or ()):
        alias = getattr(route, "tigrbl_alias", None)
        path = getattr(route, "path_template", None)
        methods = tuple(getattr(route, "methods", ()) or ())
        if not (isinstance(alias, str) and isinstance(path, str) and methods):
            continue
        rest_by_alias.setdefault(alias, []).append(
            HttpRestBindingSpec(
                proto="http.rest",
                methods=tuple(str(method).upper() for method in methods),
                path=path,
            )
        )

    normalized = []
    for spec in specs:
        rest_bindings = tuple(rest_by_alias.get(spec.alias, ()))
        rpc_binding = HttpJsonRpcBindingSpec(
            proto="http.jsonrpc",
            rpc_method=f"{model.__name__}.{spec.alias}",
        )
        existing = tuple(getattr(spec, "bindings", ()) or ())
        merged = [*existing]
        for binding in (*rest_bindings, rpc_binding):
            if binding not in merged:
                merged.append(binding)
        normalized.append(replace(spec, bindings=tuple(merged)))
    return tuple(normalized)


def apply(context: MappingContext):
    model = context.model
    _ensure_model_namespaces(model)
    _columns_binding.build_and_attach(model)
    _drop_old_entries(model, keys=context.only_keys)
    setattr(model, "__tigrbl_hooks__", context.merged_hooks)

    _schemas_binding.build_and_attach(
        model, list(context.visible_specs), only_keys=context.only_keys
    )
    _hooks_binding.normalize_and_attach(
        model, list(context.visible_specs), only_keys=context.only_keys
    )
    _handlers_binding.build_and_attach(
        model, list(context.visible_specs), only_keys=context.only_keys
    )
    _rpc_binding.register_and_attach(
        model, list(context.visible_specs), only_keys=context.only_keys
    )
    _rest_binding.build_router_and_attach(
        model,
        list(context.visible_specs),
        router=context.router,
        only_keys=context.only_keys,
    )

    normalized_specs = _normalize_bindings(model, list(context.all_specs))
    all_specs, by_key, by_alias = _index_specs(list(normalized_specs))
    model.ops = SimpleNamespace(all=all_specs, by_key=by_key, by_alias=by_alias)
    model.opspecs = model.ops
    model.alias_map = dict(context.alias_map)

    _ensure_registry_listener(model)
    _ensure_op_ctx_attach_hook(model)
    setattr(model, "__tigrbl_op_ctx_watch__", True)
    return all_specs


__all__ = ["apply"]
