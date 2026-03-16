"""Decorator helpers for anonymous route authorization metadata."""

from __future__ import annotations

from collections.abc import Iterable
from typing import TypeVar

from tigrbl_core.config.constants import TIGRBL_ALLOW_ANON_ATTR

_TableT = TypeVar("_TableT", bound=type)


def _normalize_ops(ops: Iterable[str]) -> tuple[str, ...]:
    normalized = [op.strip() for op in ops if isinstance(op, str) and op.strip()]
    seen: set[str] = set()
    deduped: list[str] = []
    for op in normalized:
        if op not in seen:
            seen.add(op)
            deduped.append(op)
    return tuple(deduped)


def allow_anon(*ops: str):
    """Attach anonymous-allowed operation names to a table class.

    Example:
        @allow_anon("list", "read")
        class Item(TableBase):
            ...
    """

    normalized = _normalize_ops(ops)

    def _decorator(table_cls: _TableT) -> _TableT:
        setattr(table_cls, TIGRBL_ALLOW_ANON_ATTR, normalized)
        return table_cls

    return _decorator


__all__ = ["allow_anon"]
