from __future__ import annotations

from ...types import Atom, Ctx, OperatedCtx
from ...stages import Operated

from typing import Any, Callable, Mapping, Optional
import logging

from ... import events as _ev
from ..._opview_helpers import _ensure_schema_out

# Runs late in POST_HANDLER, before out model build and dumping.
ANCHOR = _ev.SCHEMA_COLLECT_OUT  # "schema:collect_out"

logger = logging.getLogger("uvicorn")


def _build_projector(
    fields: tuple[str, ...],
) -> Callable[[Any], Any]:
    def _project_one(value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, Mapping):
            return {name: value.get(name) for name in fields}
        return {name: getattr(value, name, None) for name in fields}

    def _project(value: Any) -> Any:
        if isinstance(value, list):
            return [_project_one(item) for item in value]
        if isinstance(value, tuple):
            return [_project_one(item) for item in value]
        return _project_one(value)

    return _project


def _get_projector(schema_out: dict[str, Any]) -> Callable[[Any], Any]:
    cached = schema_out.get("__projector__")
    if callable(cached):
        return cached
    fields = tuple(
        str(name) for name in schema_out.get("expose", ()) if isinstance(name, str)
    )
    projector = _build_projector(fields)
    schema_out["__projector__"] = projector
    return projector


def _run(obj: Optional[object], ctx: Any) -> None:
    """Load precompiled outbound schema into ctx.temp."""
    del obj
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)

    schema_out = temp.get("schema_out")
    if not isinstance(schema_out, dict):
        schema_out = dict(_ensure_schema_out(ctx))
        temp["schema_out"] = schema_out
    if not callable(getattr(ctx, "response_serializer", None)):
        setattr(ctx, "response_serializer", _get_projector(schema_out))


class AtomImpl(Atom[Operated, Operated]):
    name = "schema.collect_out"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Operated]) -> Ctx[Operated]:
        _run(obj, ctx)
        return ctx.promote(OperatedCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
