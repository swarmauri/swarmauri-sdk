from __future__ import annotations

from typing import Any, Mapping


def merge_seq_attr(
    owner: type,
    attr: str,
    *,
    include_inherited: bool = False,
    reverse: bool = False,
) -> tuple[Any, ...]:
    """Merge sequence-like class attributes over the MRO."""

    values: list[Any] = []
    mro = reversed(owner.__mro__) if reverse else owner.__mro__
    for base in mro:
        if include_inherited:
            if not hasattr(base, attr):
                continue
            seq = getattr(base, attr) or ()
        else:
            seq = base.__dict__.get(attr, ()) or ()
        try:
            values.extend(seq)
        except TypeError:  # pragma: no cover - non-iterable
            values.append(seq)
    return tuple(values)


def resolve_table_engine(model: type) -> Any | None:
    """Resolve a table engine with wrapper-precedence semantics."""

    direct_engine: Any | None = None
    inherited_engine: Any | None = None
    for base in model.__mro__:
        if "table_config" in base.__dict__:
            cfg = base.__dict__.get("table_config")
            if isinstance(cfg, Mapping):
                eng = (
                    cfg.get("engine")
                    or cfg.get("db")
                    or cfg.get("database")
                    or cfg.get("engine_provider")
                    or cfg.get("db_provider")
                )
                if eng is not None and direct_engine is None:
                    direct_engine = eng
            continue

        cfg = getattr(base, "table_config", None)
        if isinstance(cfg, Mapping):
            eng = (
                cfg.get("engine")
                or cfg.get("db")
                or cfg.get("database")
                or cfg.get("engine_provider")
                or cfg.get("db_provider")
            )
            if eng is not None:
                inherited_engine = eng

    return inherited_engine if inherited_engine is not None else direct_engine


__all__ = ["merge_seq_attr", "resolve_table_engine"]
