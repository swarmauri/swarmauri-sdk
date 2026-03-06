from __future__ import annotations

from ...types import Atom, Ctx, cast_ctx
from ...stages import Failed, Encoded

from typing import Any

from ... import events as _ev
from ...status import create_standardized_error

ANCHOR = _ev.OUT_DUMP


async def _run(obj: object | None, ctx: Any) -> None:
    del obj
    err = getattr(ctx, "error", None)
    if err is None:
        return

    std = create_standardized_error(err)
    detail = std.detail if getattr(std, "detail", None) not in (None, "") else str(std)
    status_code = int(getattr(std, "status_code", 500) or 500)

    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    egress = temp.setdefault("egress", {})
    egress["transport_response"] = {
        "status_code": status_code,
        "headers": {"content-type": "application/json"},
        "body": {"detail": detail},
    }
    setattr(ctx, "status_code", status_code)


async def run(ctx: Any) -> None:
    await _run(None, ctx)


class AtomImpl(Atom[Failed, Encoded]):
    name = "response.error_to_transport"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Failed]) -> Ctx[Encoded]:
        await _run(obj, ctx)
        return cast_ctx(ctx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE", "run"]
