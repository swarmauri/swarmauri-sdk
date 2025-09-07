from __future__ import annotations

import logging
from typing import Any, Dict, Mapping, MutableMapping, Optional

from ... import events as _ev
from ...kernel import _default_kernel as K

# Runs near the end of the lifecycle, before wire:dump/out:masking.
ANCHOR = _ev.EMIT_ALIASES_READ  # "emit:aliases:readtime"

logger = logging.getLogger("uvicorn")


def run(obj: Optional[object], ctx: Any) -> None:
    app = getattr(ctx, "app", None) or getattr(ctx, "api", None)
    model = getattr(ctx, "model", None)
    alias = getattr(ctx, "op", None) or getattr(ctx, "method", None)
    if not (app and model and alias):
        raise RuntimeError("ctx_missing_app_model_or_op")

    ov = K.get_opview(app, model, alias)
    meta = ov.schema_out.by_field

    temp = _ensure_temp(ctx)
    emit_buf = _ensure_emit_buf(temp)
    extras = _ensure_response_extras(temp)

    for field, info in meta.items():
        alias_name = info.get("alias_out") or field
        if alias_name in extras:
            continue
        value = _read_current_value(obj, ctx, field)
        if value is None:
            continue
        mask_last = info.get("mask_last") if info.get("sensitive") else None
        if mask_last:
            value = _mask_last(value, mask_last)
        extras[alias_name] = value
        emit_buf["read"].append(
            {
                "field": field,
                "alias": alias_name,
                "emitted": True,
                "meta": {"sensitive": info.get("sensitive"), "mask_last": mask_last},
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


def _ensure_response_extras(temp: MutableMapping[str, Any]) -> Dict[str, Any]:
    extras = temp.get("response_extras")
    if not isinstance(extras, dict):
        extras = {}
        temp["response_extras"] = extras
    return extras  # type: ignore[return-value]


def _mask_last(value: Any, keep: int) -> str:
    s = str(value)
    n = min(int(keep), len(s))
    return "*" * (len(s) - n) + s[-n:]


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


__all__ = ["ANCHOR", "run"]
