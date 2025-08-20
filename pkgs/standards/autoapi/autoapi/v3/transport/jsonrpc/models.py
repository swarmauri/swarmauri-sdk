from __future__ import annotations

from typing import Any, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class RPCRequest(BaseModel):
    """JSON-RPC 2.0 request envelope."""

    jsonrpc: Literal["2.0"] = "2.0"
    method: str
    params: dict[str, Any] = Field(default_factory=dict)
    id: UUID | None = Field(
        default_factory=uuid4,
        examples=[uuid4()],
    )


class RPCError(BaseModel):
    code: int
    message: str
    data: Any | None = None


class RPCResponse(BaseModel):
    """JSON-RPC 2.0 response envelope."""

    jsonrpc: Literal["2.0"] = "2.0"
    result: Any | None = None
    error: RPCError | None = None
    id: UUID | None = Field(
        default=None,
        examples=[uuid4()],
    )
