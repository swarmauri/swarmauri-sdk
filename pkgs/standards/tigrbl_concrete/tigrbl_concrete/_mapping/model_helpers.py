# tigrbl/v3/mapping/model_helpers.py
"""Internal helpers for the model mapping."""

from __future__ import annotations
import logging

from types import SimpleNamespace
from typing import Dict, List, Optional, Sequence, Set, Tuple

from tigrbl_core._spec import OpSpec

logger = logging.getLogger("uvicorn")
logger.debug("Loaded module v3/mapping/model_helpers")


_Key = Tuple[str, str]  # (alias, target)


class _OpSpecGroup(tuple[OpSpec, ...]):
    """Tuple container that preserves legacy single-op attribute access."""

    def __getattr__(self, name: str):
        if len(self) == 1:
            return getattr(self[0], name)
        raise AttributeError(name)


def _key(sp: OpSpec) -> _Key:
    return (sp.alias, sp.target)


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
) -> Tuple[Tuple[OpSpec, ...], Dict[_Key, OpSpec], Dict[str, _OpSpecGroup]]:
    all_specs: Tuple[OpSpec, ...] = tuple(specs)
    by_key: Dict[_Key, OpSpec] = {}
    grouped: Dict[str, list[OpSpec]] = {}
    for sp in specs:
        k = _key(sp)
        by_key[k] = sp
        grouped.setdefault(sp.alias, []).append(sp)
    by_alias: Dict[str, _OpSpecGroup] = {
        alias: _OpSpecGroup(tuple(group)) for alias, group in grouped.items()
    }
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


__all__ = [
    "_Key",
    "_key",
    "_ensure_model_namespaces",
    "_index_specs",
    "_drop_old_entries",
    "_filter_specs",
]
