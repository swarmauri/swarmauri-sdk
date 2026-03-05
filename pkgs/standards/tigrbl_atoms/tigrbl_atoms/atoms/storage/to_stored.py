# tigrbl/v3/runtime/atoms/storage/to_stored.py
from __future__ import annotations

import logging
from typing import Any, Dict, Mapping, MutableMapping, Optional

from ... import events as _ev
from ...opview import opview_from_ctx, ensure_schema_in, _ensure_temp

# Runs right before the handler flushes to the DB.
ANCHOR = _ev.PRE_FLUSH  # "pre:flush"

logger = logging.getLogger("uvicorn")


def run(obj: Optional[object], ctx: Any) -> None:
    """
    storage:to_stored@pre:flush

    Transform inbound values into their persisted representation.

    - For *paired/secret-once* columns, derive the stored value from the prepared raw
      and assign it to BOTH ctx.temp["assembled_values"][field] AND the ORM object.
      Also handles a fallback when 'persist_from_paired' wasn't queued but a paired raw
      exists (planner tolerance).
    - Otherwise, apply an optional per-column inbound→stored transform and mirror the
      transformed value onto the ORM instance.

    On failure to derive for paired, raise ValueError (mapped by higher layers) to
    avoid leaking DB IntegrityErrors.
    """
    logger.debug("Running storage:to_stored")
    if getattr(ctx, "persist", True) is False:
        logger.debug("Skipping storage:to_stored; ctx.persist is False")
        return

    ov = opview_from_ctx(ctx)
    schema_in = ensure_schema_in(ctx, ov)
    temp = _ensure_temp(ctx)
    assembled = _ensure_dict(temp, "assembled_values")
    paired_values = _ensure_dict(temp, "paired_values")
    pf_paired = _ensure_dict(temp, "persist_from_paired")
    slog = _ensure_list(temp, "storage_log")
    serr = _ensure_list(temp, "storage_errors")

    # Prefer explicit obj (hydrated instance), else ctx.model if adapter provided it
    target_obj = obj or getattr(ctx, "model", None)

    # Ensure paired fields are considered even when absent from inbound schema.
    # schema_in["fields"] may omit columns like "digest" that generate their
    # values server-side via IO(...).paired. To derive their stored values, merge
    # the explicit schema fields with the paired index keys.
    all_fields = set(schema_in["fields"]) | set(ov.paired_index.keys())

    for field in sorted(all_fields):
        if field in ov.paired_index:
            if field in pf_paired or field in paired_values:
                raw = None
                if field in pf_paired:
                    raw = _resolve_from_pointer(
                        pf_paired[field].get("source"), paired_values, field
                    )
                if raw is None:
                    raw = paired_values.get(field, {}).get("raw")
                if raw is None:
                    serr.append({"field": field, "error": "missing_paired_raw"})
                    logger.debug("Missing paired raw for field %s", field)
                    raise RuntimeError(f"paired_raw_missing:{field}")
                deriver = ov.paired_index[field].get("store")
                try:
                    stored = deriver(raw, ctx) if callable(deriver) else raw
                except Exception as e:
                    serr.append(
                        {"field": field, "error": f"deriver_failed:{type(e).__name__}"}
                    )
                    logger.debug("Deriver failed for field %s: %s", field, e)
                    raise
                assembled[field] = stored
                _assign_to_model(target_obj, field, stored)
                slog.append({"field": field, "action": "derived_from_paired"})
                logger.debug("Derived stored value for paired field %s", field)
                continue

            nullable = schema_in["by_field"].get(field, {}).get("nullable", True)
            if (
                not nullable
                and field not in assembled
                and not _has_attr_with_value(target_obj, field)
            ):
                serr.append({"field": field, "error": "paired_missing_before_flush"})
                logger.debug("Paired field %s missing before flush", field)
                raise RuntimeError(f"paired_missing_before_flush:{field}")
            continue

        if field in assembled:
            transform = ov.to_stored_transforms.get(field)
            if transform is None:
                logger.debug("No transform for field %s; using assembled value", field)
                _assign_to_model(target_obj, field, assembled[field])
                continue
            try:
                stored_val = transform(assembled[field], ctx)
                assembled[field] = stored_val
                _assign_to_model(target_obj, field, stored_val)
                slog.append({"field": field, "action": "transformed"})
                logger.debug("Transformed field %s", field)
            except Exception as e:
                serr.append(
                    {"field": field, "error": f"transform_failed:{type(e).__name__}"}
                )
                logger.debug("Transform failed for field %s: %s", field, e)
                raise


# ──────────────────────────────────────────────────────────────────────────────
# Internals (tolerant to spec shapes)
# ──────────────────────────────────────────────────────────────────────────────


def _assign_to_model(target: Optional[object], field: str, value: Any) -> None:
    """Safely assign value onto the hydrated ORM object so SQLAlchemy flushes it."""
    if target is None:
        return
    try:
        setattr(target, field, value)
    except Exception:
        # Non-fatal: some adapters may not expose an assignable object here.
        pass


def _has_attr_with_value(target: Optional[object], field: str) -> bool:
    if target is None or not hasattr(target, field):
        return False
    try:
        return getattr(target, field) is not None
    except Exception:
        return False


def _ensure_dict(temp: MutableMapping[str, Any], key: str) -> Dict[str, Any]:
    d = temp.get(key)
    if not isinstance(d, dict):
        d = {}
        temp[key] = d
    return d  # type: ignore[return-value]


def _ensure_list(temp: MutableMapping[str, Any], key: str) -> list:
    lst = temp.get(key)
    if not isinstance(lst, list):
        lst = []
        temp[key] = lst
    return lst  # type: ignore[return-value]


def _resolve_from_pointer(
    source: Any, pv: Mapping[str, Dict[str, Any]], field: str
) -> Optional[Any]:
    """Resolve ('paired_values', field, 'raw') pointer, with fallback to pv[field]['raw']."""
    if isinstance(source, (tuple, list)) and len(source) == 3:
        base, fld, key = source
        if base == "paired_values" and isinstance(fld, str) and key == "raw":
            return pv.get(fld, {}).get("raw")
    return pv.get(field, {}).get("raw")


__all__ = ["ANCHOR", "run"]
