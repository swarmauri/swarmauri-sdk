# autoapi/v3/runtime/atoms/emit/paired_pre.py
from __future__ import annotations

from typing import Any, Dict, Mapping, MutableMapping, Optional

from ... import events as _ev

# This atom runs before the flush, after values have been assembled/generated.
ANCHOR = _ev.EMIT_ALIASES_PRE  # "emit:aliases:pre_flush"


def run(obj: Optional[object], ctx: Any) -> None:
    """
    emit:paired_pre@emit:aliases:pre_flush

    Purpose
    -------
    Prepare *deferred* alias emissions for "paired" values (e.g., secret-once raw tokens)
    that were generated earlier (typically by resolve:paired_gen) and stored on
    ctx.temp["paired_values"] = { <field>: {"raw": <value>, "alias"?: <str>, "meta"?: {...}} }.

    This atom:
      - Ensures ctx.temp["emit_aliases"] = {"pre": [], "post": [], "read": []}
      - Scans paired_values and pushes *deferred* emit specs into "pre"
        so that emit:paired_post can resolve them after flush/refresh and
        attach to the outbound payload/extras safely.

    Contracts / Conventions
    -----------------------
    - ctx.temp is a dict-like scratch space shared across atoms.
    - ctx.specs is a mapping field_name -> ColumnSpec (optional; used to infer alias names).
    - paired_values entries may provide an explicit "alias"; otherwise we infer one
      using ColumnSpec IO/Field hints; if nothing is available, we default to the field name.
    - This atom is a no-op when there are no paired values.

    It is safe to call multiple times; it only appends idempotent descriptors.
    """
    # Non-persisting ops should have pruned this anchor via the planner,
    # but guard anyway for robustness.
    if getattr(ctx, "persist", True) is False:
        return

    temp = _ensure_temp(ctx)
    emit_buf = _ensure_emit_buf(temp)
    paired = _get_paired_values(temp)

    if not paired:
        return

    specs: Mapping[str, Any] = getattr(ctx, "specs", {}) or {}

    for field, entry in paired.items():
        if not isinstance(entry, dict):
            continue
        if "raw" not in entry:
            # nothing to emit
            continue

        alias = (
            entry.get("alias")
            or _infer_alias_from_spec(field, specs.get(field))
            or field
        )

        # Record a *deferred* emission descriptor; emit:paired_post will resolve it.
        emit_buf["pre"].append(
            {
                "field": field,
                "alias": alias,
                "source": ("paired_values", field, "raw"),
                "meta": entry.get("meta") or {},
            }
        )


# ──────────────────────────────────────────────────────────────────────────────
# Internals
# ──────────────────────────────────────────────────────────────────────────────


def _ensure_temp(ctx: Any) -> MutableMapping[str, Any]:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    return temp


def _ensure_emit_buf(temp: MutableMapping[str, Any]) -> Dict[str, list]:
    buf = temp.get("emit_aliases")
    if not isinstance(buf, dict):
        buf = {"pre": [], "post": [], "read": []}
        temp["emit_aliases"] = buf
    else:
        buf.setdefault("pre", [])
        buf.setdefault("post", [])
        buf.setdefault("read", [])
    return buf  # type: ignore[return-value]


def _get_paired_values(temp: Mapping[str, Any]) -> Mapping[str, Dict[str, Any]]:
    pv = temp.get("paired_values")
    return pv if isinstance(pv, dict) else {}


def _infer_alias_from_spec(field: str, colspec: Any) -> Optional[str]:
    """
    Best-effort alias inference from ColumnSpec / IOSpec / FieldSpec.
    We try a few conventional attribute names without taking a hard dependency
    on any one spec layout. If nothing is found, return None.
    """
    if colspec is None:
        return None

    # Column-level direct hints
    for name in ("emit_alias", "response_alias", "alias_out", "out_alias"):
        val = getattr(colspec, name, None)
        if isinstance(val, str) and val:
            return val

    # IO-level hints
    io = getattr(colspec, "io", None)
    if io is not None:
        paired = getattr(io, "_paired", None)
        if paired is not None and isinstance(getattr(paired, "alias", None), str):
            if paired.alias:
                return paired.alias
        for name in ("emit_alias", "response_alias", "alias_out", "out_alias"):
            val = getattr(io, name, None)
            if isinstance(val, str) and val:
                return val

    # Field-level hints
    fld = getattr(colspec, "field", None)
    if fld is not None:
        for name in ("emit_alias", "response_alias", "alias_out", "out_alias"):
            val = getattr(fld, name, None)
            if isinstance(val, str) and val:
                return val

    return None


__all__ = ["ANCHOR", "run"]
