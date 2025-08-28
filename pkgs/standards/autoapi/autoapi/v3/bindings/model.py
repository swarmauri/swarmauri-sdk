# autoapi/v3/bindings/model.py
from __future__ import annotations

import logging
from types import SimpleNamespace
from typing import Dict, List, Optional, Sequence, Set, Tuple

from ..opspec import OpSpec
from ..opspec import resolve as resolve_opspecs
from ..opspec import get_registry, OpspecRegistry
from ..opspec.types import PHASES  # phase allowlist for hook merges
from ..config.constants import AUTOAPI_REGISTRY_LISTENER_ATTR

# Ctx-only decorators integration
from ..decorators import (
    collect_decorated_ops,
    collect_decorated_hooks,
    alias_map_for,
)

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

logger = logging.getLogger(__name__)

# ───────────────────────────────────────────────────────────────────────────────
# Helpers
# ───────────────────────────────────────────────────────────────────────────────

_Key = Tuple[str, str]  # (alias, target)


def _key(sp: OpSpec) -> _Key:
    return (sp.alias, sp.target)


def _ensure_model_namespaces(model: type) -> None:
    """
    Create top-level namespaces on the model class if missing.
    """
    # opspec indexes & metadata
    if not hasattr(model, "opspecs"):
        model.opspecs = SimpleNamespace(all=(), by_key={}, by_alias={})
    # pydantic schemas: .<alias>.in_ / .<alias>.out
    if not hasattr(model, "schemas"):
        model.schemas = SimpleNamespace()
    # hooks: phase chains & raw hook descriptors if you want to expose them
    if not hasattr(model, "hooks"):
        model.hooks = SimpleNamespace()
    # handlers: .<alias>.raw (core/custom), .<alias>.handler (HANDLER chain entry point)
    if not hasattr(model, "handlers"):
        model.handlers = SimpleNamespace()
    # rpc: callables to be registered/mounted elsewhere as JSON-RPC methods
    if not hasattr(model, "rpc"):
        model.rpc = SimpleNamespace()
    # rest: .router (FastAPI Router or compatible) – built in rest binding
    if not hasattr(model, "rest"):
        model.rest = SimpleNamespace(router=None)
    # basic table metadata for convenience (introspective only; NEVER used for HTTP paths)
    if not hasattr(model, "columns"):
        table = getattr(model, "__table__", None)
        cols = tuple(getattr(table, "columns", ()) or ())
        model.columns = tuple(
            getattr(c, "name", None) for c in cols if getattr(c, "name", None)
        )
    if not hasattr(model, "table_config"):
        table = getattr(model, "__table__", None)
        model.table_config = dict(getattr(table, "kwargs", {}) or {})
    # ensure raw hook store exists for decorator merges
    if not hasattr(model, "__autoapi_hooks__"):
        setattr(model, "__autoapi_hooks__", {})


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
      6) Index opspecs under model.opspecs.{all, by_key, by_alias}
      7) Install a registry listener (once) so imperative updates rebind automatically.

    Returns:
      tuple of OpSpec (the effective set).
    """
    _ensure_model_namespaces(model)

    # 0) Columns first
    _columns_binding.build_and_attach(model)

    # 1) Resolve canonical specs (source of truth)
    base_specs: List[OpSpec] = list(resolve_opspecs(model))

    # 2) Add ctx-only ops discovered via decorators (tables + mixins)
    ctx_specs: List[OpSpec] = list(collect_decorated_ops(model))

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
    for phases in base_hooks.values():
        for phase, fns in list(phases.items()):
            if not isinstance(fns, list):
                phases[phase] = list(fns)

    for alias, phases in ctx_hooks.items():
        per = base_hooks.setdefault(alias, {})
        for phase, fns in phases.items():
            if phase in PHASES:
                lst = per.setdefault(phase, [])
                lst.extend(fns)
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
    model.opspecs = SimpleNamespace(all=all_specs, by_key=by_key, by_alias=by_alias)

    # (Optional) expose resolved alias map for diagnostics
    try:
        model.alias_map = alias_map_for(model)
    except Exception:  # defensive
        pass

    # 7) Ensure we have a registry listener to refresh on changes
    _ensure_registry_listener(model)

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


# ───────────────────────────────────────────────────────────────────────────────
# Registry integration
# ───────────────────────────────────────────────────────────────────────────────


def _ensure_registry_listener(model: type) -> None:
    """
    Subscribe (once) to the per-model OpspecRegistry so future register_ops/add/remove/set
    calls automatically refresh the model namespaces.
    """
    reg: OpspecRegistry = get_registry(model)

    # If we already subscribed, skip
    if getattr(model, AUTOAPI_REGISTRY_LISTENER_ATTR, None):
        return

    def _on_registry_change(registry: OpspecRegistry, changed: Set[_Key]) -> None:
        try:
            rebind(model, changed_keys=changed)  # targeted rebind
        except Exception as e:  # pragma: no cover
            logger.exception(
                "autoapi: rebind failed for %s on ops %s: %s",
                model.__name__,
                changed,
                e,
            )

    reg.subscribe(_on_registry_change)
    # Keep a reference to avoid GC of the closure and to prevent double-subscribe
    setattr(model, AUTOAPI_REGISTRY_LISTENER_ATTR, _on_registry_change)


__all__ = ["bind", "rebind"]
