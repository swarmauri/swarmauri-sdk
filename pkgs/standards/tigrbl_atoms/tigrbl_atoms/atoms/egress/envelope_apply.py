from __future__ import annotations

from ...types import Atom, Ctx, EncodedCtx
from ...stages import Encoded

from typing import Any, MutableMapping

from ... import events as _ev
from .._temp import _ensure_temp

ANCHOR = _ev.EGRESS_ENVELOPE_APPLY


def _is_jsonrpc(ctx: Any, egress: MutableMapping[str, Any]) -> bool:
    route = getattr(ctx, "gw_raw", None)
    if getattr(route, "kind", None) == "jsonrpc":
        return True

    path = getattr(route, "path", None)
    app = getattr(ctx, "app", None)
    prefix = getattr(app, "jsonrpc_prefix", None)
    if isinstance(path, str) and isinstance(prefix, str):
        if (path.rstrip("/") or "/") == (prefix.rstrip("/") or "/"):
            return True

    explicit = egress.get("response_kind")
    if explicit == "jsonrpc":
        return True

    route_temp = getattr(ctx, "temp", None)
    route_ns = route_temp.get("route") if isinstance(route_temp, dict) else None
    rpc_env = route_ns.get("rpc_envelope") if isinstance(route_ns, dict) else None
    if isinstance(rpc_env, dict) and rpc_env.get("jsonrpc") == "2.0":
        return True

    app = getattr(ctx, "app", None)
    prefix = getattr(app, "jsonrpc_prefix", None)
    raw = getattr(ctx, "raw", None)
    scope = getattr(raw, "scope", None)
    path = scope.get("path") if isinstance(scope, dict) else None
    if isinstance(prefix, str) and isinstance(path, str):
        norm_prefix = prefix.rstrip("/") or "/"
        norm_path = path.rstrip("/") or "/"
        if norm_path == norm_prefix:
            return True

    return False


def _run(obj: object | None, ctx: Any) -> None:
    del obj
    temp = _ensure_temp(ctx)
    egress = temp.setdefault("egress", {})

    payload = egress.get("wire_payload")
    if payload is None and "result" in egress:
        payload = egress.get("result")
    if payload is None and hasattr(ctx, "result"):
        payload = getattr(ctx, "result", None)
    temp = getattr(ctx, "temp", None)
    rpc_error = temp.get("rpc_error") if isinstance(temp, dict) else None
    if payload is None and not isinstance(rpc_error, dict):
        return

    if _is_jsonrpc(ctx, egress):
        if isinstance(payload, list) and all(
            isinstance(item, dict) and item.get("jsonrpc") == "2.0" for item in payload
        ):
            egress["enveloped"] = payload
            return

        request_rpc = getattr(getattr(ctx, "gw_raw", None), "rpc", None)
        if not isinstance(request_rpc, dict) and isinstance(temp, dict):
            route = temp.get("route")
            maybe_env = route.get("rpc_envelope") if isinstance(route, dict) else None
            if isinstance(maybe_env, dict):
                request_rpc = maybe_env

        rpc_id = request_rpc.get("id") if isinstance(request_rpc, dict) else None
        if isinstance(rpc_error, dict):
            egress["enveloped"] = {
                "jsonrpc": "2.0",
                "error": dict(rpc_error),
                "id": rpc_id,
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


class AtomImpl(Atom[Encoded, Encoded]):
    name = "egress.envelope_apply"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Encoded]) -> Ctx[Encoded]:
        _run(obj, ctx)
        return ctx.promote(EncodedCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
