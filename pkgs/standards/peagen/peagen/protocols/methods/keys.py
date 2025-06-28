from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field
from typing import Dict

from peagen.protocols._registry import register


class UploadParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    public_key: str = Field(..., description="ASCII armored public key")


class UploadResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fingerprint: str


class FetchParams(BaseModel):
    model_config = ConfigDict(extra="forbid")


class FetchResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    keys: Dict[str, str]


class DeleteParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fingerprint: str


class DeleteResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ok: bool


KEYS_UPLOAD = register(
    method="Keys.upload.v1",
    params_model=UploadParams,
    result_model=UploadResult,
)

KEYS_FETCH = register(
    method="Keys.fetch.v1",
    params_model=FetchParams,
    result_model=FetchResult,
)

KEYS_DELETE = register(
    method="Keys.delete.v1",
    params_model=DeleteParams,
    result_model=DeleteResult,
)
