# tigrbl/v3/runtime/atoms/wire/validate_in.py
from __future__ import annotations

import datetime as _dt
import decimal as _dc
import uuid as _uuid
import logging
from typing import Any, Dict, Mapping, Optional, Tuple

from fastapi import HTTPException, status as _status

from ... import events as _ev
from ...opview import opview_from_ctx, ensure_schema_in, _ensure_temp

# PRE_HANDLER, runs after wire:build_in
ANCHOR = _ev.IN_VALIDATE  # "in:validate"

logger = logging.getLogger("uvicorn")


def run(obj: Optional[object], ctx: Any) -> None:
    """
    wire:validate_in@in:validate

    Validates the normalized inbound payload (ctx.temp["in_values"]) using the
    schema collected by schema:collect_in plus tolerant signals from ColumnSpec.

    What it checks
    --------------
    - Required fields are present (ABSENT → error; present(None) is a separate check)
    - Nullability (value is None while column is non-nullable → error)
    - Lightweight type conformance (optional coercion if enabled)
    - String max_length (when available)
    - Author validators (validate_in / in_validator / validator_in on ColumnSpec/FieldSpec/IOSpec)

    Effects
    -------
    - Mutates ctx.temp["in_values"] with any successful coercions/validator returns
    - Writes diagnostics to:
        ctx.temp["in_errors"] : list of {field, code, message}
        ctx.temp["in_invalid"] : bool
        ctx.temp["in_coerced"] : tuple of coerced field names (if any)
    - Raises HTTPException(422) if any validation errors are found
    """
    logger.debug("Running wire:validate_in")
    temp = _ensure_temp(ctx)
    ov = opview_from_ctx(ctx)
    schema_in = ensure_schema_in(ctx, ov)

    in_values: Dict[str, Any] = dict(temp.get("in_values") or {})
    by_field: Mapping[str, Mapping[str, Any]] = schema_in.get("by_field", {})  # type: ignore[assignment]
    required: Tuple[str, ...] = tuple(schema_in.get("required", ()))  # type: ignore[assignment]

    errors: list[Dict[str, Any]] = []
    coerced: list[str] = []

    # 1) Required presence (ABSENT → error)
    for name in required:
        if name not in in_values:
            logger.debug("Required field %s missing", name)
            errors.append(
                _err(name, "required", "Field is required but was not provided.")
            )

    # 2) Per-field validation
    for name, value in list(in_values.items()):
        entry = by_field.get(name) or {}

        # Nullability
        nullable = entry.get("nullable", None)
        if value is None and nullable is False:
            logger.debug("Field %s is null but not nullable", name)
            errors.append(
                _err(name, "null_not_allowed", "Null is not allowed for this field.")
            )
            continue  # skip further checks for this field

        # Type (optionally coerce)
        target_type = entry.get("py_type")
        if value is not None and isinstance(target_type, type):
            allow_coerce = bool(entry.get("coerce", True))
            ok, new_val, msg = _coerce_if_needed(value, target_type, allow=allow_coerce)
            if not ok:
                logger.debug("Type mismatch for field %s", name)
                errors.append(
                    _err(
                        name,
                        "type_mismatch",
                        msg or f"Expected {_type_name(target_type)}.",
                    )
                )
                continue
            if new_val is not value:
                in_values[name] = new_val
                coerced.append(name)

        # Max length (strings)
        max_len = entry.get("max_length", None)
        if (
            isinstance(max_len, int)
            and max_len > 0
            and isinstance(in_values.get(name), str)
        ):
            if len(in_values[name]) > max_len:
                logger.debug("Field %s exceeds max_length %d", name, max_len)
                errors.append(
                    _err(name, "max_length", f"String exceeds max_length={max_len}.")
                )
                continue

        # Author-supplied validator(s)
        vfn = entry.get("validator")
        if callable(vfn) and in_values.get(name) is not None:
            try:
                out = vfn(in_values[name], ctx)
                if out is not None:
                    in_values[name] = out
            except Exception as e:
                logger.debug("Validator failed for field %s: %s", name, e)
                errors.append(
                    _err(name, "validator_failed", f"{type(e).__name__}: {e}")
                )
                continue

    # 3) Unknown keys policy (handled after build_in captured samples)
    unknown = tuple(temp.get("in_unknown") or ())
    if unknown and _reject_unknown(ctx):
        logger.debug("Rejecting unknown fields: %s", unknown)
        for k in unknown:
            errors.append(_err(k, "unknown_field", "Unknown input key."))

    # Persist results + diagnostics
    temp["in_values"] = in_values
    if coerced:
        temp["in_coerced"] = tuple(coerced)

    if errors:
        temp["in_errors"] = errors
        temp["in_invalid"] = True
        logger.debug("Validation errors found: %s", errors)
        raise HTTPException(
            status_code=_status.HTTP_422_UNPROCESSABLE_ENTITY, detail=errors
        )
    else:
        temp["in_invalid"] = False
        logger.debug("Inbound payload validated successfully")


# ──────────────────────────────────────────────────────────────────────────────
# Internals
# ──────────────────────────────────────────────────────────────────────────────


def _reject_unknown(ctx: Any) -> bool:
    """
    Check cfg for a 'reject_unknown_fields' (bool); default False.
    """
    cfg = getattr(ctx, "cfg", None)
    val = getattr(cfg, "reject_unknown_fields", None)
    return bool(val) if isinstance(val, bool) else False


def _err(field: str, code: str, msg: str) -> Dict[str, Any]:
    return {"field": field, "code": code, "message": msg}


def _type_name(t: type) -> str:
    return getattr(t, "__name__", str(t))


# ── coercion helpers ──────────────────────────────────────────────────────────


def _coerce_if_needed(
    value: Any, target: type, *, allow: bool
) -> Tuple[bool, Any, Optional[str]]:
    """Return (ok, new_value, error_message). Only coerces when allow=True."""
    if isinstance(value, target):
        return True, value, None
    if not allow:
        return False, value, f"Expected {_type_name(target)}."
    try:
        coerced = _coerce(value, target)
        return True, coerced, None
    except Exception:
        return False, value, f"Could not convert to {_type_name(target)}."


def _coerce(value: Any, target: type) -> Any:
    if target is str:
        return str(value)
    if target is int:
        if isinstance(value, bool):
            return int(value)
        return int(str(value).strip())
    if target is float:
        return float(str(value).strip())
    if target is bool:
        if isinstance(value, bool):
            return value
        s = str(value).strip().lower()
        if s in {"true", "1", "yes", "y", "on"}:
            return True
        if s in {"false", "0", "no", "n", "off"}:
            return False
        raise ValueError("not a boolean")
    if target is _dc.Decimal:
        return _dc.Decimal(str(value).strip())
    if target is _uuid.UUID:
        return _uuid.UUID(str(value))
    if target is _dt.datetime:
        # allow both date-time and date-only (promote to midnight)
        s = str(value).strip()
        try:
            return _dt.datetime.fromisoformat(s)
        except Exception:
            d = _dt.date.fromisoformat(s)
            return _dt.datetime.combine(d, _dt.time())
    if target is _dt.date:
        return _dt.date.fromisoformat(str(value).strip())
    if target is _dt.time:
        return _dt.time.fromisoformat(str(value).strip())
    # Fallback: try direct construction
    return target(value)


__all__ = ["ANCHOR", "run"]
