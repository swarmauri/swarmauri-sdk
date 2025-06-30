"""
send_jsonrpc_request – build ➜ POST ➜ parse a JSON-RPC 2.0 call.

* Strictly typed against peagen.transport.envelope.Response.
* Uses httpx.post with a configurable *timeout*.
"""
from __future__ import annotations

import httpx
import uuid
from typing import Any, Mapping, Type, TypeVar, Union, overload

from pydantic import BaseModel, ValidationError

from .builder import build_jsonrpc_request, RPCBuildError
from .envelope import Response, Error
from .error_codes import ErrorCode

# ---------- public types & defaults ----------
R = TypeVar("R", bound=BaseModel)
RPC_TIMEOUT: float = 30.0     # seconds


class RPCTransportError(RuntimeError):
    """Low-level HTTP or JSON parse failure."""


class RPCResponseError(RuntimeError):
    """Gateway returned a JSON-RPC *error* object."""
    def __init__(self, err: Error):
        super().__init__(f"(code {err.code}) {err.message}")
        self.code: int = err.code
        self.message: str = err.message
        self.data: dict[str, Any] | None = err.data


# ---------- public helper ----------
@overload
def send_jsonrpc_request(
    gateway_url: str,
    method: str,
    params: Mapping[str, Any] | BaseModel,
    *,
    expect: None = ...,
    timeout: float = RPC_TIMEOUT,
) -> Response[dict]: ...                                      # raw response

@overload
def send_jsonrpc_request(
    gateway_url: str,
    method: str,
    params: Mapping[str, Any] | BaseModel,
    *,
    expect: Type[R],
    timeout: float = RPC_TIMEOUT,
) -> R: ...                                                   # typed result


def send_jsonrpc_request(
    gateway_url: str,
    method: str,
    params: Mapping[str, Any] | BaseModel,
    *,
    expect: Type[R] | None = None,
    timeout: float = RPC_TIMEOUT,
) -> Union[Response[dict], R]:
    """
    Build → HTTP POST → parse a JSON-RPC request in one line.

    Raises
    ------
    RPCBuildError       – request could not be constructed.
    RPCTransportError   – network / HTTP / non-JSON response.
    RPCResponseError    – gateway returned a JSON-RPC error object.
    """
    # 1️⃣ build (and validate) envelope
    envelope = build_jsonrpc_request(method, params, id=str(uuid.uuid4()))

    # 2️⃣ transmit
    try:
        resp = httpx.post(
            gateway_url,
            json=envelope.model_dump(mode="json"),
            timeout=timeout,
        )
        resp.raise_for_status()
    except Exception as exc:                                   # noqa: BLE001
        raise RPCTransportError(f"HTTP transport failure: {exc}") from exc

    # 3️⃣ parse JSON-RPC response
    try:
        parsed: Response[Any] = Response[Any].model_validate(resp.json())
    except ValidationError as exc:
        raise RPCTransportError(f"Invalid JSON-RPC payload: {exc}") from exc

    if parsed.error is not None:                              # JSON-RPC error
        raise RPCResponseError(parsed.error)

    if expect is None:
        return parsed                                         # raw Response
    try:
        return expect.model_validate(parsed.result)           # typed Result
    except ValidationError as exc:
        raise RPCTransportError(
            f"Result failed validation as {expect.__name__}: {exc}"
        ) from exc
