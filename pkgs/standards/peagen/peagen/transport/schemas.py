from __future__ import annotations
from typing import Any, Dict, Optional, Union, Literal

from pydantic import BaseModel, Field


class RPCErrorData(BaseModel):
    code: int = Field(..., example=-32601)
    message: str = Field(..., example="Method not found")
    data: Optional[Any] = Field(None, example={"detail": "extra info"})


class RPCError(Exception):
    """Exception carrying JSON-RPC error details."""

    def __init__(self, *, code: int, message: str, data: Any | None = None) -> None:
        self.error = RPCErrorData(code=code, message=message, data=data)
        super().__init__(message)

    def model_dump(self) -> Dict[str, Any]:
        return self.error.model_dump()


class RPCRequest(BaseModel):
    jsonrpc: Literal["2.0"] = Field("2.0", example="2.0")
    id: Optional[Union[int, str]] = Field(
        None,
        description="Client request-id (optional). If omitted, gateway will supply one.",
        examples=[1, "abc123"],
    )
    method: str = Field(..., example="Task.submit")
    params: Optional[Dict[str, Any]] = Field(default_factory=dict)


class RPCResponse(BaseModel):
    jsonrpc: Literal["2.0"] = Field("2.0", example="2.0")
    id: Union[int, str, None] = Field(..., example=1)
    # exactly one of result / error is present
    result: Optional[Any] = Field(None, example={"taskId": "01HX..."})
    error: Optional[RPCErrorData] = None
