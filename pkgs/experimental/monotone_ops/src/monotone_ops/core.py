"""Core protocols and reusable combinators for monotone operators."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator, Sequence
from dataclasses import dataclass
from typing import Any, Generic, Protocol, TypeVar, overload

T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")
T_contra = TypeVar("T_contra", contravariant=True)
U_co = TypeVar("U_co", covariant=True)


class Unary(Protocol[T_contra, U_co]):
    """A unary operator."""

    def __call__(self, x: T_contra) -> U_co: ...


class Binary(Protocol[T]):
    """A closed binary operator."""

    def __call__(self, a: T, b: T) -> T: ...


class Leq(Protocol[T_contra]):
    """A partial-order predicate: ``leq(a, b)`` means ``a <= b``."""

    def __call__(self, a: T_contra, b: T_contra) -> bool: ...


@dataclass(frozen=True, slots=True)
class Operator(Generic[T]):
    """Named binary operator with law metadata.

    The laws are descriptive; use ``monotone_ops.laws`` for finite sample checks.
    """

    name: str
    merge: Binary[T]
    laws: frozenset[str] = frozenset()
    order: Leq[T] | None = None
    doc: str = ""

    def __call__(self, a: T, b: T) -> T:
        return self.merge(a, b)


class _Missing:
    pass


_MISSING = _Missing()


@overload
def fold(op: Binary[T], items: Iterable[T]) -> T | None: ...


@overload
def fold(op: Binary[T], items: Iterable[T], *, initial: T) -> T: ...


def fold(op: Binary[T], items: Iterable[T], *, initial: T | _Missing = _MISSING) -> T | None:
    """Fold a closed binary operator over an iterable.

    Without ``initial``, an empty iterable returns ``None``. With ``initial``, the
    result is always a ``T``. Associative operators are streaming-friendly; ACI
    operators are also order-independent.
    """

    iterator = iter(items)
    if isinstance(initial, _Missing):
        try:
            acc = next(iterator)
        except StopIteration:
            return None
    else:
        acc = initial
    for item in iterator:
        acc = op(acc, item)
    return acc


def scan(op: Binary[T], items: Iterable[T], *, initial: T | _Missing = _MISSING) -> Iterator[T]:
    """Yield running aggregates."""

    iterator = iter(items)
    if isinstance(initial, _Missing):
        try:
            acc = next(iterator)
        except StopIteration:
            return
        yield acc
    else:
        acc = initial
    for item in iterator:
        acc = op(acc, item)
        yield acc


def identity(x: T) -> T:
    """Identity unary operator."""

    return x


def constant(value: U) -> Callable[[T], U]:
    """Constant unary operator. Constant maps are monotone for every input order."""

    def inner(_: T) -> U:
        return value

    return inner


def compose(f: Callable[[U], V], g: Callable[[T], U]) -> Callable[[T], V]:
    """Compose monotone maps. If both inputs are monotone, the result is monotone."""

    def inner(x: T) -> V:
        return f(g(x))

    return inner


def dual(leq: Leq[T]) -> Leq[T]:
    """Reverse a partial order."""

    def inner(a: T, b: T) -> bool:
        return leq(b, a)

    return inner


def eq_leq(a: T, b: T) -> bool:
    """Discrete order: values are comparable only when equal."""

    return a == b


def total_leq(a: T, b: T) -> bool:
    """Use Python's ``<=`` as a total/preorder predicate."""

    return bool(a <= b)  # type: ignore[operator]


def subset_leq(a: frozenset[T], b: frozenset[T]) -> bool:
    """Subset order for immutable sets."""

    return a <= b


def prefix_leq(a: Sequence[T], b: Sequence[T]) -> bool:
    """Prefix order for sequences."""

    return len(a) <= len(b) and all(x == y for x, y in zip(a, b, strict=False))


def product_leq(leqs: Sequence[Leq[Any]]) -> Leq[tuple[Any, ...]]:
    """Componentwise product order for tuples."""

    def inner(a: tuple[Any, ...], b: tuple[Any, ...]) -> bool:
        if len(a) != len(b) or len(a) != len(leqs):
            return False
        return all(leq(x, y) for leq, x, y in zip(leqs, a, b, strict=True))

    return inner


def is_chain(leq: Leq[T], xs: Sequence[T]) -> bool:
    """Return true when ``xs`` is ascending under ``leq``."""

    return all(leq(a, b) for a, b in zip(xs, xs[1:], strict=False))


def iterate_until_stable(step: Callable[[T], T], seed: T, *, max_steps: int = 10_000) -> T:
    """Iterate ``step`` until structural equality stabilizes."""

    cur = seed
    for _ in range(max_steps):
        nxt = step(cur)
        if nxt == cur:
            return cur
        cur = nxt
    raise RuntimeError(f"iteration did not stabilize within {max_steps} steps")
