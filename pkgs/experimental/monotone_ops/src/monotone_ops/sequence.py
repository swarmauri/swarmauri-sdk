"""Sequence and stream operators for prefix/subsequence-style orders."""

from __future__ import annotations

from collections.abc import Callable, Hashable, Iterable, Sequence
from typing import TypeVar

T = TypeVar("T")
H = TypeVar("H", bound=Hashable)


def append_tuple(a: tuple[T, ...], b: tuple[T, ...]) -> tuple[T, ...]:
    """Monotone under prefix order."""

    return a + b


def append_list(a: list[T], b: list[T]) -> list[T]:
    """Monotone under prefix order; returns a fresh list."""

    return [*a, *b]


def prefix_leq(a: Sequence[T], b: Sequence[T]) -> bool:
    return len(a) <= len(b) and all(x == y for x, y in zip(a, b, strict=False))


def longest_common_prefix(a: Sequence[T], b: Sequence[T]) -> tuple[T, ...]:
    """Meet for prefix order."""

    out: list[T] = []
    for x, y in zip(a, b, strict=False):
        if x != y:
            break
        out.append(x)
    return tuple(out)


def is_subsequence(a: Sequence[T], b: Sequence[T]) -> bool:
    """Return true when ``a`` is a subsequence of ``b``."""

    it = iter(b)
    return all(any(x == y for y in it) for x in a)


def ordered_dedup_union(a: Sequence[H], b: Sequence[H]) -> tuple[H, ...]:
    """Append unseen elements from ``b`` to ``a`` while preserving first-seen order."""

    seen = set(a)
    out = list(a)
    for item in b:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return tuple(out)


def sorted_unique_union(a: Iterable[H], b: Iterable[H]) -> tuple[H, ...]:
    """Deterministic set union materialized as a sorted tuple."""

    return tuple(sorted(set(a) | set(b), key=repr))


def cumulative_join(op: Callable[[T, T], T], xs: Iterable[T]) -> tuple[T, ...]:
    """Return running joins for a stream."""

    iterator = iter(xs)
    try:
        acc = next(iterator)
    except StopIteration:
        return ()
    out = [acc]
    for item in iterator:
        acc = op(acc, item)
        out.append(acc)
    return tuple(out)


def windowed_join(op: Callable[[T, T], T], xs: Sequence[T], width: int) -> tuple[T, ...]:
    """Fixed-window monotone summary for each complete window."""

    if width <= 0:
        raise ValueError("width must be positive")
    if len(xs) < width:
        return ()
    out: list[T] = []
    for start in range(0, len(xs) - width + 1):
        acc = xs[start]
        for item in xs[start + 1 : start + width]:
            acc = op(acc, item)
        out.append(acc)
    return tuple(out)


def merge_by_prefix(a: Sequence[T], b: Sequence[T]) -> tuple[T, ...]:
    """Join for comparable prefix-chain elements; raises for conflicting branches."""

    if prefix_leq(a, b):
        return tuple(b)
    if prefix_leq(b, a):
        return tuple(a)
    raise ValueError("sequences are incomparable under prefix order")
