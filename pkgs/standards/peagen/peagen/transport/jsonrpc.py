from __future__ import annotations

import inspect
from typing import Callable, Dict

from .schemas import RPCError


class RPCException(Exception):
    """Exception wrapper for :class:`RPCError`."""

    def __init__(self, code: int, message: str, data=None) -> None:  # noqa: D401 - simple init
        super().__init__(message)
        self.error = RPCError(code=code, message=message, data=data)

    def model_dump(self) -> dict:
        """Return the underlying :class:`RPCError` payload."""
        return self.error.model_dump()


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

    async def dispatch(self, req: dict | list) -> dict | list:
        """Dispatch a single request or a batch of requests."""
        if isinstance(req, list):
            return [await self.dispatch(r) for r in req]

        if req.get("jsonrpc") != "2.0" or "method" not in req:
            return self._error(-32600, "Invalid Request", req.get("id"))

        fn = self._methods.get(req["method"])
        if fn is None:
            return self._error(-32601, "Method not found", req["id"])

        try:
            params = req.get("params") or {}
            sig = inspect.signature(fn)
            if not any(
                p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values()
            ):
                params = {k: v for k, v in params.items() if k in sig.parameters}
            result = fn(**params)
            if inspect.isawaitable(result):
                result = await result
            return {"jsonrpc": "2.0", "result": result, "id": req["id"]}
        except RPCException as exc:
            return {
                "jsonrpc": "2.0",
                "error": exc.model_dump(),
                "id": req["id"],
            }
        except Exception as exc:  # noqa: BLE001
            return self._error(-32000, str(exc), req["id"])

    @staticmethod
    def _error(code: int, msg: str, _id):
        return {"jsonrpc": "2.0", "error": {"code": code, "message": msg}, "id": _id}
