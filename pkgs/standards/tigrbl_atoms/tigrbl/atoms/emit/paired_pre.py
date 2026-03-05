# tigrbl/v3/runtime/atoms/emit/paired_pre.py
from __future__ import annotations

from typing import Any, Dict, Mapping, MutableMapping, Optional
import logging

from ... import events as _ev
from ...opview import opview_from_ctx, _ensure_temp

# This atom runs before the flush, after values have been assembled/generated.
ANCHOR = _ev.EMIT_ALIASES_PRE  # "emit:aliases:pre_flush"

logger = logging.getLogger("uvicorn")


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
    - paired_values entries may provide an explicit "alias"; otherwise we infer one
      using OpView metadata; if nothing is available, we default to the field name.
    - This atom is a no-op when there are no paired values.

    It is safe to call multiple times; it only appends idempotent descriptors.
    """
    # Non-persisting ops should have pruned this anchor via the planner,
    # but guard anyway for robustness.
    logger.debug("Running emit:paired_pre")
    if getattr(ctx, "persist", True) is False:
        logger.debug("Skipping emit:paired_pre; ctx.persist is False")
        return

    temp = _ensure_temp(ctx)
    emit_buf = _ensure_emit_buf(temp)
    paired = _get_paired_values(temp)

    if not paired:
        logger.debug("No paired values found; nothing to schedule")
        return

    ov = opview_from_ctx(ctx)

    for field, entry in paired.items():
        if not isinstance(entry, dict):
            logger.debug(
                "Skipping non-dict paired entry for field %s: %s", field, entry
            )
            continue
        if "raw" not in entry:
            logger.debug("Paired entry for field %s lacks raw value", field)
            # nothing to emit
            continue

        desc = ov.paired_index.get(field, {})
        alias = entry.get("alias") or desc.get("alias") or field

        # Record a *deferred* emission descriptor; emit:paired_post will resolve it.
        emit_buf["pre"].append(
            {
                "field": field,
                "alias": alias,
                "source": ("paired_values", field, "raw"),
                "meta": entry.get("meta") or {},
            }
        )
        logger.debug("Queued deferred alias '%s' for field '%s'", alias, field)


# ──────────────────────────────────────────────────────────────────────────────
# Internals
# ──────────────────────────────────────────────────────────────────────────────


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


__all__ = ["ANCHOR", "run"]
