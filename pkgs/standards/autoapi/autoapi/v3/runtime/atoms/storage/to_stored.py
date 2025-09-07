# autoapi/v3/runtime/atoms/storage/to_stored.py
from __future__ import annotations

import hashlib
import logging
from typing import Any, Callable, Dict, Mapping, MutableMapping, Optional

from ... import events as _ev

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

    specs: Mapping[str, Any] = getattr(ctx, "specs", {}) or {}
    if not specs:
        logger.debug("No specs provided; skipping")
        return

    temp = _ensure_temp(ctx)
    assembled = _ensure_dict(temp, "assembled_values")
    paired_values = _ensure_dict(temp, "paired_values")
    pf_paired = _ensure_dict(temp, "persist_from_paired")
    slog = _ensure_list(temp, "storage_log")
    serr = _ensure_list(temp, "storage_errors")

    # Prefer explicit obj (hydrated instance), else ctx.model if adapter provided it
    target_obj = obj or getattr(ctx, "model", None)

    for field in sorted(specs.keys()):
        col = specs[field]
        io = getattr(col, "io", None)
        is_paired = getattr(getattr(io, "_paired", None), "store", None) is not None

        # ── 1) Paired derivation (primary path) ────────────────────────────────
        if field in pf_paired or (is_paired and field in paired_values):
            # Prefer pointer; else fallback to direct paired_values lookup
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
                raise ValueError(f"storage.to_stored: missing paired raw for {field!r}")

            deriver = _get_deriver(col)
            try:
                stored = deriver(raw, ctx)
            except Exception as e:
                serr.append(
                    {"field": field, "error": f"deriver_failed:{type(e).__name__}"}
                )
                logger.debug("Deriver failed for field %s: %s", field, e)
                raise

            # Stage for DB write and ensure ORM object reflects the same value
            assembled[field] = stored
            _assign_to_model(target_obj, field, stored)
            slog.append({"field": field, "action": "derived_from_paired"})
            logger.debug("Derived stored value for paired field %s", field)
            continue

        # ── 2) Generic inbound→stored transform ───────────────────────────────
        if field in assembled:
            transform = _get_transform(col)
            if transform is None:
                logger.debug("No transform for field %s; using assembled value", field)
                # Keep ORM object in sync with the inbound (already assembled) value
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

        # ── 3) Safety: non-nullable paired with no value → early failure ──────
        # If column is paired and storage.nullable is False, ensure we don't flush None.
        if is_paired and not _nullable(col):
            # If neither assembled nor ORM has a value at this point, fail clearly.
            if (field not in assembled) and (
                not _has_attr_with_value(target_obj, field)
            ):
                serr.append({"field": field, "error": "paired_missing_before_flush"})
                logger.debug("Paired field %s missing before flush", field)
                raise ValueError(
                    f"storage.to_stored: paired field {field!r} has no stored value before flush."
                )


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


def _nullable(colspec: Any) -> bool:
    s = getattr(colspec, "storage", None)
    return True if s is None else bool(getattr(s, "nullable", True))


def _ensure_temp(ctx: Any) -> MutableMapping[str, Any]:
    tmp = getattr(ctx, "temp", None)
    if not isinstance(tmp, dict):
        tmp = {}
        setattr(ctx, "temp", tmp)
    return tmp


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


def _get_transform(colspec: Any) -> Optional[Callable[[Any, Any], Any]]:
    """Return a callable(value, ctx) converting inbound → stored (Column/Field/Storage)."""
    for obj in (
        colspec,
        getattr(colspec, "field", None),
        getattr(colspec, "storage", None),
    ):
        if obj is None:
            continue
        trans = getattr(obj, "transform", None)
        if trans is not None:
            fn = getattr(trans, "to_stored", None)
            if callable(fn):
                return fn
        for name in ("to_stored", "storage_transform", "transform_in", "pre_flush"):
            fn = getattr(obj, name, None)
            if callable(fn):
                return fn
    return None


def _get_deriver(colspec: Any) -> Callable[[Any, Any], Any]:
    """
    Return a callable(raw, ctx) deriving stored from paired raw.
    If none provided, fall back to SHA-256 hex with optional pepper/salt.
    """
    io = getattr(colspec, "io", None)
    paired = getattr(io, "_paired", None)
    if paired is not None and callable(getattr(paired, "store", None)):
        return paired.store
    for obj in (colspec, getattr(colspec, "field", None)):
        if obj is None:
            continue
        for name in ("derive_from_raw", "persist_deriver", "digester", "hasher"):
            fn = getattr(obj, name, None)
            if callable(fn):
                return fn
    # fallback: digest with pepper/salt if present
    pepper, salt = _pepper_salt(colspec)

    def _fallback(raw: Any, _ctx: Any) -> str:
        data = _coerce_bytes(raw)
        if pepper:
            data = _coerce_bytes(pepper) + data
        if salt:
            data = data + _coerce_bytes(salt)
        return hashlib.sha256(data).hexdigest()

    return _fallback


def _pepper_salt(colspec: Any) -> tuple[Optional[str], Optional[str]]:
    """Probe for pepper/salt hints on ColumnSpec / FieldSpec / StorageSpec."""
    pepper = None
    salt = None
    for obj in (
        colspec,
        getattr(colspec, "field", None),
        getattr(colspec, "storage", None),
    ):
        if obj is None:
            continue
        for name in ("hash_pepper", "pepper", "secret_pepper"):
            val = getattr(obj, name, None)
            if isinstance(val, str) and val:
                pepper = pepper or val
        for name in ("salt", "hash_salt", "secret_salt"):
            val = getattr(obj, name, None)
            if isinstance(val, str) and val:
                salt = salt or val
    return pepper, salt


def _coerce_bytes(val: Any) -> bytes:
    if isinstance(val, bytes):
        return val
    if isinstance(val, bytearray):
        return bytes(val)
    try:
        return str(val).encode("utf-8")
    except Exception:
        # last resort: repr
        return repr(val).encode("utf-8")


__all__ = ["ANCHOR", "run"]
