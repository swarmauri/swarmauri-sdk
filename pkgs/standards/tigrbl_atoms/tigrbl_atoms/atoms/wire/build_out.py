from __future__ import annotations

from ...types import Atom, Ctx, EncodedCtx
from ...stages import Operated, Encoded

from typing import Any, Dict, Mapping, Optional
import logging

from ... import events as _ev
from ..._opview_helpers import _ensure_ov, _ensure_schema_out, _ensure_temp

# POST_HANDLER, runs before readtime aliases and dump.
ANCHOR = _ev.OUT_BUILD  # "out:build"

logger = logging.getLogger("uvicorn")


def _run(obj: Optional[object], ctx: Any) -> None:
    """Build canonical outbound values keyed by field name."""
    logger.debug("Running wire:build_out")
    # When ``ctx.result`` is already populated by handler/serializer stages,
    # prefer that canonical payload and avoid reconstructing per-field output
    # from ``obj``. Rebuilding from ``obj`` can produce null-filled payloads
    # for RPC routes where ``obj`` is absent or list-shaped.
    if getattr(ctx, "result", None) is not None:
        temp = _ensure_temp(ctx)
        temp.pop("out_values", None)
        temp.pop("out_missing", None)
        temp.pop("out_virtual_produced", None)
        logger.debug("Skipping wire:build_out because ctx.result is already set")
        return

    ov = _ensure_ov(ctx)
    schema_out = _ensure_schema_out(ctx)
    by_field = schema_out["by_field"]
    expose = schema_out["expose"]

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


class AtomImpl(Atom[Operated, Encoded]):
    name = "wire.build_out"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Operated]) -> Ctx[Encoded]:
        _run(obj, ctx)
        return ctx.promote(EncodedCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
