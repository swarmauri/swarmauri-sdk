# tigrbl/v3/runtime/atoms/resolve/assemble.py
from __future__ import annotations

from typing import Any, Mapping, Optional, Dict, Tuple
import logging

from ... import events as _ev
from ...opview import opview_from_ctx, ensure_schema_in, _ensure_temp

# Runs in HANDLER phase, before pre:flush and any storage transforms.
ANCHOR = _ev.RESOLVE_VALUES  # "resolve:values"

logger = logging.getLogger("uvicorn")


def run(obj: Optional[object], ctx: Any) -> None:
    """
    resolve:assemble@resolve:values

    Purpose
    -------
    Build a normalized dict of inbound values to apply on the model (assembled_values).
    - Prefer client-provided, validated values (from wire:build_in/validate).
    - For fields that are **ABSENT** (not present in inbound), apply ColumnSpec.default_factory(ctx)
      for simple server-side defaults (non-paired path).
    - Virtual columns (storage=None) are never persisted; if present in inbound, stash them
      under temp["virtual_in"] for downstream wire/out logic.

    Inputs (conventions)
    --------------------
    - ctx.temp["in_values"] OR ctx.in_data / ctx.payload / ctx.data / ctx.body :
        dict-like or Pydantic model; used as inbound source
    - ctx.persist : bool  (writes only; non-persist ops typically prune this anchor)
    - ctx.op      : str   (verb name; optional, only for diagnostics)

    Effects
    -------
    - ctx.temp["assembled_values"] : dict[field -> value] (only persisted fields)
    - ctx.temp["virtual_in"]       : dict[field -> value] (for storage=None)
    - ctx.temp["absent_fields"]    : tuple[str, ...]      (those not in inbound)
    - ctx.temp["used_default_factory"] : tuple[str, ...]  (fields defaulted here)
    """
    # Non-persisting ops should have pruned this anchor; retain guard for safety.
    if getattr(ctx, "persist", True) is False:
        logger.debug("Skipping resolve:assemble; ctx.persist is False")
        return

    logger.debug("Running resolve:assemble")
    ov = opview_from_ctx(ctx)
    schema_in = ensure_schema_in(ctx, ov)
    inbound = _coerce_inbound(getattr(ctx, "temp", {}).get("in_values", None), ctx)

    temp = _ensure_temp(ctx)
    assembled: Dict[str, Any] = {}
    virtual_in: Dict[str, Any] = {}
    absent: list[str] = []
    used_default: list[str] = []

    # Iterate fields in a stable order
    for field in sorted(schema_in["fields"]):
        meta = schema_in["by_field"].get(field, {})
        in_enabled = meta.get("in_enabled", True)
        is_virtual = meta.get("virtual", False)

        present, value = _try_read_inbound(inbound, field)
        if present:
            if is_virtual:
                virtual_in[field] = value
                logger.debug("Captured virtual inbound %s=%s", field, value)
            elif in_enabled:
                assembled[field] = value
                logger.debug("Assembled inbound %s=%s", field, value)
            continue

        absent.append(field)
        logger.debug("Field %s absent from inbound", field)

        default_fn = meta.get("default_factory")
        if callable(default_fn) and in_enabled and not is_virtual:
            try:
                default_val = default_fn(_ctx_view(ctx))
                assembled[field] = default_val
                used_default.append(field)
                logger.debug("Applied default for field %s", field)
            except Exception:
                logger.debug("Default factory failed for field %s", field)

    # Stash results on ctx.temp
    temp["assembled_values"] = assembled
    temp["virtual_in"] = virtual_in
    temp["absent_fields"] = tuple(absent)
    temp["used_default_factory"] = tuple(used_default)
    logger.debug(
        "Assembled values: %s, virtual_in: %s, absent: %s, defaults: %s",
        assembled,
        virtual_in,
        absent,
        used_default,
    )


# ──────────────────────────────────────────────────────────────────────────────
# Internals
# ──────────────────────────────────────────────────────────────────────────────


def _coerce_inbound(candidate: Any, ctx: Any) -> Mapping[str, Any]:
    """
    Return a dict-like for inbound values.
    Priority: ctx.temp["in_values"] → ctx.in_data → ctx.payload → ctx.data → ctx.body.
    Accepts Pydantic v1/v2 models (model_dump()/dict()).
    """
    for name in ("in_values",):
        if isinstance(candidate, Mapping):
            return candidate
    # fallbacks on ctx
    for attr in ("in_data", "payload", "data", "body"):
        val = getattr(ctx, attr, None)
        if isinstance(val, Mapping):
            return val
        # Pydantic v2
        if hasattr(val, "model_dump") and callable(getattr(val, "model_dump")):
            try:
                return dict(val.model_dump())
            except Exception:
                pass
        # Pydantic v1
        if hasattr(val, "dict") and callable(getattr(val, "dict")):
            try:
                return dict(val.dict())
            except Exception:
                pass
    # default empty
    return {}


def _try_read_inbound(inbound: Mapping[str, Any], field: str) -> Tuple[bool, Any]:
    """
    Distinguish ABSENT vs present(None).
    """
    if field in inbound:
        return True, inbound.get(field, None)
    # Be tolerant to alias-style inputs (if present)
    for alt in (field.lower(), field.upper()):
        if alt in inbound:
            return True, inbound.get(alt)
    return False, None


def _ctx_view(ctx: Any) -> Dict[str, Any]:
    """
    Provide a small read-only view for default_factory functions
    without exposing the entire executor context.
    """
    view = {
        "op": getattr(ctx, "op", None),
        "persist": getattr(ctx, "persist", True),
        "temp": getattr(ctx, "temp", None),
        # optional hints the executor might set
        "tenant": getattr(ctx, "tenant", None),
        "user": getattr(ctx, "user", None),
        "now": getattr(ctx, "now", None),
    }
    return view


__all__ = ["ANCHOR", "run"]
