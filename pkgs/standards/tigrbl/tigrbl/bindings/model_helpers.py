# tigrbl/v3/bindings/model_helpers.py
"""Internal helpers for the model bindings."""

from __future__ import annotations
from copy import deepcopy
from dataclasses import dataclass, replace
import logging

from types import SimpleNamespace
from typing import Any, Callable, Dict, List, Optional, Sequence, Set, Tuple

from ..hook.mro_collect import mro_collect_decorated_hooks
from ..op import OpSpec
from ..op import resolve as resolve_ops
from ..op.mro_collect import mro_alias_map_for, mro_collect_decorated_ops
from ..op.types import PHASES

logger = logging.getLogger("uvicorn")
logger.debug("Loaded module v3/bindings/model_helpers")


_Key = Tuple[str, str]  # (alias, target)


@dataclass(frozen=True)
class BindingContext:
    """Single-pass context reused across all sub-bindings."""

    model: type
    router: Any | None
    changed_keys: Set[_Key] | None
    alias_map: Dict[str, str]
    merged_hooks: Dict[str, Dict[str, List[Callable[..., Any]]]]


@dataclass(frozen=True)
class BindingPlan:
    """Resolved specs and indexes consumed by model binding."""

    context: BindingContext
    all_specs: Tuple[OpSpec, ...]
    visible_specs: Tuple[OpSpec, ...]
    by_key: Dict[_Key, OpSpec]
    by_alias: Dict[str, List[OpSpec]]


def _key(sp: OpSpec) -> _Key:
    return (sp.alias, sp.target)


def _dedupe_by_name(funcs: Sequence[Callable[..., Any]]) -> List[Callable[..., Any]]:
    return list({getattr(fn, "__qualname__", str(fn)): fn for fn in funcs}.values())


def _ensure_model_namespaces(model: type) -> None:
    """Create top-level namespaces on the model class if missing."""

    # op indexes & metadata
    if "ops" not in model.__dict__:
        if "opspecs" in model.__dict__:
            model.ops = model.opspecs
        else:
            model.ops = SimpleNamespace(all=(), by_key={}, by_alias={})
    # Backwards compatibility: older code may still expect `model.opspecs`
    model.opspecs = model.ops
    # pydantic schemas: .<alias>.in_ / .<alias>.out
    if "schemas" not in model.__dict__:
        model.schemas = SimpleNamespace()
    # hooks: phase chains & raw hook descriptors if you want to expose them
    if "hooks" not in model.__dict__:
        model.hooks = SimpleNamespace()
    # handlers: .<alias>.raw (core/custom), .<alias>.handler (HANDLER chain entry point)
    if "handlers" not in model.__dict__:
        model.handlers = SimpleNamespace()
    # rpc: callables to be registered/mounted elsewhere as JSON-RPC methods
    if "rpc" not in model.__dict__:
        model.rpc = SimpleNamespace()
    # rest: .router (ASGI Router or compatible) – built in rest binding
    if "rest" not in model.__dict__:
        model.rest = SimpleNamespace(router=None)
    # basic table metadata for convenience (introspective only; NEVER used for HTTP paths)
    if "columns" not in model.__dict__:
        table = getattr(model, "__table__", None)
        cols = tuple(getattr(table, "columns", ()) or ())
        model.columns = tuple(
            getattr(c, "name", None) for c in cols if getattr(c, "name", None)
        )
    if "table_config" not in model.__dict__:
        table = getattr(model, "__table__", None)
        model.table_config = dict(getattr(table, "kwargs", {}) or {})
    # ensure raw hook store exists for decorator merges
    if "__tigrbl_hooks__" not in model.__dict__:
        setattr(model, "__tigrbl_hooks__", {})


def _index_specs(
    specs: Sequence[OpSpec],
) -> Tuple[Tuple[OpSpec, ...], Dict[_Key, OpSpec], Dict[str, List[OpSpec]]]:
    all_specs: Tuple[OpSpec, ...] = tuple(specs)
    by_key: Dict[_Key, OpSpec] = {}
    by_alias: Dict[str, List[OpSpec]] = {}
    for sp in specs:
        k = _key(sp)
        by_key[k] = sp
        by_alias.setdefault(sp.alias, []).append(sp)
    return all_specs, by_key, by_alias


