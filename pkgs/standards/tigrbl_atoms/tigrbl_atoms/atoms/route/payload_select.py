from __future__ import annotations

from typing import Any, Mapping

from ... import events as _ev
from ...stages import Bound
from ...types import Atom, BoundCtx, Ctx

ANCHOR = _ev.ROUTE_PAYLOAD_SELECT


def _route_dict(ctx: Any) -> dict[str, object]:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)

    route_obj = temp.setdefault("route", {})
    if isinstance(route_obj, dict):
        return route_obj

    route: dict[str, object] = {}
    temp["route"] = route
    return route


def _merge_dicts(
    base: Mapping[str, object], overlay: Mapping[str, object]
) -> dict[str, object]:
    out = {str(k): v for k, v in base.items()}
    for key, value in overlay.items():
        out[str(key)] = value
    return out


def _body_mapping(ctx: Any) -> dict[str, object]:
    body = getattr(ctx, "body", None)
    if isinstance(body, Mapping):
        return {str(k): v for k, v in body.items()}
    return {}


def _run(obj: object | None, ctx: Any) -> None:
    del obj

    route = _route_dict(ctx)
    protocol = str(route.get("protocol", "") or "")
    params = route.get("params")
    params_dict = (
        {str(k): v for k, v in params.items()} if isinstance(params, Mapping) else {}
    )

    payload: object
    payload_source: str

    if protocol.endswith(".jsonrpc"):
        rpc = route.get("rpc")
        if isinstance(rpc, Mapping) and "params" in rpc:
            payload = rpc.get("params")
            payload_source = "jsonrpc.params"
        else:
            payload = {}
            payload_source = "jsonrpc.empty"
    elif protocol.endswith(".rest"):
        body = _body_mapping(ctx)
        if body:
            payload = _merge_dicts(body, params_dict)
            payload_source = "body+params"
        elif params_dict:
            payload = dict(params_dict)
            payload_source = "params"
        else:
            payload = {}
            payload_source = "empty"
    elif protocol in {"ws", "wss"}:
        if params_dict:
            payload = dict(params_dict)
            payload_source = "params"
        else:
            payload = {}
            payload_source = "empty"
    else:
        if params_dict:
            payload = dict(params_dict)
            payload_source = "params"
        else:
            payload = {}
            payload_source = "empty"

    route["payload"] = payload
    route["payload_source"] = payload_source
    setattr(ctx, "payload", payload)


def run(obj: object | None, ctx: Any) -> None:
    _run(obj, ctx)


class AtomImpl(Atom[Bound, Bound]):
    name = "route.payload_select"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Bound]) -> Ctx[Bound]:
        _run(obj, ctx)
        return ctx.promote(
            BoundCtx,
            protocol=str(ctx.temp.get("route", {}).get("protocol", "") or ""),
            path_params=dict(ctx.temp.get("route", {}).get("path_params", {}) or {}),
            binding=ctx.temp.get("route", {}).get("binding"),
        )


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE", "run"]
