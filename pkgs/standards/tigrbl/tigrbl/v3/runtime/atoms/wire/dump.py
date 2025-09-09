# tigrbl/v3/runtime/atoms/wire/dump.py
from __future__ import annotations

import base64
import datetime as _dt
import decimal as _dc
import uuid as _uuid
import logging
from typing import Any, Dict, Mapping, MutableMapping, Optional

from ... import events as _ev

# Runs at the very end of model shaping; out:masking follows at the same anchor.
ANCHOR = _ev.OUT_DUMP  # "out:dump"

logger = logging.getLogger("uvicorn")


def run(obj: Optional[object], ctx: Any) -> None:
    """
    wire:dump@out:dump

    Purpose
    -------
    Build the final wire payload (dict or list[dict]) from:
      - ctx.temp["out_values"] (field -> value) produced by wire:build_out
      - ctx.temp["schema_out"] (for alias mapping)
      - ctx.temp["response_extras"] (alias extras from emit atoms)

    What it does
    ------------
    - Maps canonical field names → wire keys using alias_out (when provided).
    - Optionally omits null values (cfg.exclude_none / cfg.omit_nulls).
    - Applies minimal JSON-friendly scalar conversions (date/time/uuid/decimal/bytes).
    - Merges response_extras (without overwriting unless configured) for single-object payloads.
    - Stores the result in ctx.temp["response_payload"] for downstream masking/transport.

    Notes
    -----
    - This step does NOT perform masking/redaction; that is handled by out:masking.
    - For collection/list responses, extras are not merged (they are usually per-item).
    """
    logger.debug("Running wire:dump")
    temp = _ensure_temp(ctx)
    out_values = temp.get("out_values")

    if not out_values:
        logger.debug("No out_values available; skipping dump")
        return  # nothing to dump

    schema_out = _schema_out(ctx)
    aliases: Mapping[str, str] = (
        schema_out.get("aliases", {}) if isinstance(schema_out, Mapping) else {}
    )

    omit_nulls = _omit_nulls(ctx)
    allow_overwrite = _allow_extras_overwrite(ctx)

    # Single object
    if isinstance(out_values, Mapping):
        logger.debug("Dumping single-object payload")
        payload = _dump_one(out_values, aliases, omit_nulls)
        # Merge extras (single-object only)
        extras = temp.get("response_extras")
        if isinstance(extras, Mapping) and extras:
            conflicts = []
            for k, v in extras.items():
                if (k in payload) and not allow_overwrite:
                    conflicts.append(k)
                    logger.debug("Conflict on extra key %s", k)
                    continue
                payload[k] = _dump_scalar(v)
            if conflicts:
                temp["dump_conflicts"] = tuple(sorted(set(conflicts)))
        temp["response_payload"] = payload
        logger.debug("Response payload built: %s", payload)
        return None

    # List/tuple of objects (already expanded by executor)
    if isinstance(out_values, (list, tuple)) and all(
        isinstance(x, Mapping) for x in out_values
    ):
        logger.debug("Dumping list payload with %d items", len(out_values))
        payload_list = [
            _dump_one(item, aliases, omit_nulls)
            for item in out_values  # type: ignore[arg-type]
        ]
        temp["response_payload"] = payload_list
        return None

    # Unknown shape — stash as-is to avoid surprises (transport may serialize).
    temp["response_payload"] = out_values
    logger.debug("Stored opaque response payload: %s", type(out_values).__name__)
    return None


# ──────────────────────────────────────────────────────────────────────────────
# Internals
# ──────────────────────────────────────────────────────────────────────────────


def _ensure_temp(ctx: Any) -> MutableMapping[str, Any]:
    tmp = getattr(ctx, "temp", None)
    if not isinstance(tmp, dict):
        tmp = {}
        setattr(ctx, "temp", tmp)
    return tmp


def _schema_out(ctx: Any) -> Mapping[str, Any]:
    tmp = getattr(ctx, "temp", {})
    sch = getattr(tmp, "get", lambda *_a, **_k: None)("schema_out")  # type: ignore
    if isinstance(sch, Mapping):
        return sch
    sch2 = getattr(ctx, "schema_out", None)
    return sch2 if isinstance(sch2, Mapping) else {}


def _omit_nulls(ctx: Any) -> bool:
    """
    Config flags to drop null-valued keys:
      - cfg.exclude_none (preferred)
      - cfg.omit_nulls
    Default False.
    """
    cfg = getattr(ctx, "cfg", None)
    for name in ("exclude_none", "omit_nulls"):
        val = getattr(cfg, name, None)
        if isinstance(val, bool):
            return val
    return False


def _allow_extras_overwrite(ctx: Any) -> bool:
    """
    If True, extras can overwrite existing keys; default False.
    cfg.extras_overwrite or cfg.response_extras_overwrite.
    """
    cfg = getattr(ctx, "cfg", None)
    for name in ("response_extras_overwrite", "extras_overwrite"):
        val = getattr(cfg, name, None)
        if isinstance(val, bool):
            return val
    return False


def _dump_one(
    values: Mapping[str, Any], aliases: Mapping[str, str], omit_nulls: bool
) -> Dict[str, Any]:
    """
    Convert a single out_values mapping to a wire payload dict with alias mapping and scalar dumps.
    """
    out: Dict[str, Any] = {}
    used_aliases: list[str] = []
    omitted: list[str] = []

    for field, val in values.items():
        if omit_nulls and val is None:
            omitted.append(field)
            continue
        key = aliases.get(field) or field
        if key != field:
            used_aliases.append(key)
        out[key] = _dump_scalar(val)

    if used_aliases:
        # diagnostics hook
        # note: this goes on the payload's temp, not user-visible
        pass
    return out


def _dump_scalar(v: Any) -> Any:
    """
    Minimal JSON-friendly conversion for common scalars.
    Leave complex types as-is; transport may have its own encoder.
    """
    if v is None:
        return None
    if isinstance(v, (_dt.datetime, _dt.date, _dt.time)):
        # ISO 8601
        try:
            return v.isoformat()
        except Exception:
            return str(v)
    if isinstance(v, _uuid.UUID):
        return str(v)
    if isinstance(v, _dc.Decimal):
        # Preserve precision via string
        return str(v)
    if isinstance(v, (bytes, bytearray, memoryview)):
        try:
            return base64.b64encode(bytes(v)).decode("ascii")
        except Exception:
            return None
    # Plain containers → recurse shallowly
    if isinstance(v, Mapping):
        return {k: _dump_scalar(v[k]) for k in v}
    if isinstance(v, list):
        return [_dump_scalar(x) for x in v]
    if isinstance(v, tuple):
        return tuple(_dump_scalar(x) for x in v)
    return v


__all__ = ["ANCHOR", "run"]
