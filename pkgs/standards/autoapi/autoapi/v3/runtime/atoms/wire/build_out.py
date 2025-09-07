from __future__ import annotations

from typing import Any, Dict, Mapping, MutableMapping, Optional
import logging

from ... import events as _ev
from ...kernel import _default_kernel as K

# POST_HANDLER, runs before readtime aliases and dump.
ANCHOR = _ev.OUT_BUILD  # "out:build"

logger = logging.getLogger("uvicorn")


def run(obj: Optional[object], ctx: Any) -> None:
    """Build canonical outbound values keyed by field name."""
    logger.debug("Running wire:build_out")
    app = getattr(ctx, "app", None)
    model = getattr(ctx, "model", None) or type(getattr(ctx, "obj", None))
    alias = getattr(ctx, "op", None) or getattr(ctx, "method", None)
    ov = None
    if app and model and alias:
        ov = K.get_opview(app, model, alias)
    else:
        if not (model and alias):
            logger.debug("build_out: missing ctx.app/model/op and no specs; skipping")
            return
        specs = getattr(ctx, "specs", None) or K.get_specs(model)
        ov = K._compile_opview_from_specs(specs, None)
    schema_out = ov.schema_out
    by_field = schema_out.by_field
    expose = schema_out.expose

    temp = _ensure_temp(ctx)
    out_values: Dict[str, Any] = {}
    produced_virtuals: list[str] = []
    missing: list[str] = []

    for field in expose:
        desc = by_field.get(field, {})
        if desc.get("virtual"):
            producer = ov.virtual_producers.get(field)
            if callable(producer):
                try:
                    out_values[field] = producer(obj, ctx)
                    produced_virtuals.append(field)
                    logger.debug("Produced virtual field %s", field)
                except Exception:
                    missing.append(field)
                    logger.debug("Virtual producer failed for field %s", field)
            else:
                missing.append(field)
                logger.debug("No producer for virtual field %s", field)
            continue

        value = _read_current_value(obj, ctx, field)
        if value is None:
            missing.append(field)
            logger.debug("No value available for field %s", field)
        out_values[field] = value

    temp["out_values"] = out_values
    if produced_virtuals:
        temp["out_virtual_produced"] = tuple(produced_virtuals)
    if missing:
        temp["out_missing"] = tuple(missing)
    logger.debug(
        "Built outbound values: %s (virtuals=%s, missing=%s)",
        out_values,
        produced_virtuals,
        missing,
    )


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
