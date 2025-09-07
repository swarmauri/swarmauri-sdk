# autoapi/v3/runtime/atoms/schema/collect_out.py
from __future__ import annotations

from typing import Any, Dict, Mapping, MutableMapping, Optional
import logging

from ... import events as _ev
from ...kernel import get_cached_specs

# Runs late in POST_HANDLER, before out model build and dumping.
ANCHOR = _ev.SCHEMA_COLLECT_OUT  # "schema:collect_out"

logger = logging.getLogger("uvicorn")


def run(obj: Optional[object], ctx: Any) -> None:
    """
    schema:collect_out@schema:collect_out

    Purpose
    -------
    Collect a minimal, vendor-neutral description of the outbound schema so
    wire:build_out (and downstream atoms) can build/shape the response model.

    It:
      - Respects IO exposure flags (default allow out).
      - Captures virtual vs persisted, nullability hints, type hints for docs.
      - Notes alias names intended for output (response/emit aliases).
      - Surfaces sensitivity/masking hints (sensitive/redact/redact_last).

    Inputs (conventions)
    --------------------
    - ctx.specs : Mapping[str, ColumnSpec]
    - ctx.op    : Optional[str] (for policy hooks, currently informational)

    Effects
    -------
    - ctx.temp["schema_out"] = {
        "fields": [
          {
            "name": str,
            "virtual": bool,
            "nullable": Optional[bool],
            "py_type": Optional[str],
            "alias_out": Optional[str],
            "sensitive": bool,
            "redact_last": Optional[int|bool],
            "max_length": Optional[int],
          }, ...
        ],
        "expose": tuple[str, ...],         # field names that appear in the out model
        "by_field": {name: <entry>, ...},  # convenience lookup
        "aliases": {field: alias, ...},    # known static aliases (spec-declared)
        "order": tuple[str, ...],          # stable field order for model build
      }
    """
    logger.debug("Running schema:collect_out")
    model = (
        getattr(ctx, "model", None)
        or getattr(ctx, "Model", None)
        or type(getattr(ctx, "obj", None))
    )
    specs: Mapping[str, Any] = getattr(ctx, "specs", None) or (
        get_cached_specs(model) if model else {}
    )
    if not specs:
        msg = "ctx.specs is required for schema:collect_out"
        logger.debug(msg)
        raise RuntimeError(msg)

    temp = _ensure_temp(ctx)
    if "schema_out" in temp:
        logger.debug("schema_out already populated; skipping")
        return

    fields_sorted = sorted(specs.keys())
    entries: list[Dict[str, Any]] = []
    by_field: Dict[str, Dict[str, Any]] = {}
    aliases: Dict[str, str] = {}
    expose: list[str] = []

    for field in fields_sorted:
        col = specs[field]
        storage = getattr(col, "storage", None)
        io = getattr(col, "io", None)
        f = getattr(col, "field", None)

        out_enabled = _bool_attr(io, "out", "allow_out", "expose_out", default=True)
        if not out_enabled:
            logger.debug("Field %s excluded from outbound schema", field)
            # Not exposed on output — skip entirely for outbound schema
            continue

        is_virtual = storage is None
        nullable = getattr(storage, "nullable", None) if storage is not None else None
        py_type = _py_type_str(f)

        alias_out = _infer_out_alias(field, col)
        if alias_out:
            aliases[field] = alias_out
            logger.debug("Field %s has alias_out %s", field, alias_out)

        sensitive, redact_last = _sensitivity(col)
        max_len = _max_len(col)

        entry = {
            "name": field,
            "virtual": is_virtual,
            "nullable": nullable
            if nullable is not None
            else (None if is_virtual else True),
            "py_type": py_type,
            "alias_out": alias_out,
            "sensitive": sensitive,
            "redact_last": redact_last,
            "max_length": max_len,
        }
        entries.append(entry)
        by_field[field] = entry
        expose.append(field)
        logger.debug(
            "Collected outbound field %s (virtual=%s, sensitive=%s)",
            field,
            is_virtual,
            sensitive,
        )

    schema_out = {
        "fields": entries,
        "expose": tuple(expose),
        "by_field": by_field,
        "aliases": aliases,
        "order": tuple(e["name"] for e in entries),
    }
    temp["schema_out"] = schema_out
    logger.debug("schema_out populated with %d fields", len(entries))


# ──────────────────────────────────────────────────────────────────────────────
# Internals (tolerant to spec shapes)
# ──────────────────────────────────────────────────────────────────────────────


def _ensure_temp(ctx: Any) -> MutableMapping[str, Any]:
    tmp = getattr(ctx, "temp", None)
    if not isinstance(tmp, dict):
        tmp = {}
        setattr(ctx, "temp", tmp)
    return tmp


def _bool_attr(obj: Any, *names: str, default: bool) -> bool:
    for n in names:
        if hasattr(obj, n):
            v = getattr(obj, n)
            if isinstance(v, bool):
                return v
    return default


def _py_type_str(field_spec: Any) -> Optional[str]:
    """
    Best-effort Python type name for docs: FieldSpec.py_type or similar.
    Falls back to None if not available.
    """
    if field_spec is None:
        return None
    for name in ("py_type", "python_type"):
        t = getattr(field_spec, name, None)
        if t is None:
            continue
        try:
            return getattr(t, "__name__", None) or str(t)
        except Exception:
            return str(t)
    return None


def _infer_out_alias(field: str, colspec: Any) -> Optional[str]:
    """
    Outbound alias inference (author-supplied). We look for common names.
    """
    for obj in (colspec, getattr(colspec, "io", None), getattr(colspec, "field", None)):
        if obj is None:
            continue
        for name in ("alias_out", "response_alias", "emit_alias", "out_alias", "alias"):
            val = getattr(obj, name, None)
            if isinstance(val, str) and val:
                return val
    return None


def _sensitivity(colspec: Any) -> tuple[bool, Optional[int | bool]]:
    """
    Extract sensitivity/masking indicators. `redact_last` may be bool (use default 4)
    or an int for number of trailing characters to keep.
    """
    sensitive = False
    redact_last: Optional[int | bool] = None

    def _probe(obj: Any) -> None:
        nonlocal sensitive, redact_last
        if obj is None:
            return
        if getattr(obj, "sensitive", False) or getattr(obj, "redact", False):
            sensitive = True
        rl = getattr(obj, "redact_last", None)
        if isinstance(rl, bool):
            if rl:
                sensitive = True
                redact_last = True  # signal to use default window downstream
        elif isinstance(rl, int) and rl > 0:
            sensitive = True
            redact_last = rl

    _probe(colspec)
    _probe(getattr(colspec, "field", None))

    return sensitive, redact_last


def _max_len(colspec: Any) -> Optional[int]:
    """
    Detect a maximum length hint for outbound strings (ColumnSpec/FieldSpec/IOSpec/Storage).
    """
    for obj in (
        colspec,
        getattr(colspec, "field", None),
        getattr(colspec, "io", None),
        getattr(colspec, "storage", None),
    ):
        if obj is None:
            continue
        for name in ("max_length", "max_len", "length", "size"):
            v = getattr(obj, name, None)
            if isinstance(v, int) and v > 0:
                return v
    return None


__all__ = ["ANCHOR", "run"]
