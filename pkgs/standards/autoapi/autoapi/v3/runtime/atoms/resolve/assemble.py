# autoapi/v3/runtime/atoms/resolve/assemble.py
from __future__ import annotations

from typing import Any, Mapping, MutableMapping, Optional, Dict, Tuple

from ... import events as _ev

# Runs in HANDLER phase, before pre:flush and any storage transforms.
ANCHOR = _ev.RESOLVE_VALUES  # "resolve:values"


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
    - ctx.specs : mapping field_name -> ColumnSpec
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
        return

    specs: Mapping[str, Any] = getattr(ctx, "specs", {}) or {}
    if not specs:
        return

    inbound = _coerce_inbound(getattr(ctx, "temp", {}).get("in_values", None), ctx)

    temp = _ensure_temp(ctx)
    assembled: Dict[str, Any] = {}
    virtual_in: Dict[str, Any] = {}
    absent: list[str] = []
    used_default: list[str] = []

    # Iterate fields in a stable order
    for field in sorted(specs.keys()):
        col = specs[field]
        io = getattr(col, "io", None)

        # honor IO inbound exposure; default True when unspecified
        in_enabled = _bool_attr(io, "in_", "allow_in", "expose_in", default=True)

        # If inbound value is present, prefer it
        present, value = _try_read_inbound(inbound, field)
        if present:
            if _is_virtual(col):
                virtual_in[field] = value
            elif in_enabled:
                assembled[field] = value
            # if not in_enabled, ignore inbound quietly
            continue

        # Not present in inbound → ABSENT semantics
        absent.append(field)

        # Apply server-side default if provided and inbound is ABSENT.
        default_fn = getattr(col, "default_factory", None)
        if callable(default_fn) and in_enabled and not _is_virtual(col):
            try:
                default_val = default_fn(_ctx_view(ctx))
                assembled[field] = default_val
                used_default.append(field)
            except Exception:
                # Be conservative: do not fail the request here; leave field absent
                # Handler/DB defaults may still populate via server_default/RETURNING.
                pass

    # Stash results on ctx.temp
    temp["assembled_values"] = assembled
    temp["virtual_in"] = virtual_in
    temp["absent_fields"] = tuple(absent)
    temp["used_default_factory"] = tuple(used_default)


# ──────────────────────────────────────────────────────────────────────────────
# Internals
# ──────────────────────────────────────────────────────────────────────────────


def _ensure_temp(ctx: Any) -> MutableMapping[str, Any]:
    tmp = getattr(ctx, "temp", None)
    if not isinstance(tmp, dict):
        tmp = {}
        setattr(ctx, "temp", tmp)
    return tmp


def _is_virtual(colspec: Any) -> bool:
    """Storage-less columns are virtual (wire-only)."""
    return getattr(colspec, "storage", None) is None


def _bool_attr(obj: Any, *names: str, default: bool) -> bool:
    for n in names:
        if hasattr(obj, n):
            v = getattr(obj, n)
            if isinstance(v, bool):
                return v
    return default


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
        "specs": getattr(ctx, "specs", None),
        "temp": getattr(ctx, "temp", None),
        # optional hints the executor might set
        "tenant": getattr(ctx, "tenant", None),
        "user": getattr(ctx, "user", None),
        "now": getattr(ctx, "now", None),
    }
    return view


__all__ = ["ANCHOR", "run"]
