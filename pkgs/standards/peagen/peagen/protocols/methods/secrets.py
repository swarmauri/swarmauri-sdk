from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from peagen.protocols._registry import register


class AddParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    cipher: str
    tenant_id: str = Field("default", description="Tenant identifier")
    owner_user_id: str | None = Field(
        None, description="Optional ID of the user creating the secret"
    )
    version: int | None = None


class AddResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ok: bool


class GetParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    tenant_id: str = "default"


class GetResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    secret: str


class DeleteParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    tenant_id: str = "default"
    version: int | None = None


class DeleteResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ok: bool


SECRETS_ADD = register(
    method="Secrets.add",
    params_model=AddParams,
    result_model=AddResult,
)

SECRETS_GET = register(
    method="Secrets.get",
    params_model=GetParams,
    result_model=GetResult,
)

SECRETS_DELETE = register(
    method="Secrets.delete",
    params_model=DeleteParams,
    result_model=DeleteResult,
)
