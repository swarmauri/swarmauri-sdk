"""Security-label, permission, trust, and risk monotone operators."""

from __future__ import annotations

from collections.abc import Callable
from enum import Enum
from typing import TypeVar

T = TypeVar("T")


class AccessDecision(Enum):
    ALLOW = 0
    ABSTAIN = 1
    DENY = 2


def restrictive_join(a: AccessDecision, b: AccessDecision) -> AccessDecision:
    """Join under the order ALLOW < ABSTAIN < DENY."""

    return a if a.value >= b.value else b


def permissive_meet(a: AccessDecision, b: AccessDecision) -> AccessDecision:
    """Meet under the order ALLOW < ABSTAIN < DENY."""

    return a if a.value <= b.value else b


def permission_union(a: int, b: int) -> int:
    """Bit permission join under capability inclusion."""

    return a | b


def permission_intersection(a: int, b: int) -> int:
    """Bit permission meet under capability inclusion."""

    return a & b


def risk_join(a: float, b: float) -> float:
    """Risk aggregation as max under usual risk order."""

    return max(a, b)


def trust_meet(a: float, b: float) -> float:
    """Trust aggregation as min under usual trust order."""

    return min(a, b)


def ordered_label_join(levels: tuple[T, ...]) -> Callable[[T, T], T]:
    """Confidentiality-style join: choose the higher label."""

    rank = {level: idx for idx, level in enumerate(levels)}

    def merge(a: T, b: T) -> T:
        return a if rank[a] >= rank[b] else b

    return merge


def ordered_label_meet(levels: tuple[T, ...]) -> Callable[[T, T], T]:
    """Confidentiality-style meet: choose the lower label."""

    rank = {level: idx for idx, level in enumerate(levels)}

    def merge(a: T, b: T) -> T:
        return a if rank[a] <= rank[b] else b

    return merge


def clearance_allows(clearance: T, required: T, levels: tuple[T, ...]) -> bool:
    rank = {level: idx for idx, level in enumerate(levels)}
    return rank[clearance] >= rank[required]


def integrity_join(levels: tuple[T, ...]) -> Callable[[T, T], T]:
    """Biba-style integrity join: lower integrity dominates conservatively."""

    return ordered_label_meet(levels)


def integrity_meet(levels: tuple[T, ...]) -> Callable[[T, T], T]:
    return ordered_label_join(levels)
