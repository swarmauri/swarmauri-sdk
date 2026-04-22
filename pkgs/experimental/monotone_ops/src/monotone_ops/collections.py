"""Monotone operators over sets, maps, tuples, counters, and bitsets."""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Hashable, Mapping, Sequence
from typing import Any, TypeVar

T = TypeVar("T", bound=Hashable)
K = TypeVar("K", bound=Hashable)
V = TypeVar("V")


def set_union(a: frozenset[T], b: frozenset[T]) -> frozenset[T]:
    return a | b


def set_intersection(a: frozenset[T], b: frozenset[T]) -> frozenset[T]:
    return a & b


def set_subset_leq(a: frozenset[T], b: frozenset[T]) -> bool:
    return a <= b


def set_superset_leq(a: frozenset[T], b: frozenset[T]) -> bool:
    return a >= b


def bit_or(a: int, b: int) -> int:
    """Join for bitset inclusion."""

    return a | b


def bit_and(a: int, b: int) -> int:
    """Meet for bitset inclusion."""

    return a & b


def bit_subset_leq(a: int, b: int) -> bool:
    """Return true when every bit set in ``a`` is also set in ``b``."""

    return (a & b) == a


def dict_join(val_join: Callable[[V, V], V]) -> Callable[[Mapping[K, V], Mapping[K, V]], dict[K, V]]:
    """Key-union map join with pointwise value join."""

    def merge(a: Mapping[K, V], b: Mapping[K, V]) -> dict[K, V]:
        out = dict(a)
        for key, value in b.items():
            out[key] = value if key not in out else val_join(out[key], value)
        return out

    return merge


def dict_meet(val_meet: Callable[[V, V], V]) -> Callable[[Mapping[K, V], Mapping[K, V]], dict[K, V]]:
    """Key-intersection map meet with pointwise value meet."""

    def merge(a: Mapping[K, V], b: Mapping[K, V]) -> dict[K, V]:
        return {key: val_meet(a[key], b[key]) for key in a.keys() & b.keys()}

    return merge


def dict_pointwise_leq(val_leq: Callable[[V, V], bool]) -> Callable[[Mapping[K, V], Mapping[K, V]], bool]:
    """Pointwise partial-map order: all keys in ``a`` exist in ``b`` and compare."""

    def leq(a: Mapping[K, V], b: Mapping[K, V]) -> bool:
        return all(key in b and val_leq(value, b[key]) for key, value in a.items())

    return leq


def tuple_pointwise(
    *ops: Callable[[Any, Any], Any],
) -> Callable[[tuple[Any, ...], tuple[Any, ...]], tuple[Any, ...]]:
    """Lift binary operators pointwise to tuples."""

    def merge(a: tuple[Any, ...], b: tuple[Any, ...]) -> tuple[Any, ...]:
        if len(a) != len(b) or len(a) != len(ops):
            raise ValueError("tuple arity mismatch")
        return tuple(op(x, y) for op, x, y in zip(ops, a, b, strict=True))

    return merge


def sequence_pointwise(op: Callable[[V, V], V]) -> Callable[[Sequence[V], Sequence[V]], tuple[V, ...]]:
    """Pointwise merge for equal-length sequences."""

    def merge(a: Sequence[V], b: Sequence[V]) -> tuple[V, ...]:
        if len(a) != len(b):
            raise ValueError("sequence length mismatch")
        return tuple(op(x, y) for x, y in zip(a, b, strict=True))

    return merge


def counter_add(a: Counter[T], b: Counter[T]) -> Counter[T]:
    """Multiset sum under pointwise count order."""

    out = Counter(a)
    out.update(b)
    return out


def counter_max(a: Counter[T], b: Counter[T]) -> Counter[T]:
    """Pointwise maximum count join."""

    return a | b


def counter_min(a: Counter[T], b: Counter[T]) -> Counter[T]:
    """Pointwise minimum count meet."""

    return a & b


def counter_leq(a: Counter[T], b: Counter[T]) -> bool:
    keys = set(a) | set(b)
    return all(a[key] <= b[key] for key in keys)


def frozendict(items: Mapping[K, V] | Sequence[tuple[K, V]]) -> frozenset[tuple[K, V]]:
    """Hashable map representation useful for law-test samples."""

    return frozenset(dict(items).items())


def frozendict_join(
    val_join: Callable[[V, V], V],
) -> Callable[[frozenset[tuple[K, V]], frozenset[tuple[K, V]]], frozenset[tuple[K, V]]]:
    merge_dict = dict_join(val_join)

    def merge(a: frozenset[tuple[K, V]], b: frozenset[tuple[K, V]]) -> frozenset[tuple[K, V]]:
        return frozenset(merge_dict(dict(a), dict(b)).items())

    return merge
