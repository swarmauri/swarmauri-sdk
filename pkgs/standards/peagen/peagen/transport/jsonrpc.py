from __future__ import annotations

import inspect
from typing import Callable, Dict

from pydantic import BaseModel
from peagen.transport import _registry
from peagen.transport.envelope import Error


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
            PModel = _registry.params_model(req["method"])
            sig = inspect.signature(fn)

            if PModel and len(sig.parameters) == 1:
                arg_name, _ = next(iter(sig.parameters.items()))
                hints = inspect.get_annotations(fn, eval_str=True)
                ann = hints.get(arg_name)
                if ann and isinstance(ann, type) and issubclass(ann, BaseModel):
                    parsed = PModel.model_validate(params)
                    if isinstance(parsed, ann):
                        result = fn(parsed)
                    elif hasattr(parsed, arg_name):
                        result = fn(getattr(parsed, arg_name))
                    else:
                        result = fn(parsed)
                else:
                    parsed = PModel.model_validate(params).model_dump()
                    result = fn(**parsed)
            else:
                result = fn(**params)
            if inspect.isawaitable(result):
                result = await result
            if isinstance(result, BaseModel):
                result = result.model_dump()
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
