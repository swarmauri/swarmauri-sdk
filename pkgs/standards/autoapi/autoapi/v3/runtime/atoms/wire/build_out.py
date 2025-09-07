# autoapi/v3/runtime/atoms/wire/build_out.py
from __future__ import annotations

from typing import Any, Dict, Mapping, MutableMapping, Optional
import logging

from ... import events as _ev

# POST_HANDLER, runs before readtime aliases and dump.
ANCHOR = _ev.OUT_BUILD  # "out:build"

logger = logging.getLogger("uvicorn")


def run(obj: Optional[object], ctx: Any) -> None:
    """
    wire:build_out@out:build

    Purpose
    -------
    Build canonical outbound values keyed by *field name* (not aliases).
    - Reads the shape from ctx.temp["schema_out"] (built by schema:collect_out).
    - Pulls values from the hydrated ORM object; tolerates executor fallbacks.
    - Computes virtual columns via ColumnSpec.read_producer / .producer if present.
    - Writes results to ctx.temp["out_values"] for wire:dump to serialize.
      (Alias extras from emit atoms live in ctx.temp["response_extras"] and are
       merged later during wire:dump.)

    Notes
    -----
    - We intentionally keep keys as canonical field names so out:masking can
      evaluate sensitivity on real fields, while alias extras remain separate.
    """
    schema_out = _schema_out(ctx)
    if not schema_out:
        logger.debug("No schema_out available; skipping wire:build_out")
        return

    logger.debug("Running wire:build_out")
    temp = _ensure_temp(ctx)
    specs: Mapping[str, Any] = getattr(ctx, "specs", {}) or {}
    _by_field: Mapping[str, Mapping[str, Any]] = schema_out.get("by_field", {})  # type: ignore[assignment]
    expose = tuple(schema_out.get("expose", ()))  # type: ignore[assignment]

    out_values: Dict[str, Any] = {}
    produced_virtuals: list[str] = []
    missing: list[str] = []

    for field in expose:
        col = specs.get(field)
        if col is None:
            logger.debug("No spec for field %s; skipping", field)
            continue

        is_virtual = getattr(col, "storage", None) is None

        if is_virtual:
            producer = _get_virtual_producer(col)
            if callable(producer):
                try:
                    out_values[field] = producer(obj, ctx)
                    produced_virtuals.append(field)
                    logger.debug("Produced virtual field %s", field)
                except Exception:
                    # Virtual read failed; leave missing for now
                    missing.append(field)
                    logger.debug("Virtual producer failed for field %s", field)
            else:
                # No producer configured; virtual field cannot be derived
                missing.append(field)
                logger.debug("No producer for virtual field %s", field)
            continue

        # persisted column: prefer attribute on the hydrated object
        value = _read_current_value(obj, ctx, field)
        if value is None:
            missing.append(field)
            logger.debug("No value available for field %s", field)
        out_values[field] = value

    # Persist results + small diagnostics
    temp["out_values"] = out_values
    if produced_virtuals:
        temp["out_virtual_produced"] = tuple(produced_virtuals)
    if missing:
        temp["out_missing"] = tuple(missing)
    logger.debug(
        "Built outbound values: %s (virtuals=%s, missing=%s)",
        out_values,
        produced_virtuals,
        missing,
    )


# ──────────────────────────────────────────────────────────────────────────────
# Internals
# ──────────────────────────────────────────────────────────────────────────────


def _ensure_temp(ctx: Any) -> MutableMapping[str, Any]:
    tmp = getattr(ctx, "temp", None)
    if not isinstance(tmp, dict):
        tmp = {}
        setattr(ctx, "temp", tmp)
    return tmp


def _schema_out(ctx: Any) -> Mapping[str, Any]:
    tmp = getattr(ctx, "temp", {})
    sch = getattr(tmp, "get", lambda *_a, **_k: None)("schema_out")  # type: ignore
    if isinstance(sch, Mapping):
        return sch
    # allow adapters to stuff schema_out directly on ctx
    sch2 = getattr(ctx, "schema_out", None)
    return sch2 if isinstance(sch2, Mapping) else {}


def _get_virtual_producer(colspec: Any):
    """
    Return a read-time producer for virtual columns (obj, ctx) -> value.
    Accepts common attribute names at either ColumnSpec or FieldSpec level.
    """
    for obj in (colspec, getattr(colspec, "field", None)):
        if obj is None:
            continue
        for name in ("read_producer", "producer", "out_producer", "compute_out"):
            fn = getattr(obj, name, None)
            if callable(fn):
                return fn
    return None


def _read_current_value(obj: Optional[object], ctx: Any, field: str) -> Optional[Any]:
    """
    Pull the current value for `field` from the most reliable source we have.
    Preference: object attribute → ctx.row/values → ctx.temp['hydrated_values'].
    """
    if obj is not None and hasattr(obj, field):
        try:
            return getattr(obj, field)
        except Exception:
            pass

    for name in ("row", "values", "current_values"):
        src = getattr(ctx, name, None)
        if isinstance(src, Mapping) and field in src:
            return src.get(field)

    hv = getattr(getattr(ctx, "temp", {}), "get", lambda *a, **k: None)(
        "hydrated_values"
    )  # type: ignore
    if isinstance(hv, Mapping):
        return hv.get(field)

    return None


__all__ = ["ANCHOR", "run"]
