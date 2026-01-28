from __future__ import annotations

from typing import Any, Dict, Mapping, Tuple

import logging

from ....column.mro_collect import mro_collect_columns

logger = logging.getLogger("uvicorn")


def _pk_columns(model: type) -> Tuple[Any, ...]:
    logger.debug("_pk_columns called with model=%s", model)
    table = getattr(model, "__table__", None)
    if table is None:
        raise ValueError(f"{model.__name__} has no __table__")
    pks = tuple(table.primary_key.columns)  # type: ignore[attr-defined]
    if not pks:
        raise ValueError(f"{model.__name__} has no primary key")
    logger.debug("_pk_columns returning %s", pks)
    return pks


def _single_pk_name(model: type) -> str:
    logger.debug("_single_pk_name called with model=%s", model)
    pks = _pk_columns(model)
    if len(pks) != 1:
        raise NotImplementedError(
            f"{model.__name__} has composite PK; not supported by default core"
        )
    name = pks[0].name
    logger.debug("_single_pk_name returning %s", name)
    return name


def _coerce_pk_value(model: type, value: Any) -> Any:
    logger.debug("_coerce_pk_value called with model=%s value=%s", model, value)
    if value is None:
        return None
    try:
        col = _pk_columns(model)[0]
        py_type = col.type.python_type  # type: ignore[attr-defined]
    except Exception:  # pragma: no cover - best effort
        logger.debug("_coerce_pk_value returning original value %s", value)
        return value
    if isinstance(value, py_type):
        return value
    try:
        coerced = py_type(value)
        logger.debug("_coerce_pk_value coerced %s to %s", value, coerced)
        return coerced
    except Exception:  # pragma: no cover - fallback to original
        logger.debug("_coerce_pk_value failed to coerce %s", value)
        return value


def _model_columns(model: type) -> Tuple[str, ...]:
    logger.debug("_model_columns called with model=%s", model)
    table = getattr(model, "__table__", None)
    if table is None:
        return ()
    cols = tuple(c.name for c in table.columns)
    logger.debug("_model_columns returning %s", cols)
    return cols


def _colspecs(model: type) -> Mapping[str, Any]:
    logger.info("_colspecs called with model=%s", model)
    cache_bust = hash(
        (
            id(getattr(model, "__tigrbl_colspecs__", None)),
            id(getattr(model, "__tigrbl_cols__", None)),
        )
    )
    specs = mro_collect_columns(model, _cache_bust=cache_bust)
    logger.info("_colspecs returning %s", specs)
    return specs


def _filter_in_values(
    model: type, data: Mapping[str, Any], verb: str
) -> Dict[str, Any]:
    logger.info("_filter_in_values called with data=%s verb=%s", data, verb)
    specs = _colspecs(model)
    if not specs:
        result = dict(data)
        logger.debug("_filter_in_values returning %s", result)
        return result
    out: Dict[str, Any] = {}
    for k, v in data.items():
        sp = specs.get(k)
        if sp is None:
            out[k] = v
            continue
        io = getattr(sp, "io", None)
        allowed = True
        if io is not None:
            in_verbs = getattr(io, "in_verbs", ())
            mutable = getattr(io, "mutable_verbs", ())
            if in_verbs and verb not in in_verbs:
                allowed = False
            if mutable and verb not in mutable:
                allowed = False
        if allowed:
            out[k] = v
    logger.info("_filter_in_values returning %s", out)
    return out


def _immutable_columns(model: type, verb: str) -> set[str]:
    logger.info("_immutable_columns called with model=%s verb=%s", model, verb)
    specs = _colspecs(model)
    if not specs:
        return set()
    imm: set[str] = set()
    for name, sp in specs.items():
        io = getattr(sp, "io", None)
        mutable = getattr(io, "mutable_verbs", ()) if io else ()
        if mutable and verb not in mutable:
            imm.add(name)
    logger.info("_immutable_columns returning %s", imm)
    return imm
