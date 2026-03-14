from __future__ import annotations

from typing import Any, Mapping

from ... import events as _ev
from ...stages import Bound
from ...types import Atom, BoundCtx, Ctx

ANCHOR = _ev.DISPATCH_INPUT_NORMALIZE


def _dispatch_dict(ctx: Any) -> dict[str, object]:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    obj = temp.setdefault("dispatch", {})
    if isinstance(obj, dict):
        return obj
    temp["dispatch"] = {}
    return temp["dispatch"]


def _normalize(value: object) -> object:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, list):
        return [_normalize(v) for v in value]
    if isinstance(value, tuple):
        return [_normalize(v) for v in value]
    if isinstance(value, Mapping):
        return {str(k): _normalize(v) for k, v in value.items()}
    return value


def _run(obj: object | None, ctx: Any) -> None:
    del obj
    dispatch = _dispatch_dict(ctx)
    temp = getattr(ctx, "temp", None)
    route = temp.setdefault("route", {}) if isinstance(temp, dict) else {}
    parsed = dispatch.get("parsed_payload")
    if isinstance(parsed, Mapping):
        normalized = {str(k): _normalize(v) for k, v in parsed.items()}
    else:
        normalized = _normalize(parsed)
    dispatch["normalized_input"] = normalized
    if isinstance(route, dict):
        route["payload"] = normalized
    setattr(ctx, "payload", normalized)


class AtomImpl(Atom[Bound, Bound]):
    name = "dispatch.input_normalize"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Bound]) -> Ctx[Bound]:
        _run(obj, ctx)
        return ctx.promote(BoundCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
