# autoapi/v3/runtime/atoms/storage/to_stored.py
from __future__ import annotations

import logging
from typing import Any, Dict, MutableMapping, Optional

from ... import events as _ev
from ...kernel import _default_kernel as K

# Runs right before the handler flushes to the DB.
ANCHOR = _ev.PRE_FLUSH  # "pre:flush"

logger = logging.getLogger("uvicorn")


def run(obj: Optional[object], ctx: Any) -> None:
    """Transform inbound values into their persisted representation."""
    app = getattr(ctx, "app", None) or getattr(ctx, "api", None)
    model = getattr(ctx, "model", None)
    alias = getattr(ctx, "op", None) or getattr(ctx, "method", None)
    if not (app and model and alias):
        raise RuntimeError("ctx_missing_app_model_or_op")

    ov = K.get_opview(app, model, alias)
    paired = ov.paired_index
    transforms = ov.to_stored_transforms

    temp = _ensure_temp(ctx)
    assembled = _ensure_dict(temp, "assembled_values")
    paired_values = _ensure_dict(temp, "paired_values")
    pf_paired = _ensure_dict(temp, "persist_from_paired")

    target_obj = obj or getattr(ctx, "model", None)

    for field, desc in paired.items():
        if field in pf_paired or field in paired_values:
            raw = paired_values.get(field, {}).get("raw")
            if raw is None:
                raise RuntimeError(f"paired_raw_missing:{field}")
            store = desc.get("store")
            stored = store(raw, ctx) if callable(store) else raw
            assembled[field] = stored
            if target_obj is None:
                raise RuntimeError("hydrated_object_missing")
            setattr(target_obj, field, stored)

    for field, trans in transforms.items():
        if field in assembled:
            stored_val = trans(assembled[field], ctx)
            assembled[field] = stored_val
            if target_obj is None:
                raise RuntimeError("hydrated_object_missing")
            setattr(target_obj, field, stored_val)


# ──────────────────────────────────────────────────────────────────────────────
# Internals
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


__all__ = ["ANCHOR", "run"]
