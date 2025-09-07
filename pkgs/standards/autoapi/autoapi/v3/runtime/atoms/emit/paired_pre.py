from __future__ import annotations

import logging
from typing import Any, Dict, MutableMapping, Optional

from ... import events as _ev
from ...kernel import _default_kernel as K

# This atom runs before the flush, after values have been assembled/generated.
ANCHOR = _ev.EMIT_ALIASES_PRE  # "emit:aliases:pre_flush"

logger = logging.getLogger("uvicorn")


def run(obj: Optional[object], ctx: Any) -> None:
    app = getattr(ctx, "app", None) or getattr(ctx, "api", None)
    model = getattr(ctx, "model", None)
    alias = getattr(ctx, "op", None) or getattr(ctx, "method", None)
    if not (app and model and alias):
        raise RuntimeError("ctx_missing_app_model_or_op")

    ov = K.get_opview(app, model, alias)
    paired_meta = ov.paired_index

    temp = _ensure_temp(ctx)
    emit_buf = _ensure_emit_buf(temp)
    paired = _get_paired_values(temp)

    for field, entry in paired.items():
        if not isinstance(entry, dict) or "raw" not in entry:
            continue
        alias_name = (
            entry.get("alias") or paired_meta.get(field, {}).get("alias") or field
        )
        emit_buf["pre"].append(
            {
                "field": field,
                "alias": alias_name,
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


def _get_paired_values(temp: MutableMapping[str, Any]) -> Dict[str, Dict[str, Any]]:
    pv = temp.get("paired_values")
    return pv if isinstance(pv, dict) else {}


__all__ = ["ANCHOR", "run"]
