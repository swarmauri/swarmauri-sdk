"""Selector operators induced by total orders and lexicographic orders."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

T = TypeVar("T")


def _identity(x: T) -> T:
    return x


def argmax_by(key: Callable[[T], Any], tie_key: Callable[[T], Any] | None = None) -> Callable[[T, T], T]:
    """Return an idempotent selector for the maximum ``(key, tie_key)`` tuple."""

    tie = tie_key or _identity

    def merge(a: T, b: T) -> T:
        return a if (key(a), tie(a)) >= (key(b), tie(b)) else b

    return merge


def argmin_by(key: Callable[[T], Any], tie_key: Callable[[T], Any] | None = None) -> Callable[[T, T], T]:
    """Return an idempotent selector for the minimum ``(key, tie_key)`` tuple."""

    tie = tie_key or _identity

    def merge(a: T, b: T) -> T:
        return a if (key(a), tie(a)) <= (key(b), tie(b)) else b

    return merge


def lexicographic_max(
    *keys: Callable[[T], Any],
    tie_key: Callable[[T], Any] | None = None,
) -> Callable[[T, T], T]:
    """Lexicographic maximum selector with deterministic full-tie handling."""

    tie = tie_key or _identity

    def merge(a: T, b: T) -> T:
        ka = tuple(key(a) for key in keys) + (tie(a),)
        kb = tuple(key(b) for key in keys) + (tie(b),)
        return a if ka >= kb else b

    return merge


def lexicographic_min(
    *keys: Callable[[T], Any],
    tie_key: Callable[[T], Any] | None = None,
) -> Callable[[T, T], T]:
    """Lexicographic minimum selector with deterministic full-tie handling."""

    tie = tie_key or _identity

    def merge(a: T, b: T) -> T:
        ka = tuple(key(a) for key in keys) + (tie(a),)
        kb = tuple(key(b) for key in keys) + (tie(b),)
        return a if ka <= kb else b

    return merge


def latest_by(clock: Callable[[T], Any], replica: Callable[[T], Any] | None = None) -> Callable[[T, T], T]:
    """Latest-wins selector over a logical clock and deterministic replica id."""

    return argmax_by(clock, replica)


def earliest_by(clock: Callable[[T], Any], replica: Callable[[T], Any] | None = None) -> Callable[[T, T], T]:
    """Earliest-wins selector over a logical clock and deterministic replica id."""

    return argmin_by(clock, replica)


def ordered_level_join(levels: list[T]) -> Callable[[T, T], T]:
    """Join over a caller-supplied total order of finite levels."""

    rank = {level: idx for idx, level in enumerate(levels)}

    def merge(a: T, b: T) -> T:
        return a if rank[a] >= rank[b] else b

    return merge


def ordered_level_meet(levels: list[T]) -> Callable[[T, T], T]:
    """Meet over a caller-supplied total order of finite levels."""

    rank = {level: idx for idx, level in enumerate(levels)}

    def merge(a: T, b: T) -> T:
        return a if rank[a] <= rank[b] else b

    return merge


def pareto_dominates(a: tuple[Any, ...], b: tuple[Any, ...]) -> bool:
    """Componentwise dominance for product-ordered scores."""

    if len(a) != len(b):
        return False
    return all(x >= y for x, y in zip(a, b, strict=True))


def pareto_front(points: frozenset[tuple[Any, ...]]) -> frozenset[tuple[Any, ...]]:
    """Monotone antichain summary: remove dominated points."""

    kept = set(points)
    for p in points:
        for q in points:
            if p != q and pareto_dominates(q, p):
                kept.discard(p)
                break
    return frozenset(kept)


def pareto_join(a: frozenset[tuple[Any, ...]], b: frozenset[tuple[Any, ...]]) -> frozenset[tuple[Any, ...]]:
    """Join for Pareto antichains: union followed by dominated-point pruning."""

    return pareto_front(a | b)
