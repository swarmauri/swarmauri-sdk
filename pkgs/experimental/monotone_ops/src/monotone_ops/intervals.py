"""Interval-domain operators for abstract interpretation and range rollups."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True, slots=True, order=True)
class Interval:
    """Closed numeric interval. ``lo > hi`` denotes bottom/empty."""

    lo: float
    hi: float

    @staticmethod
    def empty() -> Interval:
        return Interval(math.inf, -math.inf)

    @staticmethod
    def unbounded() -> Interval:
        return Interval(-math.inf, math.inf)

    @staticmethod
    def point(x: float) -> Interval:
        return Interval(float(x), float(x))

    @property
    def is_empty(self) -> bool:
        return self.lo > self.hi

    def contains(self, x: float) -> bool:
        return not self.is_empty and self.lo <= x <= self.hi


def interval_leq(a: Interval, b: Interval) -> bool:
    """Concretization subset order: narrower intervals are <= wider intervals."""

    if a.is_empty:
        return True
    if b.is_empty:
        return a.is_empty
    return b.lo <= a.lo and a.hi <= b.hi


def interval_hull(a: Interval, b: Interval) -> Interval:
    """Join under subset order: smallest interval containing both operands."""

    if a.is_empty:
        return b
    if b.is_empty:
        return a
    return Interval(min(a.lo, b.lo), max(a.hi, b.hi))


def interval_intersection(a: Interval, b: Interval) -> Interval:
    """Meet under subset order."""

    lo = max(a.lo, b.lo)
    hi = min(a.hi, b.hi)
    return Interval(lo, hi) if lo <= hi else Interval.empty()


def interval_add(a: Interval, b: Interval) -> Interval:
    """Minkowski addition; monotone under subset order."""

    if a.is_empty or b.is_empty:
        return Interval.empty()
    return Interval(a.lo + b.lo, a.hi + b.hi)


def interval_mul(a: Interval, b: Interval) -> Interval:
    """Interval multiplication; monotone under subset order."""

    if a.is_empty or b.is_empty:
        return Interval.empty()
    products = (a.lo * b.lo, a.lo * b.hi, a.hi * b.lo, a.hi * b.hi)
    return Interval(min(products), max(products))


def interval_widen(prev: Interval, nxt: Interval) -> Interval:
    """Classic interval widening used to force convergence of ascending chains."""

    if prev.is_empty:
        return nxt
    if nxt.is_empty:
        return prev
    lo = -math.inf if nxt.lo < prev.lo else prev.lo
    hi = math.inf if nxt.hi > prev.hi else prev.hi
    return Interval(lo, hi)


def interval_narrow(prev: Interval, nxt: Interval) -> Interval:
    """Simple interval narrowing after a widening phase."""

    if prev.is_empty or nxt.is_empty:
        return Interval.empty()
    lo = nxt.lo if prev.lo == -math.inf else prev.lo
    hi = nxt.hi if prev.hi == math.inf else prev.hi
    return interval_intersection(Interval(lo, hi), nxt)


def box_join(a: Sequence[Interval], b: Sequence[Interval]) -> tuple[Interval, ...]:
    if len(a) != len(b):
        raise ValueError("box dimensions differ")
    return tuple(interval_hull(x, y) for x, y in zip(a, b, strict=True))


def box_meet(a: Sequence[Interval], b: Sequence[Interval]) -> tuple[Interval, ...]:
    if len(a) != len(b):
        raise ValueError("box dimensions differ")
    return tuple(interval_intersection(x, y) for x, y in zip(a, b, strict=True))


def box_leq(a: Sequence[Interval], b: Sequence[Interval]) -> bool:
    return len(a) == len(b) and all(interval_leq(x, y) for x, y in zip(a, b, strict=True))


def lower_bound_join(a: float, b: float) -> float:
    """Join for lower-bound facts under reverse numeric order."""

    return min(a, b)


def upper_bound_join(a: float, b: float) -> float:
    """Join for upper-bound facts under usual numeric order."""

    return max(a, b)
