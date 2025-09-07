from __future__ import annotations

import logging
from typing import Any, Dict, MutableMapping, Optional, Sequence, Mapping

from ... import events as _ev
from ...kernel import _default_kernel as K

# Runs at the very end of the lifecycle (after wire:dump).
ANCHOR = _ev.OUT_DUMP  # "out:dump"

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
    payload = temp.get("response_payload")
    if payload is None:
        raise RuntimeError("response_payload_missing")

    emit_buf = _ensure_emit_buf(temp)
    skip_aliases = _collect_emitted_aliases(emit_buf)

    if isinstance(payload, dict):
        _mask_one(payload, meta, skip_aliases)
    elif isinstance(payload, (list, tuple)):
        for item in payload:
            if isinstance(item, dict):
                _mask_one(item, meta, skip_aliases)


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


def _collect_emitted_aliases(
    emit_buf: Mapping[str, Sequence[Mapping[str, Any]]],
) -> set[str]:
    aliases: set[str] = set()
    for bucket in ("post", "read"):
        for d in emit_buf.get(bucket, ()) or ():
            a = d.get("alias")
            if isinstance(a, str) and a:
                aliases.add(a)
    return aliases


def _mask_one(
    item: Dict[str, Any], meta: Mapping[str, Dict[str, Any]], skip_aliases: set[str]
) -> None:
    for field, info in meta.items():
        if field not in item or field in skip_aliases:
            continue
        if not info.get("sensitive"):
            continue
        value = item.get(field)
        keep_last = info.get("mask_last")
        item[field] = _mask_value(value, keep_last)


def _mask_value(value: Any, keep_last: Optional[int]) -> str:
    if isinstance(value, (bytes, bytearray, memoryview)):
        return "••••"
    s = str(value) if value is not None else ""
    if not s:
        return ""
    n = keep_last if (isinstance(keep_last, int) and keep_last >= 0) else 4
    n = min(n, len(s))
    return "•" * (len(s) - n) + s[-n:]


__all__ = ["ANCHOR", "run"]
