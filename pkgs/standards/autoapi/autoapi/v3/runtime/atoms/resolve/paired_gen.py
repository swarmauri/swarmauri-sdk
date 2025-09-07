# autoapi/v3/runtime/atoms/resolve/paired_gen.py
from __future__ import annotations

import secrets
import logging
from typing import Any, Dict, MutableMapping, Optional

from ... import events as _ev
from ...kernel import _default_kernel as K

# Runs in HANDLER phase, before pre:flush (and before storage transforms).
ANCHOR = _ev.RESOLVE_VALUES  # "resolve:values"

logger = logging.getLogger("uvicorn")


def run(obj: Optional[object], ctx: Any) -> None:
    """Generate raw values for paired columns using OpView metadata."""
    app = getattr(ctx, "app", None) or getattr(ctx, "api", None)
    model = getattr(ctx, "model", None)
    alias = getattr(ctx, "op", None) or getattr(ctx, "method", None)
    if not (app and model and alias):
        raise RuntimeError("ctx_missing_app_model_or_op")

    ov = K.get_opview(app, model, alias)
    paired = ov.paired_index
    if not paired:
        return

    temp = _ensure_temp(ctx)
    assembled = _ensure_dict(temp, "assembled_values")
    virtual_in = _ensure_dict(temp, "virtual_in")
    paired_values = _ensure_dict(temp, "paired_values")
    persist_from_paired = _ensure_dict(temp, "persist_from_paired")

    generated: list[str] = []
    for field, desc in paired.items():
        if field in assembled:
            continue
        alias_name = desc.get("alias") or field
        raw = virtual_in.get(alias_name)
        if raw is None:
            gen = desc.get("gen")
            raw = gen(_ctx_view(ctx)) if callable(gen) else secrets.token_urlsafe(32)
        if raw is None:
            raise RuntimeError(f"paired_raw_missing:{field}")
        paired_values[field] = {"raw": raw, "alias": alias_name, "meta": {}}
        persist_from_paired[field] = {"source": ("paired_values", field, "raw")}
        generated.append(field)

    if generated:
        temp["generated_paired"] = tuple(generated)


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
