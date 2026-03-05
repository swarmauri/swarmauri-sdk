from __future__ import annotations

from typing import Any, MutableMapping

from ... import events as _ev

ANCHOR = _ev.EGRESS_HTTP_FINALIZE


def _ensure_temp(ctx: Any) -> MutableMapping[str, Any]:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    return temp


def run(obj: object | None, ctx: Any) -> None:
    del obj
    temp = _ensure_temp(ctx)
    egress = temp.setdefault("egress", {})

    status_code = egress.get("status_code", getattr(ctx, "status_code", None))
    if status_code is None:
        status_code = 200
    status = int(status_code)

    route = getattr(ctx, "gw_raw", None)
    if getattr(route, "kind", None) == "jsonrpc":
        status = 200
    else:
        route_temp = temp.get("route") if isinstance(temp.get("route"), dict) else None
        rpc_env = (
            route_temp.get("rpc_envelope") if isinstance(route_temp, dict) else None
        )
        if isinstance(rpc_env, dict) and rpc_env.get("jsonrpc") == "2.0":
            status = 200

    egress["status_code"] = status
    setattr(ctx, "status_code", status)


__all__ = ["ANCHOR", "run"]
