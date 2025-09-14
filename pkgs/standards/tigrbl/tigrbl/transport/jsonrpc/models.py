from __future__ import annotations

from typing import Any, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


def _uuid_examples(schema: dict[str, Any]) -> None:
    """Populate schema examples with a random UUID."""
    schema["examples"] = [str(uuid4())]


class RPCRequest(BaseModel):
    """JSON-RPC 2.0 request envelope."""

    jsonrpc: Literal["2.0"] = "2.0"
    method: str
    params: dict[str, Any] | list[Any] = Field(default_factory=dict)
    id: UUID | str | int | None = Field(
        default_factory=uuid4,
        json_schema_extra=_uuid_examples,
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
    id: UUID | str | int | None = Field(
        default=None,
        json_schema_extra=_uuid_examples,
    )
