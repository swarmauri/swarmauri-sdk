from __future__ import annotations

import inspect
from typing import Callable, Dict, get_type_hints

from pydantic import BaseModel

from peagen.protocols import Error


class RPCException(Exception):
    """Exception carrying JSON-RPC error details."""

    def __init__(self, code: int, message: str, data: object | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.data = data

    def as_error(self) -> dict:
        return Error(code=self.code, message=self.message, data=self.data).model_dump()


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
            bound_args = None
            if len(sig.parameters) == 1:
                param = next(iter(sig.parameters.values()))
                hints = get_type_hints(fn)
                ann = hints.get(param.name, param.annotation)
                if inspect.isclass(ann) and issubclass(ann, BaseModel):
                    bound_args = {param.name: ann(**params)}
            if bound_args is None:
                bound_args = params
            result = fn(**bound_args)
            if inspect.isawaitable(result):
                result = await result
            return {"jsonrpc": "2.0", "result": result, "id": req["id"]}
        except RPCException as exc:
            return {
                "jsonrpc": "2.0",
                "error": exc.as_error(),
                "id": req["id"],
            }
        except Exception as exc:  # noqa: BLE001
            return self._error(-32000, str(exc), req["id"])

    @staticmethod
    def _error(code: int, msg: str, _id):
        return {"jsonrpc": "2.0", "error": {"code": code, "message": msg}, "id": _id}
