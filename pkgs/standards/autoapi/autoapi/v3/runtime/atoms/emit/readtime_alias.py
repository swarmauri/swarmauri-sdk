from __future__ import annotations

from typing import Any, Dict, Mapping, MutableMapping, Optional
import logging

from ... import events as _ev
from ...opview import opview_from_ctx, ensure_schema_out, _ensure_temp

# Runs near the end of the lifecycle, before wire:dump/out:masking.
ANCHOR = _ev.EMIT_ALIASES_READ  # "emit:aliases:readtime"

logger = logging.getLogger("uvicorn")


def run(obj: Optional[object], ctx: Any) -> None:
    """Emit safe read-time aliases into response extras."""
    logger.debug("Running emit:readtime_alias")
    temp = _ensure_temp(ctx)
    emit_buf = _ensure_emit_buf(temp)
    extras = _ensure_response_extras(temp)

    ov = opview_from_ctx(ctx)
    schema_out = ensure_schema_out(ctx, ov)
    for field, desc in schema_out["by_field"].items():
        out_alias = desc.get("alias_out")
        if not out_alias:
            continue
        if out_alias in extras:
            logger.debug("Alias %s already present in extras; skipping", out_alias)
            continue

        value = _read_current_value(obj, ctx, field)
        if value is None:
            logger.debug("No current value available for field %s", field)
            continue

        safe_val = _safe_readtime_value(value, desc)
        extras[out_alias] = safe_val
        logger.debug("Emitted read-time alias '%s' for field '%s'", out_alias, field)

        emit_buf["read"].append(
            {
                "field": field,
                "alias": out_alias,
                "emitted": True,
                "meta": _alias_meta(desc),
            }
        )


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


def _ensure_response_extras(temp: MutableMapping[str, Any]) -> Dict[str, Any]:
    extras = temp.get("response_extras")
    if not isinstance(extras, dict):
        extras = {}
        temp["response_extras"] = extras
    return extras  # type: ignore[return-value]


def _alias_meta(desc: Mapping[str, Any]) -> Dict[str, Any]:
    meta: Dict[str, Any] = {}
    for attr in ("sensitive", "mask_last"):
        if attr in desc:
            meta[attr] = desc[attr]
    return meta


def _read_current_value(obj: Optional[object], ctx: Any, field: str) -> Optional[Any]:
    if obj is not None and hasattr(obj, field):
        try:
            return getattr(obj, field)
        except Exception:
            pass
    for name in ("row", "values", "current_values"):
        src = getattr(ctx, name, None)
        if isinstance(src, Mapping) and field in src:
            return src.get(field)
    hv = getattr(getattr(ctx, "temp", {}), "get", lambda *a, **k: None)(
        "hydrated_values"
    )  # type: ignore
    if isinstance(hv, Mapping):
        return hv.get(field)
    return None


def _mask_value(value: Any, keep_last: Optional[int]) -> str:
    if isinstance(value, (bytes, bytearray, memoryview)):
        return "••••"
    s = str(value) if value is not None else ""
    if not s:
        return ""
    n = keep_last if (isinstance(keep_last, int) and keep_last >= 0) else 4
    n = min(n, len(s))
    return "•" * (len(s) - n) + s[-n:]


def _safe_readtime_value(value: Any, desc: Mapping[str, Any]) -> Any:
    if desc.get("sensitive"):
        keep_last = desc.get("mask_last")
        return _mask_value(value, keep_last)
    return value


__all__ = ["ANCHOR", "run"]
