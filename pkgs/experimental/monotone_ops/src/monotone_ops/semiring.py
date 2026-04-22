"""Semiring operators and algebraic-path utilities."""

from __future__ import annotations

import math
from collections.abc import Callable, Hashable, Mapping
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

T = TypeVar("T")
N = TypeVar("N", bound=Hashable)


@dataclass(frozen=True, slots=True)
class Semiring(Generic[T]):
    add: Callable[[T, T], T]
    mul: Callable[[T, T], T]
    zero: T
    one: T
    name: str = "semiring"


def boolean_semiring() -> Semiring[bool]:
    return Semiring(lambda a, b: a or b, lambda a, b: a and b, False, True, "boolean")


def tropical_min_plus() -> Semiring[float]:
    return Semiring(min, lambda a, b: a + b, math.inf, 0.0, "tropical_min_plus")


def max_plus() -> Semiring[float]:
    return Semiring(max, lambda a, b: a + b, -math.inf, 0.0, "max_plus")


def max_min() -> Semiring[float]:
    """Widest-path semiring: path capacity is min edge capacity; choose max."""

    return Semiring(max, min, -math.inf, math.inf, "max_min")


def viterbi() -> Semiring[float]:
    """Max-product semiring for best-probability paths."""

    return Semiring(max, lambda a, b: a * b, 0.0, 1.0, "viterbi")


def set_union_intersection(universe: frozenset[T]) -> Semiring[frozenset[T]]:
    return Semiring(lambda a, b: a | b, lambda a, b: a & b, frozenset(), universe, "sets")


def semiring_matrix_multiply(a: list[list[T]], b: list[list[T]], sr: Semiring[T]) -> list[list[T]]:
    if not a or not b or len(a[0]) != len(b):
        raise ValueError("incompatible matrix dimensions")
    rows, mid, cols = len(a), len(b), len(b[0])
    out = [[sr.zero for _ in range(cols)] for _ in range(rows)]
    for i in range(rows):
        for j in range(cols):
            acc = sr.zero
            for k in range(mid):
                acc = sr.add(acc, sr.mul(a[i][k], b[k][j]))
            out[i][j] = acc
    return out


def algebraic_path_closure(
    nodes: list[N],
    edges: Mapping[tuple[N, N], T],
    sr: Semiring[T],
) -> dict[tuple[N, N], T]:
    """Floyd-Warshall-style all-pairs closure over a semiring."""

    dist: dict[tuple[N, N], T] = {}
    for i in nodes:
        for j in nodes:
            dist[(i, j)] = sr.one if i == j else sr.zero
    for edge, weight in edges.items():
        dist[edge] = sr.add(dist.get(edge, sr.zero), weight)
    for k in nodes:
        for i in nodes:
            dik = dist[(i, k)]
            for j in nodes:
                candidate = sr.mul(dik, dist[(k, j)])
                dist[(i, j)] = sr.add(dist[(i, j)], candidate)
    return dist


def single_source_dag(
    order: list[N],
    outgoing: Mapping[N, list[tuple[N, T]]],
    source: N,
    sr: Semiring[T],
) -> dict[N, T]:
    """Generic single-source dynamic program on a topologically ordered DAG."""

    dist = {node: sr.zero for node in order}
    dist[source] = sr.one
    for node in order:
        base = dist[node]
        for dst, weight in outgoing.get(node, []):
            dist[dst] = sr.add(dist[dst], sr.mul(base, weight))
    return dist


def lift_semiring_values(values: Mapping[N, T], sr: Semiring[T]) -> Callable[[N], T]:
    """Return a total map with semiring zero for missing keys."""

    def fn(node: N) -> T:
        return values.get(node, sr.zero)

    return fn


def pointwise_semiring_join(a: Mapping[N, T], b: Mapping[N, T], sr: Semiring[T]) -> dict[N, T]:
    keys = a.keys() | b.keys()
    return {key: sr.add(a.get(key, sr.zero), b.get(key, sr.zero)) for key in keys}


def weighted_choice(weights: Mapping[Any, T], sr: Semiring[T]) -> T:
    """Fold semiring addition over a collection of alternatives."""

    acc = sr.zero
    for value in weights.values():
        acc = sr.add(acc, value)
    return acc
