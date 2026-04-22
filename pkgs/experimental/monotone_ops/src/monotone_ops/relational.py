"""Positive relational algebra operators under relation inclusion."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from typing import Any

Row = tuple[Any, ...]
Relation = frozenset[Row]


@dataclass(frozen=True, slots=True)
class NamedRelation:
    schema: tuple[str, ...]
    rows: Relation

    def __post_init__(self) -> None:
        width = len(self.schema)
        if any(len(row) != width for row in self.rows):
            raise ValueError("row width does not match schema")


def rel_leq(a: Relation, b: Relation) -> bool:
    return a <= b


def rel_union(a: Relation, b: Relation) -> Relation:
    return a | b


def rel_intersection(a: Relation, b: Relation) -> Relation:
    return a & b


def select(rel: Relation, predicate: Callable[[Row], bool]) -> Relation:
    """Selection by a fixed positive predicate; monotone in ``rel``."""

    return frozenset(row for row in rel if predicate(row))


def project(rel: Relation, indexes: Sequence[int]) -> Relation:
    return frozenset(tuple(row[i] for i in indexes) for row in rel)


def cartesian_product(a: Relation, b: Relation) -> Relation:
    return frozenset(row_a + row_b for row_a in a for row_b in b)


def named_project(rel: NamedRelation, columns: Sequence[str]) -> NamedRelation:
    indexes = tuple(rel.schema.index(column) for column in columns)
    return NamedRelation(tuple(columns), project(rel.rows, indexes))


def named_select(rel: NamedRelation, predicate: Callable[[dict[str, Any]], bool]) -> NamedRelation:
    def row_predicate(row: Row) -> bool:
        return predicate(dict(zip(rel.schema, row, strict=True)))

    return NamedRelation(rel.schema, select(rel.rows, row_predicate))


def natural_join(a: NamedRelation, b: NamedRelation) -> NamedRelation:
    """Natural join. Monotone in both input relations."""

    common = tuple(column for column in a.schema if column in b.schema)
    a_common = tuple(a.schema.index(column) for column in common)
    b_common = tuple(b.schema.index(column) for column in common)
    b_only = tuple(column for column in b.schema if column not in common)
    b_only_idx = tuple(b.schema.index(column) for column in b_only)
    schema = a.schema + b_only
    rows: set[Row] = set()
    for row_a in a.rows:
        key_a = tuple(row_a[i] for i in a_common)
        for row_b in b.rows:
            key_b = tuple(row_b[i] for i in b_common)
            if key_a == key_b:
                rows.add(row_a + tuple(row_b[i] for i in b_only_idx))
    return NamedRelation(schema, frozenset(rows))


def semi_join(a: NamedRelation, b: NamedRelation) -> NamedRelation:
    """Positive semijoin: keep rows in ``a`` that join with at least one row in ``b``."""

    joined = natural_join(a, b)
    return named_project(joined, a.schema)


def rename(rel: NamedRelation, mapping: dict[str, str]) -> NamedRelation:
    return NamedRelation(tuple(mapping.get(col, col) for col in rel.schema), rel.rows)


def union_named(a: NamedRelation, b: NamedRelation) -> NamedRelation:
    if a.schema != b.schema:
        raise ValueError("schemas must match")
    return NamedRelation(a.schema, a.rows | b.rows)


def positive_consequence(
    facts: NamedRelation,
    rule: Callable[[NamedRelation], NamedRelation],
    *,
    max_steps: int = 10_000,
) -> NamedRelation:
    """Inflationary least-fixed-point loop for a positive relational rule."""

    cur = facts
    for _ in range(max_steps):
        nxt = union_named(cur, rule(cur))
        if nxt == cur:
            return cur
        cur = nxt
    raise RuntimeError("positive_consequence did not stabilize")


def relation_from_dicts(rows: Iterable[dict[str, Any]]) -> NamedRelation:
    rows = tuple(rows)
    if not rows:
        return NamedRelation((), frozenset())
    schema = tuple(rows[0].keys())
    return NamedRelation(schema, frozenset(tuple(row[col] for col in schema) for row in rows))
