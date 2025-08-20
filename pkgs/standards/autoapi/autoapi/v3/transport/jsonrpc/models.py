from __future__ import annotations

from typing import Any, Literal
import uuid
from pydantic import BaseModel, Field


class RPCRequest(BaseModel):
    """JSON-RPC 2.0 request envelope."""

    jsonrpc: Literal["2.0"] = "2.0"
    method: str
    params: dict[str, Any] = Field(default_factory=dict)
    id: str | int | None = Field(default_factory=lambda: str(uuid.uuid4()))


class RPCError(BaseModel):
    code: int
    message: str
    data: Any | None = None


class RPCResponse(BaseModel):
    """JSON-RPC 2.0 response envelope."""

    jsonrpc: Literal["2.0"] = "2.0"
    result: Any | None = None
    error: RPCError | None = None
    id: str | int | None = None
