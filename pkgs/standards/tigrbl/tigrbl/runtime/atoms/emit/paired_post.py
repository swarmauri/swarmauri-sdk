# tigrbl/v3/runtime/atoms/emit/paired_post.py
from __future__ import annotations

from typing import Any, Dict, Mapping, MutableMapping, Optional
import logging

from ... import events as _ev

# Runs after DB flush + refresh, before out model construction.
ANCHOR = _ev.EMIT_ALIASES_POST  # "emit:aliases:post_refresh"

logger = logging.getLogger("uvicorn")


def run(obj: Optional[object], ctx: Any) -> None:
    """
    emit:paired_post@emit:aliases:post_refresh

    Purpose
    -------
    Resolve *deferred* alias emissions prepared by emit:paired_pre. For each pending
    descriptor, look up the generated raw value (typically created by resolve:paired_gen),
    copy it into a response-extras buffer, and scrub the raw from temp to enforce
    the secret-once rule.

    Inputs / Conventions
    --------------------
    - ctx.temp["emit_aliases"]["pre"] : list of descriptors from paired_pre
        { "field": str, "alias": str, "source": ("paired_values", field, "raw"), "meta": {...} }
    - ctx.temp["paired_values"]      : { field: {"raw": <value>, "meta"?: {...}, ...}, ... }
    - ctx.persist                    : bool (this anchor should be pruned when False)
    - ctx.temp["response_extras"]    : dict aggregated here for out-building

    Effects
    -------
    - Appends alias/value into ctx.temp["response_extras"][alias] = value
    - Appends a redacted audit descriptor to ctx.temp["emit_aliases"]["post"]
    - Scrubs ctx.temp["paired_values"][field]["raw"] after emission (secret-once)
    - Clears "pre" queue after processing
    """
    # Non-persisting ops should have pruned this anchor via the planner,
    # but guard anyway for robustness.
    logger.debug("Running emit:paired_post")
    if getattr(ctx, "persist", True) is False:
        logger.debug("Skipping emit:paired_post; ctx.persist is False")
        return

    temp = _ensure_temp(ctx)
    emit_buf = _ensure_emit_buf(temp)
    pre_queue = list(emit_buf.get("pre") or ())
    if not pre_queue:
        logger.debug("No deferred aliases to emit")
        return

    pv = _get_paired_values(temp)
    extras = _ensure_response_extras(temp)

    for desc in pre_queue:
        if not isinstance(desc, dict):
            logger.debug("Skipping non-dict descriptor: %s", desc)
            continue
        field = desc.get("field")
        alias = desc.get("alias")
        if not isinstance(field, str) or not isinstance(alias, str) or not field:
            logger.debug("Descriptor missing valid field/alias: %s", desc)
            continue

        value = _resolve_value_from_source(desc.get("source"), pv, field)
        if value is None:
            logger.debug("No value resolved for field %s; skipping", field)
            continue

        logger.debug("Emitting alias '%s' for field '%s'", alias, field)
        # 1) Emit into response extras (to be merged by wire/out stages)
        extras[alias] = value

        # 2) Record a minimal (redacted) audit entry; do NOT keep raw value here
        emit_buf["post"].append(
            {
                "field": field,
                "alias": alias,
                "emitted": True,
                "meta": (desc.get("meta") or {}),
            }
        )

        # 3) Enforce secret-once: scrub raw so later steps cannot re-emit accidentally
        _scrub_paired_raw(pv, field)
        logger.debug("Scrubbed paired raw for field '%s'", field)

    # All pre-emit descriptors consumed
    emit_buf["pre"].clear()
    logger.debug("Cleared pre-emit queue")


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


def _ensure_response_extras(temp: MutableMapping[str, Any]) -> Dict[str, Any]:
    extras = temp.get("response_extras")
    if not isinstance(extras, dict):
        extras = {}
        temp["response_extras"] = extras
    return extras  # type: ignore[return-value]


def _get_paired_values(temp: Mapping[str, Any]) -> Dict[str, Dict[str, Any]]:
    pv = temp.get("paired_values")
    return pv if isinstance(pv, dict) else {}


def _resolve_value_from_source(
    source: Any, pv: Mapping[str, Dict[str, Any]], field: str
) -> Optional[Any]:
    """
    Resolve the value indicated by a ('paired_values', field, 'raw')-style pointer.
    Falls back to pv[field]['raw'] when source is missing/malformed.
    """
    if isinstance(source, (tuple, list)) and len(source) == 3:
        base, fld, key = source
        if base == "paired_values" and isinstance(fld, str) and key == "raw":
            return pv.get(fld, {}).get("raw")
    # Fallback
    return pv.get(field, {}).get("raw")


def _scrub_paired_raw(pv: MutableMapping[str, Dict[str, Any]], field: str) -> None:
    entry = pv.get(field)
    if not isinstance(entry, dict):
        return
    # Remove raw, mark emitted
    entry.pop("raw", None)
    entry["emitted"] = True


__all__ = ["ANCHOR", "run"]
