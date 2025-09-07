from __future__ import annotations

from typing import Any, MutableMapping, Optional
import logging

from ... import events as _ev
from ...kernel import _default_kernel as K

# Runs late in POST_HANDLER, before out model build and dumping.
ANCHOR = _ev.SCHEMA_COLLECT_OUT  # "schema:collect_out"

logger = logging.getLogger("uvicorn")


def run(obj: Optional[object], ctx: Any) -> None:
    """Load precompiled outbound schema into ctx.temp."""
    app = getattr(ctx, "app", None)
    model = getattr(ctx, "model", None)
    alias = getattr(ctx, "op", None) or getattr(ctx, "method", None)

    ov = None
    if app and model and alias:
        ov = K.get_opview(app, model, alias)
    else:
        model = model or type(getattr(ctx, "obj", None))
        if not (model and alias):
            logger.debug("collect_out: missing ctx.app/model/op and no specs; skipping")
            return
        specs = getattr(ctx, "specs", None) or K.get_specs(model)
        ov = K._compile_opview_from_specs(specs, None)

    temp = _ensure_temp(ctx)
    temp["schema_out"] = {
        "fields": ov.schema_out.fields,
        "by_field": ov.schema_out.by_field,
        "expose": ov.schema_out.expose,
    }


def _ensure_temp(ctx: Any) -> MutableMapping[str, Any]:
    tmp = getattr(ctx, "temp", None)
    if not isinstance(tmp, dict):
        tmp = {}
        setattr(ctx, "temp", tmp)
    return tmp


__all__ = ["ANCHOR", "run"]
