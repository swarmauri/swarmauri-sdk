from __future__ import annotations

from dataclasses import asdict
import logging
from typing import Any, MutableMapping, Optional

from ... import events as _ev
from ...kernel import _default_kernel as K

# Runs late in POST_HANDLER, before out model build and dumping.
ANCHOR = _ev.SCHEMA_COLLECT_OUT  # "schema:collect_out"

logger = logging.getLogger("uvicorn")


def run(obj: Optional[object], ctx: Any) -> None:
    """Load precompiled outbound schema into ``ctx.temp``.

    The schema is sourced from the OpView compiled during application start. If
    the runtime context lacks the necessary identifiers we raise ``RuntimeError``
    to signal misconfiguration instead of silently skipping work.
    """

    app = getattr(ctx, "app", None) or getattr(ctx, "api", None)
    model = getattr(ctx, "model", None)
    alias = getattr(ctx, "op", None) or getattr(ctx, "method", None)
    if not (app and model and alias):  # pragma: no cover - defensive
        raise RuntimeError("ctx_missing_app_model_or_op")

    ov = K.get_opview(app, model, alias)
    temp = _ensure_temp(ctx)
    temp["schema_out"] = asdict(ov.schema_out)


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------


def _ensure_temp(ctx: Any) -> MutableMapping[str, Any]:
    tmp = getattr(ctx, "temp", None)
    if not isinstance(tmp, dict):
        tmp = {}
        setattr(ctx, "temp", tmp)
    return tmp


__all__ = ["ANCHOR", "run"]
