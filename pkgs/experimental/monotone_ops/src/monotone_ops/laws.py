"""Finite-sample law checks for monotone operators.

These checks are not proofs. They are deliberately small, deterministic guards that
catch implementation mistakes and document the intended algebraic contract.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from itertools import product
from typing import TypeVar

from .core import Binary, Leq

T = TypeVar("T")
U = TypeVar("U")


@dataclass(frozen=True, slots=True)
class LawReport:
    law: str
    passed: bool
    counterexample: tuple[object, ...] | None = None

    def assert_ok(self) -> None:
        if not self.passed:
            raise AssertionError(f"{self.law} failed: {self.counterexample!r}")


def _materialize(samples: Iterable[T]) -> tuple[T, ...]:
    return tuple(samples)


def check_idempotent(op: Binary[T], samples: Iterable[T]) -> LawReport:
    for a in _materialize(samples):
        if op(a, a) != a:
            return LawReport("idempotent", False, (a, op(a, a)))
    return LawReport("idempotent", True)


def check_commutative(op: Binary[T], samples: Iterable[T]) -> LawReport:
    xs = _materialize(samples)
    for a, b in product(xs, xs):
        if op(a, b) != op(b, a):
            return LawReport("commutative", False, (a, b, op(a, b), op(b, a)))
    return LawReport("commutative", True)


def check_associative(op: Binary[T], samples: Iterable[T]) -> LawReport:
    xs = _materialize(samples)
    for a, b, c in product(xs, xs, xs):
        left = op(op(a, b), c)
        right = op(a, op(b, c))
        if left != right:
            return LawReport("associative", False, (a, b, c, left, right))
    return LawReport("associative", True)


def check_inflationary(op: Binary[T], leq: Leq[T], samples: Iterable[T]) -> LawReport:
    xs = _materialize(samples)
    for a, b in product(xs, xs):
        merged = op(a, b)
        if not leq(a, merged) or not leq(b, merged):
            return LawReport("inflationary", False, (a, b, merged))
    return LawReport("inflationary", True)


def check_deflationary(op: Binary[T], leq: Leq[T], samples: Iterable[T]) -> LawReport:
    xs = _materialize(samples)
    for a, b in product(xs, xs):
        merged = op(a, b)
        if not leq(merged, a) or not leq(merged, b):
            return LawReport("deflationary", False, (a, b, merged))
    return LawReport("deflationary", True)


def check_monotone_unary(
    fn: Callable[[T], U],
    leq_in: Leq[T],
    leq_out: Leq[U],
    samples: Iterable[T],
) -> LawReport:
    xs = _materialize(samples)
    for a, b in product(xs, xs):
        if leq_in(a, b) and not leq_out(fn(a), fn(b)):
            return LawReport("monotone_unary", False, (a, b, fn(a), fn(b)))
    return LawReport("monotone_unary", True)


def check_monotone_binary(op: Binary[T], leq: Leq[T], samples: Iterable[T]) -> LawReport:
    xs = _materialize(samples)
    for a1, a2, b1, b2 in product(xs, xs, xs, xs):
        if leq(a1, a2) and leq(b1, b2):
            left = op(a1, b1)
            right = op(a2, b2)
            if not leq(left, right):
                return LawReport("monotone_binary", False, (a1, a2, b1, b2, left, right))
    return LawReport("monotone_binary", True)


def assert_all(*reports: LawReport) -> None:
    for report in reports:
        report.assert_ok()


def aci_reports(op: Binary[T], samples: Sequence[T]) -> tuple[LawReport, LawReport, LawReport]:
    return (
        check_associative(op, samples),
        check_commutative(op, samples),
        check_idempotent(op, samples),
    )
