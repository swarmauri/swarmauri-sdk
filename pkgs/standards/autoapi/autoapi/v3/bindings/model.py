# autoapi/v3/bindings/model.py
from __future__ import annotations

import logging
from dataclasses import replace
from types import SimpleNamespace
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from ..op import OpSpec, alias_map_for, collect_decorated_ops
from ..op import resolve as resolve_ops
from ..op.types import PHASES  # phase allowlist for hook merges

# Ctx-only decorators integration
from ..hook.collect import collect_decorated_hooks

# Sub-binders (implemented elsewhere)
from . import (
    schemas as _schemas_binding,
)  # build_and_attach(model, specs, only_keys=None) -> None
from . import (
    hooks as _hooks_binding,
)  # normalize_and_attach(model, specs, only_keys=None) -> None
from . import (
    handlers as _handlers_binding,
)  # build_and_attach(model, specs, only_keys=None) -> None
from . import (
    rpc as _rpc_binding,
)  # register_and_attach(model, specs, only_keys=None) -> None
from . import (
    rest as _rest_binding,
)  # build_router_and_attach(model, specs, only_keys=None) -> None
from . import columns as _columns_binding
from .model_helpers import (
    _Key,
    _drop_old_entries,
    _ensure_model_namespaces,
    _filter_specs,
    _index_specs,
    _key,
)
from .model_registry import _ensure_op_ctx_attach_hook, _ensure_registry_listener

logger = logging.getLogger(__name__)


# ───────────────────────────────────────────────────────────────────────────────
# Public API
# ───────────────────────────────────────────────────────────────────────────────


def bind(model: type, *, only_keys: Optional[Set[_Key]] = None) -> Tuple[OpSpec, ...]:
    """
    Build (or refresh) all AutoAPI namespaces on the model class.

    Steps:
      1) Ensure model namespaces exist.
      2) Resolve canonical OpSpecs and merge ctx-only ops (@op_ctx). If both define
         the same (alias,target), the ctx-only op overrides.
      3) Optionally drop old entries for targeted (alias,target) keys.
      4) Merge ctx-only hooks (@hook_ctx) into model.__autoapi_hooks__ (alias-aware),
         filtering to known PHASES.
      5) Rebuild & attach (scoped by only_keys when provided):
         • schemas (in_/out)
         • hooks (phase chains, with START_TX/END_TX or mark_skip_persist defaults)
         • handlers (raw & handler entrypoint for HANDLER)
         • rpc (model.rpc.<alias>)
         • rest (model.rest.router)
      6) Index ops under model.ops.{all, by_key, by_alias}
      7) Install a registry listener (once) so imperative updates rebind automatically.

    Returns:
      tuple of OpSpec (the effective set).
    """
    _ensure_model_namespaces(model)

    # 0) Columns first
    _columns_binding.build_and_attach(model)

    # 1) Resolve canonical specs (source of truth)
    base_specs: List[OpSpec] = list(resolve_ops(model))

    # 2) Add ctx-only ops discovered via decorators (tables + mixins)
    ctx_specs: List[OpSpec] = list(collect_decorated_ops(model))

    # 2a) Inherit canonical schemas for aliased ops lacking explicit schemas
    base_by_target: Dict[str, OpSpec] = {sp.target: sp for sp in base_specs}
    fixed_ctx_specs: List[OpSpec] = []
    for sp in ctx_specs:
        if (
            sp.alias != sp.target
            and sp.target != "custom"
            and sp.request_model is None
            and sp.response_model is None
        ):
            base = base_by_target.get(sp.target)
            if base:
                sp = replace(
                    sp,
                    request_model=base.request_model,
                    response_model=base.response_model,
                )
        fixed_ctx_specs.append(sp)
    ctx_specs = fixed_ctx_specs

    # 2b) De-dupe by (alias,target) with ctx-only overriding canonical/defaults
    merged_by_key: Dict[_Key, OpSpec] = {}
    for sp in base_specs:
        merged_by_key[_key(sp)] = sp
    for sp in ctx_specs:
        merged_by_key[_key(sp)] = sp

    all_merged_specs: List[OpSpec] = list(merged_by_key.values())

    # 3) Targeted rebuild support: drop old entries and restrict working set if requested
    _drop_old_entries(model, keys=only_keys)
    specs: List[OpSpec] = _filter_specs(all_merged_specs, only_keys)

    # 4) Merge ctx-only hooks (alias-aware) BEFORE normalization/attachment
    visible_aliases = (
        {sp.alias for sp in specs} if specs else {sp.alias for sp in all_merged_specs}
    )
    ctx_hooks = collect_decorated_hooks(model, visible_aliases=visible_aliases)
    base_hooks = getattr(model, "__autoapi_hooks__", {}) or {}

    # Coerce any pre-existing phase sequences to mutable lists so we can extend
    # and deduplicate by function name
    for phases in base_hooks.values():
        for phase, fns in list(phases.items()):
            seq = list(fns) if not isinstance(fns, list) else fns
            uniq: dict[str, Callable[..., Any]] = {}
            for fn in seq:
                uniq[getattr(fn, "__qualname__", str(fn))] = fn
            phases[phase] = list(uniq.values())

    for alias, phases in ctx_hooks.items():
        per = base_hooks.setdefault(alias, {})
        for phase, fns in phases.items():
            if phase in PHASES:
                lst = per.setdefault(phase, [])
                seen = {getattr(fn, "__qualname__", str(fn)) for fn in lst}
                for fn in fns:
                    name = getattr(fn, "__qualname__", str(fn))
                    if name not in seen:
                        lst.append(fn)
                        seen.add(name)
                per[phase] = lst

    setattr(model, "__autoapi_hooks__", base_hooks)

    # 5) Attach schemas, hooks, handlers, rpc, router (sub-binders honor only_keys)
    _schemas_binding.build_and_attach(model, specs, only_keys=only_keys)
    _hooks_binding.normalize_and_attach(model, specs, only_keys=only_keys)
    _handlers_binding.build_and_attach(model, specs, only_keys=only_keys)
    _rpc_binding.register_and_attach(model, specs, only_keys=only_keys)
    _rest_binding.build_router_and_attach(model, specs, only_keys=only_keys)

    # 6) Index on the model (always overwrite with fresh views)
    all_specs, by_key, by_alias = _index_specs(all_merged_specs)
    model.ops = SimpleNamespace(all=all_specs, by_key=by_key, by_alias=by_alias)
    # Maintain `.opspecs` alias for backward compatibility
    model.opspecs = model.ops

    # (Optional) expose resolved alias map for diagnostics
    try:
        model.alias_map = alias_map_for(model)
    except Exception:  # defensive
        pass

    # 7) Ensure we have a registry listener to refresh on changes
    _ensure_registry_listener(model)
    _ensure_op_ctx_attach_hook(model)
    setattr(model, "__autoapi_op_ctx_watch__", True)

    logger.debug(
        "autoapi.bindings.model.bind(%s): %d ops bound (visible=%d)",
        model.__name__,
        len(all_specs),
        len(specs),
    )
    return all_specs


def rebind(
    model: type, *, changed_keys: Optional[Set[_Key]] = None
) -> Tuple[OpSpec, ...]:
    """
    Public helper to trigger a rebind for the model. If `changed_keys` is provided,
    we attempt a targeted refresh; otherwise we rebuild everything.
    """
    return bind(model, only_keys=changed_keys)


__all__ = ["bind", "rebind"]
