from __future__ import annotations

import logging
from functools import lru_cache
from typing import Any, Mapping, Tuple

from .table_spec import TableSpec

logger = logging.getLogger("uvicorn")


def _merge_seq_attr(model: type, attr: str) -> Tuple[Any, ...]:
    values: list[Any] = []
    for base in model.__mro__:
        seq = base.__dict__.get(attr, ()) or ()
        try:
            values.extend(seq)
        except TypeError:  # pragma: no cover - non-iterable
            values.append(seq)
    return tuple(values)


@lru_cache(maxsize=None)
def mro_collect_table_spec(model: type) -> TableSpec:
    """Collect TableSpec-like declarations across the model's MRO.

    Merges common spec attributes (OPS, COLUMNS, SCHEMAS, HOOKS, SECURITY_DEPS,
    DEPS) declared on the class or any mixins. Engine bindings declared via
    ``table_config`` prefer the last inherited binding in the MRO (from
    wrapper classes) and otherwise fall back to the first direct binding.
    """

    logger.info("Collecting table spec for %s", model.__name__)

    direct_engine: Any | None = None
    inherited_engine: Any | None = None
    for base in model.__mro__:
        if "table_config" in base.__dict__:
            cfg = base.__dict__.get("table_config")
            if isinstance(cfg, Mapping):
                eng = (
                    cfg.get("engine")
                    or cfg.get("db")
                    or cfg.get("database")
                    or cfg.get("engine_provider")
                    or cfg.get("db_provider")
                )
                if eng is not None and direct_engine is None:
                    direct_engine = eng
            continue

        cfg = getattr(base, "table_config", None)
        if isinstance(cfg, Mapping):
            eng = (
                cfg.get("engine")
                or cfg.get("db")
                or cfg.get("database")
                or cfg.get("engine_provider")
                or cfg.get("db_provider")
            )
            if eng is not None:
                inherited_engine = eng

    engine = inherited_engine if inherited_engine is not None else direct_engine

    spec = TableSpec(
        model=model,
        engine=engine,
        ops=_merge_seq_attr(model, "OPS"),
        columns=_merge_seq_attr(model, "COLUMNS"),
        schemas=_merge_seq_attr(model, "SCHEMAS"),
        hooks=_merge_seq_attr(model, "HOOKS"),
        security_deps=_merge_seq_attr(model, "SECURITY_DEPS"),
        deps=_merge_seq_attr(model, "DEPS"),
    )

    logger.debug(
        "Collected table spec for %s: %d ops, %d columns",
        model.__name__,
        len(spec.ops),
        len(spec.columns),
    )
    return spec


__all__ = ["mro_collect_table_spec"]