def _drop_old_entries(model: type, *, keys: Set[_Key] | None) -> None:
    """
    Remove per-op artifacts for the provided keys before a targeted rebuild.
    Safe no-ops if keys are None (full rebuild happens cleanly by overwrite).
    """

    if not keys:
        return
    # schemas
    for alias, _target in keys:
        ns = getattr(model.schemas, alias, None)
        if ns:
            for attr in ("in_", "out", "list"):
                try:
                    delattr(ns, attr)
                except Exception:
                    pass
            if not ns.__dict__:
                try:
                    delattr(model.schemas, alias)
                except Exception:
                    pass
    # handlers
    for alias, _target in keys:
        if hasattr(model.handlers, alias):
            try:
                delattr(model.handlers, alias)
            except Exception:
                pass
    # hooks
    for alias, _target in keys:
        if hasattr(model.hooks, alias):
            try:
                delattr(model.hooks, alias)
            except Exception:
                pass
    # rpc
    for alias, _target in keys:
        if hasattr(model.rpc, alias):
            try:
                delattr(model.rpc, alias)
            except Exception:
                pass
    # REST endpoints are refreshed wholesale by rest binding as needed


def _filter_specs(
    specs: Sequence[OpSpec], only_keys: Optional[Set[_Key]]
) -> List[OpSpec]:
    if not only_keys:
        return list(specs)
    ok = only_keys
    return [sp for sp in specs if _key(sp) in ok]


def _plan_hooks(
    model: type, *, visible_aliases: Set[str]
) -> Dict[str, Dict[str, List[Callable[..., Any]]]]:
    base_hooks = deepcopy(getattr(model, "__tigrbl_hooks__", {}) or {})

    for phases in base_hooks.values():
        for phase, fns in list(phases.items()):
            seq = fns if isinstance(fns, list) else list(fns)
            phases[phase] = _dedupe_by_name(seq)

    ctx_hooks = mro_collect_decorated_hooks(model, visible_aliases=visible_aliases)
    for alias, phases in ctx_hooks.items():
        per = base_hooks.setdefault(alias, {})
        for phase, fns in phases.items():
            if phase not in PHASES:
                continue
            existing = per.setdefault(phase, [])
            per[phase] = _dedupe_by_name([*existing, *fns])
    return base_hooks


def build_binding_plan(
    model: type,
    *,
    router: Any | None = None,
    changed_keys: Set[_Key] | None = None,
) -> BindingPlan:
    """Build one universal spec plan consumed by all bind/rebind flows."""
    base_specs = list(resolve_ops(model, auto_bind=False))
    ctx_specs = list(mro_collect_decorated_ops(model))

    base_by_target: Dict[str, OpSpec] = {sp.target: sp for sp in base_specs}
    merged_by_key: Dict[_Key, OpSpec] = {_key(sp): sp for sp in base_specs}

    for sp in ctx_specs:
        if (
            sp.alias != sp.target
            and sp.target != "custom"
            and sp.request_model is None
            and sp.response_model is None
        ):
            base = base_by_target.get(sp.target)
            if base is not None:
                sp = replace(
                    sp,
                    request_model=base.request_model,
                    response_model=base.response_model,
                )

        key = _key(sp)
        base = merged_by_key.get(key)
        if base is not None:
            sp = replace(
                sp,
                http_methods=sp.http_methods or base.http_methods,
                path_suffix=sp.path_suffix or base.path_suffix,
                tags=sp.tags or base.tags,
            )
        merged_by_key[key] = sp

    all_specs = tuple(merged_by_key.values())
    visible_specs = tuple(_filter_specs(all_specs, changed_keys))
    visible_aliases = (
        {sp.alias for sp in visible_specs}
        if visible_specs
        else {sp.alias for sp in all_specs}
    )
    merged_hooks = _plan_hooks(model, visible_aliases=visible_aliases)

    alias_map: Dict[str, str] = {}
    try:
        alias_map = mro_alias_map_for(model)
    except Exception:
        pass

    all_specs_ix, by_key, by_alias = _index_specs(all_specs)
    context = BindingContext(
        model=model,
        router=router,
        changed_keys=changed_keys,
        alias_map=alias_map,
        merged_hooks=merged_hooks,
    )
    return BindingPlan(
        context=context,
        all_specs=all_specs_ix,
        visible_specs=visible_specs,
        by_key=by_key,
        by_alias=by_alias,
    )


__all__ = [
    "_Key",
    "_key",
    "_ensure_model_namespaces",
    "_index_specs",
    "_drop_old_entries",
    "_filter_specs",
    "BindingContext",
    "BindingPlan",
    "build_binding_plan",
]
