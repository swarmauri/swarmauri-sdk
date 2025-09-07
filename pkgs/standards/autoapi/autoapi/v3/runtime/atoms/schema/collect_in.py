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
    app = getattr(ctx, "app", None) or getattr(ctx, "api", None)
    model = getattr(ctx, "model", None)
    alias = getattr(ctx, "op", None) or getattr(ctx, "method", None)
    if not (app and model and alias):
        raise RuntimeError("ctx_missing_app_model_or_op")

    ov = K.get_opview(app, model, alias)
    temp = _ensure_temp(ctx)
    temp["schema_in"] = ov.schema_in


def _ensure_temp(ctx: Any) -> MutableMapping[str, Any]:
    tmp = getattr(ctx, "temp", None)
    if not isinstance(tmp, dict):
        tmp = {}
        setattr(ctx, "temp", tmp)
    return tmp


__all__ = ["ANCHOR", "run"]
