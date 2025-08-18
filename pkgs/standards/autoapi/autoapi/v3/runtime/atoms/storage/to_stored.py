# autoapi/v3/runtime/atoms/storage/to_stored.py
from __future__ import annotations

import hashlib
from typing import Any, Callable, Dict, Mapping, MutableMapping, Optional

from ... import events as _ev

# Runs right before the handler flushes to the DB.
ANCHOR = _ev.PRE_FLUSH  # "pre:flush"


def run(obj: Optional[object], ctx: Any) -> None:
    """
    storage:to_stored@pre:flush

    Purpose
    -------
    Transform inbound values into their persisted representation.
      - For *paired/secret-once* columns: derive the stored value from the
        prepared raw in ctx.temp["paired_values"][field]["raw"].
      - Otherwise: apply an optional per-column `to_stored(value, ctx)` transform.

    Inputs / Conventions
    --------------------
    - ctx.persist : bool
    - ctx.specs   : {field -> ColumnSpec}
    - ctx.temp["assembled_values"]     : dict[field -> value]       (from resolve:assemble)
    - ctx.temp["paired_values"]        : {field: {"raw": str, ...}} (from resolve:paired_gen)
    - ctx.temp["persist_from_paired"]  : {field: {"source": ("paired_values", field, "raw")}}
    - Optional author callables on ColumnSpec / FieldSpec:
        - to_stored(value, ctx)                 → Any
        - storage_transform(value, ctx)         → Any
        - transform_in(value, ctx)              → Any
        - derive_from_raw(raw, ctx)             → Any
        - persist_deriver(raw, ctx)             → Any
        - digester(raw, ctx)                    → Any
        - hasher(raw, ctx)                      → Any
      (first match wins per category)

    Effects
    -------
    - Mutates ctx.temp["assembled_values"][field] with the stored form.
    - Appends diagnostic entries to ctx.temp["storage_log"].
    - On failure to derive for paired columns, raises ValueError (mapped by higher layers).
    """
    if getattr(ctx, "persist", True) is False:
        return

    specs: Mapping[str, Any] = getattr(ctx, "specs", {}) or {}
    if not specs:
        return

    temp = _ensure_temp(ctx)
    assembled = _ensure_dict(temp, "assembled_values")
    paired_values = _ensure_dict(temp, "paired_values")
    pf_paired = _ensure_dict(temp, "persist_from_paired")
    slog = _ensure_list(temp, "storage_log")
    serr = _ensure_list(temp, "storage_errors")

    for field in sorted(specs.keys()):
        col = specs[field]

        # 1) Derive from paired raw when requested
        if field in pf_paired:
            raw = _resolve_from_pointer(pf_paired[field].get("source"), paired_values, field)
            if raw is None:
                serr.append({"field": field, "error": "missing_paired_raw"})
                raise ValueError(f"storage.to_stored: missing paired raw for {field!r}")

            deriver = _get_deriver(col)
            try:
                stored = deriver(raw, ctx)
            except Exception as e:
                serr.append({"field": field, "error": f"deriver_failed:{type(e).__name__}"})
                raise

            assembled[field] = stored
            slog.append({"field": field, "action": "derived_from_paired"})
            continue  # paired derivation wins even if an inbound value existed

        # 2) Apply general inbound→stored transform if provided and value is present
        if field in assembled:
            transform = _get_transform(col)
            if transform is None:
                # nothing to do
                continue
            try:
                assembled[field] = transform(assembled[field], ctx)
                slog.append({"field": field, "action": "transformed"})
            except Exception as e:
                serr.append({"field": field, "error": f"transform_failed:{type(e).__name__}"})
                raise


# ──────────────────────────────────────────────────────────────────────────────
# Internals (tolerant to spec shapes)
# ──────────────────────────────────────────────────────────────────────────────

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

def _resolve_from_pointer(source: Any, pv: Mapping[str, Dict[str, Any]], field: str) -> Optional[Any]:
    """
    Resolve ('paired_values', field, 'raw') style pointer, with fallback to pv[field]['raw'].
    """
    if isinstance(source, (tuple, list)) and len(source) == 3:
        base, fld, key = source
        if base == "paired_values" and isinstance(fld, str) and key == "raw":
            return pv.get(fld, {}).get("raw")
    return pv.get(field, {}).get("raw")

# — transforms — #

def _get_transform(colspec: Any) -> Optional[Callable[[Any, Any], Any]]:
    """
    Return a callable(value, ctx) that converts inbound → stored.
    Checks common names on ColumnSpec then FieldSpec.
    """
    for obj in (colspec, getattr(colspec, "field", None)):
        if obj is None:
            continue
        for name in ("to_stored", "storage_transform", "transform_in", "pre_flush"):
            fn = getattr(obj, name, None)
            if callable(fn):
                return fn
    return None

def _get_deriver(colspec: Any) -> Callable[[Any, Any], Any]:
    """
    Return a callable(raw, ctx) that derives stored from paired raw.
    If none provided, fall back to a SHA-256 hex digester with optional pepper/salt.
    """
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
    """
    Probe for pepper/salt hints on ColumnSpec / FieldSpec / StorageSpec.
    Names are intentionally broad to avoid tight coupling.
    """
    pepper = None
    salt = None
    for obj in (colspec, getattr(colspec, "field", None), getattr(colspec, "storage", None)):
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
