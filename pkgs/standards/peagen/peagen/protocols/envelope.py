from __future__ import annotations

from typing import Generic, Literal, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, TypeAdapter

P = TypeVar("P")
R = TypeVar("R")


class Error(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: int
    message: str
    data: Optional[dict] = None


class Request(BaseModel, Generic[P]):
    model_config = ConfigDict(extra="forbid")

    jsonrpc: Literal["2.0"] = "2.0"
    id: int | str
    method: str
    params: P


class Response(BaseModel, Generic[R]):
    model_config = ConfigDict(extra="forbid")

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


# -------- helpers for wiring into the dispatcher ---------


def parse_request(raw: dict) -> Request:
    """Validate an untyped request before dispatch."""
    structural = TypeAdapter(Request[dict]).validate_python(raw)
    return structural
