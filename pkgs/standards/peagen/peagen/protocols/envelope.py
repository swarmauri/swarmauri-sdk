from __future__ import annotations

from typing import Generic, Literal, Optional, TypeVar

from pydantic import BaseModel, TypeAdapter

P = TypeVar("P")
R = TypeVar("R")


class Error(BaseModel):
    code: int
    message: str
    data: Optional[dict] = None


class Request(BaseModel, Generic[P]):
    jsonrpc: Literal["2.0"] = "2.0"
    id: int | str
    method: str
    params: P


class Response(BaseModel, Generic[R]):
    jsonrpc: Literal["2.0"] = "2.0"
    id: int | str | None
    result: Optional[R] = None
    error: Optional[Error] = None

    @classmethod
    def ok(cls, *, id: int | str | None, result: R) -> "Response[R]":
        return cls(id=id, result=result)

    @classmethod
    def fail(cls, *, id: int | str | None, err: Error) -> "Response[None]":
        return cls(id=id, error=err)


# ---------- helpers for wiring into the dispatcher ----------


def parse_request(raw: dict) -> Request:
    """Runtime validation entry point used by the gateway."""
    structural = TypeAdapter(Request[dict]).validate_python(raw)
    return structural
