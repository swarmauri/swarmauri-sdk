from __future__ import annotations

from enum import IntEnum
from typing import Any

from peagen.transport.jsonrpc import RPCException


class GatewayError(IntEnum):
    """JSON-RPC error codes used by the gateway."""

    DUPLICATE_SPEC = -32001
    STATE_CONFLICT = -32002
    SERVICE_UNAVAILABLE = -32003
    RATE_LIMITED = -32004
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32099


__all__ = ["GatewayError", "raise_rpc"]


def raise_rpc(code: GatewayError, message: str, **data: Any) -> None:
    """Raise an :class:`RPCException` with *code*, *message* and *data*."""

    raise RPCException(code=int(code), message=message, data=data or None)
