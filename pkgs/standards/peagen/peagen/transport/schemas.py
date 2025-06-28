"""Backwards compatibility wrappers for protocol envelopes."""

from __future__ import annotations

from peagen.protocols import (
    Error as RPCErrorData,
    Request as RPCRequest,
    Response as RPCResponse,
)


class RPCError(Exception):
    """Exception carrying JSON-RPC error details."""

    def __init__(self, *, code: int, message: str, data: dict | None = None) -> None:
        self.error = RPCErrorData(code=code, message=message, data=data)
        super().__init__(message)

    def model_dump(self) -> dict:
        return self.error.model_dump()


__all__ = ["RPCRequest", "RPCResponse", "RPCError", "RPCErrorData"]
