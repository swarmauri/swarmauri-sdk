# autoapi/v3/runtime/atoms/resolve/assemble.py
from __future__ import annotations

from typing import Any, Mapping, MutableMapping, Optional, Dict, Tuple
import logging

from ... import events as _ev
from ...kernel import _default_kernel as K

# Runs in HANDLER phase, before pre:flush and any storage transforms.
ANCHOR = _ev.RESOLVE_VALUES  # "resolve:values"

logger = logging.getLogger("uvicorn")


def run(obj: Optional[object], ctx: Any) -> None:
    """Assemble inbound values according to schema_in from OpView."""
    app = getattr(ctx, "app", None) or getattr(ctx, "api", None)
    model = getattr(ctx, "model", None)
    alias = getattr(ctx, "op", None) or getattr(ctx, "method", None)
    if not (app and model and alias):
        raise RuntimeError("ctx_missing_app_model_or_op")

    ov = K.get_opview(app, model, alias)
    schema_in = ov.schema_in

    inbound = _coerce_inbound(getattr(ctx, "temp", {}).get("in_values", None), ctx)

    temp = _ensure_temp(ctx)
    assembled: Dict[str, Any] = {}
    virtual_in: Dict[str, Any] = {}
    absent: list[str] = []
    used_default: list[str] = []

    for field in schema_in.fields:
        info = schema_in.by_field.get(field, {})
        alias_in = info.get("alias_in")
        present, value = _try_read_inbound(inbound, alias_in or field)
        is_virtual = bool(info.get("virtual"))
        if present:
            if is_virtual:
                virtual_in[field] = value
            else:
                assembled[field] = value
            continue
        absent.append(field)
        default_fn = info.get("default_factory")
        if callable(default_fn) and not is_virtual:
            try:
                assembled[field] = default_fn(_ctx_view(ctx))
                used_default.append(field)
            except Exception:
                pass

    temp["assembled_values"] = assembled
    temp["virtual_in"] = virtual_in
    temp["absent_fields"] = tuple(absent)
    temp["used_default_factory"] = tuple(used_default)


# ──────────────────────────────────────────────────────────────────────────────
# Internals
# ──────────────────────────────────────────────────────────────────────────────


def _ensure_temp(ctx: Any) -> MutableMapping[str, Any]:
    tmp = getattr(ctx, "temp", None)
    if not isinstance(tmp, dict):
        tmp = {}
        setattr(ctx, "temp", tmp)
    return tmp


def _coerce_inbound(candidate: Any, ctx: Any) -> Mapping[str, Any]:
    for name in ("in_values",):
        if isinstance(candidate, Mapping):
            return candidate
    for attr in ("in_data", "payload", "data", "body"):
        val = getattr(ctx, attr, None)
        if isinstance(val, Mapping):
            return val
        if hasattr(val, "model_dump") and callable(getattr(val, "model_dump")):
            try:
                return dict(val.model_dump())
            except Exception:
                pass
        if hasattr(val, "dict") and callable(getattr(val, "dict")):
            try:
                return dict(val.dict())
            except Exception:
                pass
    return {}


def _try_read_inbound(inbound: Mapping[str, Any], field: str) -> Tuple[bool, Any]:
    if field in inbound:
        return True, inbound.get(field)
    for alt in (field.lower(), field.upper()):
        if alt in inbound:
            return True, inbound.get(alt)
    return False, None


def _ctx_view(ctx: Any) -> Dict[str, Any]:
    return {
        "op": getattr(ctx, "op", None),
        "persist": getattr(ctx, "persist", True),
        "temp": getattr(ctx, "temp", None),
        "tenant": getattr(ctx, "tenant", None),
        "user": getattr(ctx, "user", None),
        "now": getattr(ctx, "now", None),
    }


__all__ = ["ANCHOR", "run"]
