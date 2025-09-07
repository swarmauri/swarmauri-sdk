from __future__ import annotations

from typing import Any, MutableMapping, Optional
import logging

from ... import events as _ev
from ...kernel import _default_kernel as K

# Runs at the very beginning of the lifecycle, before in-model build/validation.
ANCHOR = _ev.SCHEMA_COLLECT_IN  # "schema:collect_in"

logger = logging.getLogger("uvicorn")


def run(obj: Optional[object], ctx: Any) -> None:
    """Load precompiled inbound schema into ctx.temp."""
    app = getattr(ctx, "app", None)
    model = getattr(ctx, "model", None)
    alias = getattr(ctx, "op", None) or getattr(ctx, "method", None)

    if app and model and alias:
        ov = K.get_opview(app, model, alias)
        temp = _ensure_temp(ctx)
        temp["schema_in"] = {
            "fields": ov.schema_in.fields,
            "by_field": ov.schema_in.by_field,
            "required": tuple(
                f for f, meta in ov.schema_in.by_field.items() if meta.get("required")
            ),
        }
        return

    # Fallback: compile minimal schema from collected specs
    model = model or (
        type(getattr(ctx, "obj", None)) if getattr(ctx, "obj", None) else None
    )
    specs = getattr(ctx, "specs", None) or (K.get_specs(model) if model else None)
    if specs is None or alias is None:
        logger.debug("collect_in: missing ctx.app/model/op and no specs; skipping")
        return

    fields = tuple(sorted(specs.keys()))
    by_field: dict[str, dict] = {}
    required: list[str] = []
    for name, spec in specs.items():
        meta: dict[str, Any] = {}
        field_spec = getattr(spec, "field", None)
        if field_spec and alias in getattr(field_spec, "required_in", ()):
            meta["required"] = True
            required.append(name)
        if field_spec and alias in getattr(field_spec, "allow_null_in", ()):
            meta["nullable"] = True
        by_field[name] = meta

    temp = _ensure_temp(ctx)
    temp["schema_in"] = {
        "fields": fields,
        "by_field": by_field,
        "required": tuple(required),
    }


def _ensure_temp(ctx: Any) -> MutableMapping[str, Any]:
    tmp = getattr(ctx, "temp", None)
    if not isinstance(tmp, dict):
        tmp = {}
        setattr(ctx, "temp", tmp)
    return tmp


__all__ = ["ANCHOR", "run"]
