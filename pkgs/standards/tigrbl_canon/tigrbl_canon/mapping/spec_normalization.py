from __future__ import annotations

from dataclasses import replace
from typing import Any, Iterable, Mapping

from .._spec.app_spec import AppSpec


def _seqify(value: Any) -> tuple[Any, ...]:
    """Normalize sequence-like inputs while treating scalars as a single item."""

    if value is None:
        return ()
    if isinstance(value, tuple):
        return value
    if isinstance(value, (str, bytes, bytearray)):
        return (value,)
    if isinstance(value, Mapping):
        return (value,)
    if isinstance(value, Iterable):
        return tuple(value)
    return (value,)


def merge_seq_attr(
    owner: type,
    attr: str,
    *,
    include_inherited: bool = False,
    reverse: bool = False,
    dedupe: bool = True,
) -> tuple[Any, ...]:
    """Merge sequence-like class attributes over the MRO."""

    values: list[Any] = []
    seen_hashable: set[Any] = set()
    mro = reversed(owner.__mro__) if reverse else owner.__mro__
    for base in mro:
        if include_inherited:
            if not hasattr(base, attr):
                continue
            seq = getattr(base, attr) or ()
        else:
            seq = base.__dict__.get(attr, ()) or ()
        for item in _seqify(seq):
            if dedupe:
                try:
                    if item in seen_hashable:
                        continue
                    seen_hashable.add(item)
                except TypeError:
                    # Unhashable items keep insertion order and fall back to equality.
                    if any(item == existing for existing in values):
                        continue
            values.append(item)
    return tuple(values)


def normalize_app_spec(spec: AppSpec) -> AppSpec:
    """Return a mapping-normalized AppSpec snapshot with stable sequence fields."""

    return replace(
        spec,
        routers=_seqify(spec.routers),
        ops=_seqify(spec.ops),
        tables=_seqify(spec.tables),
        schemas=_seqify(spec.schemas),
        hooks=_seqify(spec.hooks),
        security_deps=_seqify(spec.security_deps),
        deps=_seqify(spec.deps),
        middlewares=_seqify(spec.middlewares),
        jsonrpc_prefix=str(spec.jsonrpc_prefix or "/rpc"),
        system_prefix=str(spec.system_prefix or "/system"),
    )


def resolve_table_engine(model: type) -> Any | None:
    """Resolve a table engine with wrapper-precedence semantics."""
    resolved_engine: Any | None = None
    for base in model.__mro__:
        cfg = base.__dict__.get("table_config")
        if not isinstance(cfg, Mapping):
            continue
        eng = (
            cfg.get("engine")
            or cfg.get("db")
            or cfg.get("database")
            or cfg.get("engine_provider")
            or cfg.get("db_provider")
        )
        if eng is not None:
            # Right-most class in the effective MRO wins (wrapper precedence).
            resolved_engine = eng

    if resolved_engine is not None:
        return resolved_engine

    cfg = getattr(model, "table_config", None)
    if isinstance(cfg, Mapping):
        return (
            cfg.get("engine")
            or cfg.get("db")
            or cfg.get("database")
            or cfg.get("engine_provider")
            or cfg.get("db_provider")
        )
    return None


__all__ = ["merge_seq_attr", "normalize_app_spec", "resolve_table_engine"]
