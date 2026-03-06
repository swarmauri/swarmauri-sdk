from __future__ import annotations

from ...types import Atom, Ctx, cast_ctx
from ...stages import Executing, Operated

from typing import Any

from ... import events as _ev
from ... import system as _sys
from ...status import create_standardized_error, to_rpc_error_payload

ANCHOR = _ev.SYS_HANDLER_PERSISTENCE
_delegate = _sys.get("handler", "crud")[1]


async def _run(obj: object | None, ctx: Any) -> None:
    try:
        rv = _delegate(obj, ctx)
        if hasattr(rv, "__await__"):
            await rv
    except Exception as exc:
        route = getattr(ctx, "gw_raw", None)
        temp = getattr(ctx, "temp", None)
        route_ns = temp.get("route") if isinstance(temp, dict) else None
        rpc_env = route_ns.get("rpc_envelope") if isinstance(route_ns, dict) else None
        is_jsonrpc = getattr(route, "kind", None) == "jsonrpc" or (
            isinstance(rpc_env, dict) and rpc_env.get("jsonrpc") == "2.0"
        )
        if not is_jsonrpc:
            raise

        http_exc = create_standardized_error(exc)
        if not isinstance(temp, dict):
            temp = {}
            setattr(ctx, "temp", temp)
        temp["rpc_error"] = to_rpc_error_payload(http_exc)
        setattr(ctx, "status_code", 200)
        setattr(ctx, "result", None)




class AtomImpl(Atom[Executing, Operated]):
    name = "sys.handler_persistence"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Executing]) -> Ctx[Operated]:
        await _run(obj, ctx)
        return cast_ctx(ctx)

INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
