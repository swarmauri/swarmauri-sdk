from __future__ import annotations

import logging
from typing import Any, Dict, Mapping, MutableMapping, Optional

from ... import events as _ev
from ...kernel import _default_kernel as K

# POST_HANDLER, runs before readtime aliases and dump.
ANCHOR = _ev.OUT_BUILD  # "out:build"

logger = logging.getLogger("uvicorn")


def run(obj: Optional[object], ctx: Any) -> None:
    app = getattr(ctx, "app", None) or getattr(ctx, "api", None)
    model = getattr(ctx, "model", None)
    alias = getattr(ctx, "op", None) or getattr(ctx, "method", None)
    if not (app and model and alias):
        raise RuntimeError("ctx_missing_app_model_or_op")

    ov = K.get_opview(app, model, alias)
    schema_out = getattr(ctx, "temp", {}).get("schema_out") or ov.schema_out
    if not schema_out:
        raise RuntimeError("schema_out_missing")

    temp = _ensure_temp(ctx)
    out_values: Dict[str, Any] = {}
    produced_virtuals: list[str] = []
    missing: list[str] = []

    expose = schema_out.expose
    for field in expose:
        if field in ov.virtual_producers:
            producer = ov.virtual_producers[field]
            try:
                out_values[field] = producer(obj, ctx)
                produced_virtuals.append(field)
            except Exception:
                missing.append(field)
            continue
        value = _read_current_value(obj, ctx, field)
        if value is None:
            missing.append(field)
        out_values[field] = value

    temp["out_values"] = out_values
    if produced_virtuals:
        temp["out_virtual_produced"] = tuple(produced_virtuals)
    if missing:
        temp["out_missing"] = tuple(missing)


# ──────────────────────────────────────────────────────────────────────────────
# Internals
# ──────────────────────────────────────────────────────────────────────────────


def _ensure_temp(ctx: Any) -> MutableMapping[str, Any]:
    tmp = getattr(ctx, "temp", None)
    if not isinstance(tmp, dict):
        tmp = {}
        setattr(ctx, "temp", tmp)
    return tmp


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
