"""Small abstract domains: sign, taint, and finite powerset abstractions."""

from __future__ import annotations

from collections.abc import Callable, Hashable
from enum import Enum
from typing import TypeVar

T = TypeVar("T", bound=Hashable)


class Sign(Enum):
    BOTTOM = frozenset()  # type: ignore[var-annotated]
    NEG = frozenset({"neg"})
    ZERO = frozenset({"zero"})
    POS = frozenset({"pos"})
    NONPOS = frozenset({"neg", "zero"})
    NONNEG = frozenset({"zero", "pos"})
    NONZERO = frozenset({"neg", "pos"})
    TOP = frozenset({"neg", "zero", "pos"})


_SIGN_BY_SET: dict[frozenset[str], Sign] = {sign.value: sign for sign in Sign}


def sign_of_int(x: int) -> Sign:
    if x < 0:
        return Sign.NEG
    if x > 0:
        return Sign.POS
    return Sign.ZERO


def sign_leq(a: Sign, b: Sign) -> bool:
    return a.value <= b.value


def sign_join(a: Sign, b: Sign) -> Sign:
    return _SIGN_BY_SET[a.value | b.value]


def sign_meet(a: Sign, b: Sign) -> Sign:
    return _SIGN_BY_SET[a.value & b.value]


def sign_negate(a: Sign) -> Sign:
    mapping = {"neg": "pos", "zero": "zero", "pos": "neg"}
    return _SIGN_BY_SET[frozenset(mapping[x] for x in a.value)]


def sign_add(a: Sign, b: Sign) -> Sign:
    """Sound monotone abstract addition over signs."""

    if not a.value or not b.value:
        return Sign.BOTTOM
    concrete: set[str] = set()
    for x in a.value:
        for y in b.value:
            if x == "zero":
                concrete.add(y)
            elif y == "zero" or x == y:
                concrete.add(x)
            else:
                concrete.update({"neg", "zero", "pos"})
    return _SIGN_BY_SET[frozenset(concrete)]


class Taint(Enum):
    CLEAN = 0
    SUSPECT = 1
    TAINTED = 2


def taint_leq(a: Taint, b: Taint) -> bool:
    return a.value <= b.value


def taint_join(a: Taint, b: Taint) -> Taint:
    return a if a.value >= b.value else b


def taint_meet(a: Taint, b: Taint) -> Taint:
    return a if a.value <= b.value else b


def powerset_join(a: frozenset[T], b: frozenset[T]) -> frozenset[T]:
    return a | b


def powerset_meet(a: frozenset[T], b: frozenset[T]) -> frozenset[T]:
    return a & b


def finite_abstraction(
    universe: frozenset[T],
) -> tuple[Callable[[frozenset[T]], frozenset[T]], Callable[[frozenset[T]], frozenset[T]]]:
    """Return abstraction/concretization for values in a finite universe."""

    def alpha(values: frozenset[T]) -> frozenset[T]:
        return values & universe

    def gamma(abs_value: frozenset[T]) -> frozenset[T]:
        return abs_value & universe

    return alpha, gamma
