from __future__ import annotations

from typing import Any, MutableMapping

from ... import events as _ev

ANCHOR = _ev.EGRESS_ENVELOPE_APPLY


def _ensure_temp(ctx: Any) -> MutableMapping[str, Any]:
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    return temp


def _is_jsonrpc(ctx: Any, egress: MutableMapping[str, Any]) -> bool:
    route = getattr(ctx, "gw_raw", None)
    if getattr(route, "kind", None) == "jsonrpc":
        return True

    explicit = egress.get("response_kind")
    if explicit == "jsonrpc":
        return True

    route_temp = getattr(ctx, "temp", None)
    route_ns = route_temp.get("route") if isinstance(route_temp, dict) else None
    rpc_env = route_ns.get("rpc_envelope") if isinstance(route_ns, dict) else None
    return isinstance(rpc_env, dict) and rpc_env.get("jsonrpc") == "2.0"


def run(obj: object | None, ctx: Any) -> None:
    del obj
    temp = _ensure_temp(ctx)
    egress = temp.setdefault("egress", {})

    payload = egress.get("wire_payload")
    if payload is None:
        return

    if _is_jsonrpc(ctx, egress):
        request_rpc = getattr(getattr(ctx, "gw_raw", None), "rpc", None)
        rpc_id = request_rpc.get("id") if isinstance(request_rpc, dict) else None
        if isinstance(payload, dict) and isinstance(payload.get("__rpc_error__"), dict):
            egress["enveloped"] = {
                "jsonrpc": "2.0",
                "error": payload["__rpc_error__"],
                "id": payload.get("__rpc_id__", rpc_id),
            }
        else:
            egress["enveloped"] = {
                "jsonrpc": "2.0",
                "result": payload,
                "id": rpc_id,
            }
        return

    envelope = egress.get("envelope")
    if isinstance(envelope, dict):
        data = dict(envelope)
        data.setdefault("data", payload)
        egress["enveloped"] = data
    else:
        egress["enveloped"] = payload


__all__ = ["ANCHOR", "run"]
