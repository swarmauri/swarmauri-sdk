from __future__ import annotations
import inspect, asyncio
from typing import Callable, Dict, Any


class RPCDispatcher:
    """Ultra-light JSON-RPC 2.0 dispatcher (no batching, no notifications)."""

    def __init__(self):
        self._methods: Dict[str, Callable] = {}

    # decorator: @rpc.method() or @rpc.method("Custom.Name")
    def method(self, name: str | None = None):
        def decorator(fn: Callable):
            self._methods[name or fn.__name__] = fn
            return fn
        return decorator

    async def dispatch(self, req: dict) -> dict:
        if req.get("jsonrpc") != "2.0" or "method" not in req:
            return self._error(-32600, "Invalid Request", req.get("id"))

        fn = self._methods.get(req["method"])
        if fn is None:
            return self._error(-32601, "Method not found", req["id"])

        try:
            params = req.get("params") or {}
            result = fn(**params)
            if inspect.isawaitable(result):
                result = await result
            return {"jsonrpc": "2.0", "result": result, "id": req["id"]}
        except Exception as exc:                        # noqa: BLE001
            return self._error(-32000, str(exc), req["id"])

    @staticmethod
    def _error(code: int, msg: str, _id):
        return {"jsonrpc": "2.0", "error": {"code": code, "message": msg}, "id": _id}
