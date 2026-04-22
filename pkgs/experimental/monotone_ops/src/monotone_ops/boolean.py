"""Boolean monotone operators.

Positive Boolean functions are exactly those expressible without negation using
AND/OR over variables. Threshold functions are another important monotone family.
"""

from __future__ import annotations

from collections.abc import Callable, Hashable, Mapping, Sequence


def bool_or(a: bool, b: bool) -> bool:
    """Join for ``False < True``."""

    return a or b


def bool_and(a: bool, b: bool) -> bool:
    """Meet for ``False < True``."""

    return a and b


def bool_leq(a: bool, b: bool) -> bool:
    return (not a) or b


def any_true(values: Sequence[bool]) -> bool:
    return any(values)


def all_true(values: Sequence[bool]) -> bool:
    return all(values)


def at_least_k(values: Sequence[bool], k: int) -> bool:
    """Monotone threshold predicate over Boolean vectors."""

    if k < 0:
        raise ValueError("k must be non-negative")
    return sum(1 for value in values if value) >= k


def at_most_k_false(values: Sequence[bool], k: int) -> bool:
    """Equivalent monotone reliability predicate: no more than ``k`` failures."""

    if k < 0:
        raise ValueError("k must be non-negative")
    return sum(1 for value in values if not value) <= k


def majority(values: Sequence[bool]) -> bool:
    if not values:
        raise ValueError("majority is undefined for an empty sequence")
    return at_least_k(values, len(values) // 2 + 1)


def monotone_dnf(clauses: Sequence[frozenset[Hashable]]) -> Callable[[Mapping[Hashable, bool]], bool]:
    """Build a positive DNF predicate from clauses of variable names.

    A clause is satisfied when every variable in the clause is true. The DNF is
    satisfied when at least one clause is satisfied.
    """

    frozen = tuple(frozenset(clause) for clause in clauses)

    def predicate(assignment: Mapping[Hashable, bool]) -> bool:
        return any(all(assignment.get(var, False) for var in clause) for clause in frozen)

    return predicate


def monotone_cnf(clauses: Sequence[frozenset[Hashable]]) -> Callable[[Mapping[Hashable, bool]], bool]:
    """Build a positive CNF predicate from clauses of variable names.

    A clause is satisfied when any variable in the clause is true. The CNF is
    satisfied when all clauses are satisfied.
    """

    frozen = tuple(frozenset(clause) for clause in clauses)

    def predicate(assignment: Mapping[Hashable, bool]) -> bool:
        return all(any(assignment.get(var, False) for var in clause) for clause in frozen)

    return predicate


def k_of_n_merger(k: int) -> Callable[[frozenset[Hashable], frozenset[Hashable]], frozenset[Hashable]]:
    """Return a merge over evidence sets plus an attached threshold.

    The merge is union; the threshold is checked by ``len(state) >= k``.
    """

    if k <= 0:
        raise ValueError("k must be positive")

    def merge(a: frozenset[Hashable], b: frozenset[Hashable]) -> frozenset[Hashable]:
        return a | b

    merge.threshold = k  # type: ignore[attr-defined]
    return merge
