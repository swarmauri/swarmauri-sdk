"""Typed JSON-RPC request/response models."""

from __future__ import annotations

from pydantic import BaseModel, Field

from peagen.transport import RPCRequest, RPCResponse
from peagen.defaults import KEYS_UPLOAD, KEYS_FETCH, KEYS_DELETE


class KeysUploadParams(BaseModel):
    public_key: str


class KeysUploadResult(BaseModel):
    fingerprint: str


class KeysUploadRequest(RPCRequest):
    method: str = Field(default=KEYS_UPLOAD, const=True)
    params: KeysUploadParams


class KeysUploadResponse(RPCResponse):
    result: KeysUploadResult | None


class KeysFetchParams(BaseModel):
    pass


class KeysFetchResult(BaseModel):
    keys: dict[str, str]


class KeysFetchRequest(RPCRequest):
    method: str = Field(default=KEYS_FETCH, const=True)
    params: KeysFetchParams | None = None


class KeysFetchResponse(RPCResponse):
    result: KeysFetchResult | None


class KeysDeleteParams(BaseModel):
    fingerprint: str


class KeysDeleteResult(BaseModel):
    ok: bool


class KeysDeleteRequest(RPCRequest):
    method: str = Field(default=KEYS_DELETE, const=True)
    params: KeysDeleteParams


class KeysDeleteResponse(RPCResponse):
    result: KeysDeleteResult | None


__all__ = [
    "KeysUploadParams",
    "KeysUploadResult",
    "KeysUploadRequest",
    "KeysUploadResponse",
    "KeysFetchParams",
    "KeysFetchResult",
    "KeysFetchRequest",
    "KeysFetchResponse",
    "KeysDeleteParams",
    "KeysDeleteResult",
    "KeysDeleteRequest",
    "KeysDeleteResponse",
]
