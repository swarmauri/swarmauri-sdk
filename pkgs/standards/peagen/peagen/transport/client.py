# """Minimal helper for AutoAPI JSON-RPC requests."""

# from __future__ import annotations

# from typing import Any, Mapping, Type, TypeVar, Union, overload

# import httpx
# from pydantic import BaseModel
# from autoapi_client import AutoAPIClient

# R = TypeVar("R", bound=BaseModel)
# RPC_TIMEOUT: float = 30.0


# class RPCTransportError(RuntimeError):
#     """Low-level HTTP or JSON parse failure."""


# class RPCResponseError(RuntimeError):
#     """Gateway returned a JSON-RPC error object."""

#     def __init__(self, err: Mapping[str, Any]):
#         super().__init__(f"(code {err.get('code')}) {err.get('message')}")
#         self.code: int = err.get("code", -32000)
#         self.message: str = err.get("message", "unknown")
#         self.data: Mapping[str, Any] | None = err.get("data")


# @overload
# def send_jsonrpc_request(
#     gateway_url: str,
#     method: str,
#     params: Mapping[str, Any] | BaseModel,
#     *,
#     expect: None = ...,  # noqa: D417
#     timeout: float = RPC_TIMEOUT,
# ) -> dict: ...


# @overload
# def send_jsonrpc_request(
#     gateway_url: str,
#     method: str,
#     params: Mapping[str, Any] | BaseModel,
#     *,
#     expect: Type[R],
#     timeout: float = RPC_TIMEOUT,
# ) -> R: ...


# def send_jsonrpc_request(
#     gateway_url: str,
#     method: str,
#     params: Mapping[str, Any] | BaseModel,
#     *,
#     expect: Type[R] | None = None,
#     timeout: float = RPC_TIMEOUT,
# ) -> Union[dict, R]:
#     """Call *method* on *gateway_url* using :class:`AutoAPIClient`."""

#     try:
#         with AutoAPIClient(gateway_url, client=httpx.Client(timeout=timeout)) as rpc:
#             return rpc.call(method, params=params, out_schema=expect)
#     except httpx.HTTPError as exc:  # pragma: no cover
#         raise RPCTransportError(str(exc)) from exc
#     except RuntimeError as exc:  # pragma: no cover
#         raise RPCResponseError({"message": str(exc)}) from exc
