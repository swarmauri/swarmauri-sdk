from __future__ import annotations

from typing import Any, Dict, Iterable, Mapping, Optional, Sequence

import logging

from . import select, and_, asc, desc
from .model import _model_columns, _colspecs

logger = logging.getLogger("uvicorn")

_CANON_OPS = {
    "eq": "eq",
    "=": "eq",
    "==": "eq",
    "ne": "ne",
    "!=": "ne",
    "<>": "ne",
    "lt": "lt",
    "<": "lt",
    "gt": "gt",
    ">": "gt",
    "lte": "lte",
    "le": "lte",
    "<=": "lte",
    "gte": "gte",
    "ge": "gte",
    ">=": "gte",
    "like": "like",
    "not_like": "not_like",
    "ilike": "ilike",
    "not_ilike": "not_ilike",
    "in": "in",
    "not_in": "not_in",
    "nin": "not_in",
}


def _coerce_filters(
    model: type, filters: Optional[Mapping[str, Any]]
) -> Dict[str, Any]:
    logger.debug("_coerce_filters called with filters=%s", filters)
    cols = set(_model_columns(model))
    specs = _colspecs(model)
    raw = dict(filters or {})
    out: Dict[str, Any] = {}
    for k, v in raw.items():
        name, op = k.split("__", 1) if "__" in k else (k, "eq")
        if name not in cols:
            continue
        canon = _CANON_OPS.get(op, op)
        sp = specs.get(name)
        if sp is not None:
            io = getattr(sp, "io", None)
            ops = set(getattr(io, "filter_ops", ()) or [])
            ops = {_CANON_OPS.get(o, o) for o in ops}
            if not ops or canon not in ops:
                continue
        key = name if canon == "eq" else f"{name}__{canon}"
        out[key] = v
    logger.debug("_coerce_filters returning %s", out)
    return out


def _apply_filters(model: type, filters: Mapping[str, Any]) -> Any:
    logger.debug("_apply_filters called with filters=%s", filters)
    if select is None:  # pragma: no cover
        return None
    clauses = []
    for k, v in filters.items():
        name, op = k.split("__", 1) if "__" in k else (k, "eq")
        canon = _CANON_OPS.get(op, op)
        col = getattr(model, name, None)
        if col is None:
            continue
        if canon == "eq":
            clauses.append(col == v)
        elif canon == "ne":
            clauses.append(col != v)
        elif canon == "lt":
            clauses.append(col < v)
        elif canon == "gt":
            clauses.append(col > v)
        elif canon == "lte":
            clauses.append(col <= v)
        elif canon == "gte":
            clauses.append(col >= v)
        elif canon == "like":
            clauses.append(col.like(v))
        elif canon == "not_like":
            clauses.append(~col.like(v))
        elif canon == "ilike":
            clauses.append(col.ilike(v))
        elif canon == "not_ilike":
            clauses.append(~col.ilike(v))
        elif canon == "in":
            seq = list(v) if isinstance(v, (list, tuple, set)) else [v]
            clauses.append(col.in_(seq))
        elif canon == "not_in":
            seq = list(v) if isinstance(v, (list, tuple, set)) else [v]
            clauses.append(~col.in_(seq))
    if not clauses:
        logger.debug("_apply_filters produced no clauses")
        return None
    result = clauses[0] if len(clauses) == 1 else and_(*clauses)
    logger.debug("_apply_filters returning %s", result)
    return result


def _apply_sort(model: type, sort: Any) -> Sequence[Any] | None:
    logger.debug("_apply_sort called with sort=%s", sort)
    if select is None or sort is None:  # pragma: no cover
        return None

    def _tokenize(s: str) -> list[str]:
        return [t.strip() for t in s.split(",") if t.strip()]

    tokens: list[str] = []
    if isinstance(sort, str):
        tokens = _tokenize(sort)
    elif isinstance(sort, Iterable):
        for t in sort:
            if isinstance(t, str):
                tokens.extend(_tokenize(t))

    if not tokens:
        logger.debug("_apply_sort no tokens derived")
        return None

    specs = _colspecs(model)
    order_by_exprs: list[Any] = []
    for tok in tokens:
        direction = "asc"
        name = tok

        if ":" in tok:
            name, dirpart = tok.split(":", 1)
            name = name.strip()
            dirpart = dirpart.strip().lower()
            if dirpart in ("desc", "descending"):
                direction = "desc"
        elif tok.startswith("-"):
            name = tok[1:]
            direction = "desc"

        col = getattr(model, name, None)
        if col is None:
            continue
        sp = specs.get(name)
        if sp is not None:
            io = getattr(sp, "io", None)
            if io is not None and not getattr(io, "sortable", False):
                continue
        if direction == "desc":
            order_by_exprs.append(desc(col))
        else:
            order_by_exprs.append(asc(col))

    result = order_by_exprs or None
    logger.debug("_apply_sort returning %s", result)
    return result
