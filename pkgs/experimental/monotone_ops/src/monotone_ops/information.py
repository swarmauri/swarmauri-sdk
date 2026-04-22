"""Information-order lattices.

The common shape is ``UNKNOWN <= known(value) <= CONFLICT``. It supports
safe accumulation of partial facts without lossy overwrites.
"""

from __future__ import annotations

from collections.abc import Hashable, Mapping
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T", bound=Hashable)
K = TypeVar("K", bound=Hashable)


@dataclass(frozen=True, slots=True)
class Unknown:
    def __repr__(self) -> str:
        return "UNKNOWN"


@dataclass(frozen=True, slots=True)
class Conflict:
    def __repr__(self) -> str:
        return "CONFLICT"


@dataclass(frozen=True, slots=True)
class Known(Generic[T]):
    value: T

    def __repr__(self) -> str:
        return f"Known({self.value!r})"


UNKNOWN = Unknown()
CONFLICT = Conflict()
Info = Unknown | Known[T] | Conflict


def known(value: T) -> Known[T]:
    return Known(value)


def is_unknown(x: Info[T]) -> bool:
    return isinstance(x, Unknown)


def is_conflict(x: Info[T]) -> bool:
    return isinstance(x, Conflict)


def information_leq(a: Info[T], b: Info[T]) -> bool:
    """Partial order: unknown bottom, conflict top, equal known values comparable."""

    if isinstance(a, Unknown) or isinstance(b, Conflict):
        return True
    if isinstance(a, Conflict):
        return isinstance(b, Conflict)
    if isinstance(b, Unknown):
        return isinstance(a, Unknown)
    return isinstance(a, Known) and isinstance(b, Known) and a.value == b.value


def information_join(a: Info[T], b: Info[T]) -> Info[T]:
    """Least upper bound for the information order."""

    if isinstance(a, Unknown):
        return b
    if isinstance(b, Unknown):
        return a
    if isinstance(a, Conflict) or isinstance(b, Conflict):
        return CONFLICT
    return a if a.value == b.value else CONFLICT


def information_meet(a: Info[T], b: Info[T]) -> Info[T]:
    """Greatest lower bound for the information order."""

    if isinstance(a, Conflict):
        return b
    if isinstance(b, Conflict):
        return a
    if isinstance(a, Unknown) or isinstance(b, Unknown):
        return UNKNOWN
    return a if a.value == b.value else UNKNOWN


def optional_join(a: T | None, b: T | None) -> Info[T]:
    """Merge optional values into the explicit information lattice."""

    ia: Info[T] = UNKNOWN if a is None else Known(a)
    ib: Info[T] = UNKNOWN if b is None else Known(b)
    return information_join(ia, ib)


def record_join(a: Mapping[K, Info[T]], b: Mapping[K, Info[T]]) -> dict[K, Info[T]]:
    """Pointwise information join over partial records."""

    out: dict[K, Info[T]] = dict(a)
    for key, value in b.items():
        out[key] = value if key not in out else information_join(out[key], value)
    return out


def record_meet(a: Mapping[K, Info[T]], b: Mapping[K, Info[T]]) -> dict[K, Info[T]]:
    """Pointwise information meet over common fields."""

    return {key: information_meet(a[key], b[key]) for key in a.keys() & b.keys()}


def fill_unknowns(base: Mapping[K, T | None], patch: Mapping[K, T | None]) -> dict[K, T | None]:
    """Conservative partial-record completion; existing known values are preserved."""

    out = dict(base)
    for key, value in patch.items():
        if out.get(key) is None:
            out[key] = value
    return out


def support_join(
    a: Mapping[K, frozenset[Hashable]],
    b: Mapping[K, frozenset[Hashable]],
) -> dict[K, frozenset[Hashable]]:
    """Join provenance/support sets fieldwise."""

    out = dict(a)
    for key, value in b.items():
        out[key] = value if key not in out else out[key] | value
    return out
