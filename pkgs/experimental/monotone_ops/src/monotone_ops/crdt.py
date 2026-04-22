"""State-based CRDT merge operators as monotone semilattice joins."""

from __future__ import annotations

from collections.abc import Hashable, Mapping
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T", bound=Hashable)
R = TypeVar("R", bound=Hashable)
Dot = TypeVar("Dot", bound=Hashable)

VectorClock = Mapping[R, int]


def vector_clock_join(a: VectorClock[R], b: VectorClock[R]) -> dict[R, int]:
    keys = a.keys() | b.keys()
    return {key: max(a.get(key, 0), b.get(key, 0)) for key in keys}


def vector_clock_leq(a: VectorClock[R], b: VectorClock[R]) -> bool:
    keys = a.keys() | b.keys()
    return all(a.get(key, 0) <= b.get(key, 0) for key in keys)


@dataclass(frozen=True, slots=True)
class GSet(Generic[T]):
    members: frozenset[T] = frozenset()

    def add(self, item: T) -> GSet[T]:
        return GSet(self.members | {item})


def gset_merge(a: GSet[T], b: GSet[T]) -> GSet[T]:
    return GSet(a.members | b.members)


@dataclass(frozen=True, slots=True)
class TwoPSet(Generic[T]):
    adds: frozenset[T] = frozenset()
    removes: frozenset[T] = frozenset()

    @property
    def value(self) -> frozenset[T]:
        return self.adds - self.removes

    def add(self, item: T) -> TwoPSet[T]:
        return TwoPSet(self.adds | {item}, self.removes)

    def remove(self, item: T) -> TwoPSet[T]:
        return TwoPSet(self.adds, self.removes | {item})


def twopset_merge(a: TwoPSet[T], b: TwoPSet[T]) -> TwoPSet[T]:
    return TwoPSet(a.adds | b.adds, a.removes | b.removes)


@dataclass(frozen=True, slots=True)
class GCounter(Generic[R]):
    counts: Mapping[R, int]

    @property
    def value(self) -> int:
        return sum(self.counts.values())

    def increment(self, replica: R, amount: int = 1) -> GCounter[R]:
        if amount < 0:
            raise ValueError("amount must be non-negative")
        out = dict(self.counts)
        out[replica] = out.get(replica, 0) + amount
        return GCounter(out)


def gcounter_merge(a: GCounter[R], b: GCounter[R]) -> GCounter[R]:
    return GCounter(vector_clock_join(a.counts, b.counts))


@dataclass(frozen=True, slots=True)
class PNCounter(Generic[R]):
    positive: GCounter[R]
    negative: GCounter[R]

    @property
    def value(self) -> int:
        return self.positive.value - self.negative.value

    def increment(self, replica: R, amount: int = 1) -> PNCounter[R]:
        return PNCounter(self.positive.increment(replica, amount), self.negative)

    def decrement(self, replica: R, amount: int = 1) -> PNCounter[R]:
        return PNCounter(self.positive, self.negative.increment(replica, amount))


def pncounter_merge(a: PNCounter[R], b: PNCounter[R]) -> PNCounter[R]:
    return PNCounter(gcounter_merge(a.positive, b.positive), gcounter_merge(a.negative, b.negative))


@dataclass(frozen=True, slots=True)
class LWWRegister(Generic[T, R]):
    value: T
    timestamp: int
    replica: R


def lww_merge(a: LWWRegister[T, R], b: LWWRegister[T, R]) -> LWWRegister[T, R]:
    return a if (a.timestamp, a.replica) >= (b.timestamp, b.replica) else b


@dataclass(frozen=True, slots=True)
class ORSet(Generic[T, Dot]):
    adds: Mapping[T, frozenset[Dot]]
    removes: Mapping[T, frozenset[Dot]]

    @property
    def value(self) -> frozenset[T]:
        return frozenset(
            item for item, dots in self.adds.items() if dots - self.removes.get(item, frozenset())
        )

    def add(self, item: T, dot: Dot) -> ORSet[T, Dot]:
        adds = {key: set(value) for key, value in self.adds.items()}
        adds.setdefault(item, set()).add(dot)
        return ORSet({k: frozenset(v) for k, v in adds.items()}, self.removes)

    def remove(self, item: T) -> ORSet[T, Dot]:
        removes = {key: set(value) for key, value in self.removes.items()}
        removes.setdefault(item, set()).update(self.adds.get(item, frozenset()))
        return ORSet(self.adds, {k: frozenset(v) for k, v in removes.items()})


def orset_merge(a: ORSet[T, Dot], b: ORSet[T, Dot]) -> ORSet[T, Dot]:
    keys = a.adds.keys() | b.adds.keys()
    adds = {key: a.adds.get(key, frozenset()) | b.adds.get(key, frozenset()) for key in keys}
    remove_keys = a.removes.keys() | b.removes.keys()
    removes = {key: a.removes.get(key, frozenset()) | b.removes.get(key, frozenset()) for key in remove_keys}
    return ORSet(adds, removes)


@dataclass(frozen=True, slots=True)
class MVRegister(Generic[T, Dot]):
    values: Mapping[Dot, T]

    @property
    def read(self) -> frozenset[T]:
        return frozenset(self.values.values())


def mvregister_merge(a: MVRegister[T, Dot], b: MVRegister[T, Dot]) -> MVRegister[T, Dot]:
    out = dict(a.values)
    out.update(b.values)
    return MVRegister(out)
