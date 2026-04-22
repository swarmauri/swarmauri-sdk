"""Galois connections, closures, interiors, and nuclei."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar

C = TypeVar("C")
A = TypeVar("A")
T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class ClosureOperator(Generic[T]):
    """A monotone, extensive, idempotent operator by contract."""

    apply: Callable[[T], T]

    def __call__(self, x: T) -> T:
        return self.apply(x)


@dataclass(frozen=True, slots=True)
class InteriorOperator(Generic[T]):
    """A monotone, reductive, idempotent operator by contract."""

    apply: Callable[[T], T]

    def __call__(self, x: T) -> T:
        return self.apply(x)


@dataclass(frozen=True, slots=True)
class GaloisConnection(Generic[C, A]):
    """Adjunction skeleton: abstraction ``alpha`` and concretization ``gamma``."""

    alpha: Callable[[C], A]
    gamma: Callable[[A], C]

    def closure_on_concrete(self) -> ClosureOperator[C]:
        return ClosureOperator(lambda x: self.gamma(self.alpha(x)))

    def interior_on_abstract(self) -> InteriorOperator[A]:
        return InteriorOperator(lambda x: self.alpha(self.gamma(x)))


def compose_closure(a: ClosureOperator[T], b: ClosureOperator[T]) -> ClosureOperator[T]:
    """Compose closures; iterate externally if commutation is not guaranteed."""

    return ClosureOperator(lambda x: a(b(x)))


def compose_interior(a: InteriorOperator[T], b: InteriorOperator[T]) -> InteriorOperator[T]:
    return InteriorOperator(lambda x: a(b(x)))


def fixed_by(op: Callable[[T], T], x: T) -> bool:
    return op(x) == x


def Moore_closure(seed: frozenset[T], closed_sets: frozenset[frozenset[T]]) -> frozenset[T]:
    """Closure as intersection of all closed sets containing ``seed``."""

    containing = [closed for closed in closed_sets if seed <= closed]
    if not containing:
        raise ValueError("no closed set contains seed")
    acc = containing[0]
    for closed in containing[1:]:
        acc = acc & closed
    return acc


def Alexandrov_interior(seed: frozenset[T], open_sets: frozenset[frozenset[T]]) -> frozenset[T]:
    """Interior as union of all open sets contained in ``seed``."""

    acc: frozenset[T] = frozenset()
    for opened in open_sets:
        if opened <= seed:
            acc = acc | opened
    return acc
