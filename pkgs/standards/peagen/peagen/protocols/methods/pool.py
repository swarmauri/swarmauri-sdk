from __future__ import annotations

from pydantic import BaseModel, ConfigDict, RootModel

from .._registry import register


class CreateParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str


class CreateResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str


class JoinParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str


class JoinResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    memberId: str


class ListParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    poolName: str
    limit: int | None = None
    offset: int = 0


class ListResult(RootModel[list[dict]]):
    pass


POOL_CREATE = register(
    method="Pool.create",
    params_model=CreateParams,
    result_model=CreateResult,
)

POOL_JOIN = register(
    method="Pool.join",
    params_model=JoinParams,
    result_model=JoinResult,
)

POOL_LIST_TASKS = register(
    method="Pool.listTasks",
    params_model=ListParams,
    result_model=ListResult,
)
