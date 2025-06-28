from __future__ import annotations

from pydantic import BaseModel, ConfigDict, RootModel

from .._registry import register


class RegisterParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    workerId: str
    pool: str
    url: str
    advertises: dict
    handlers: list[str] | None = None


class RegisterResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ok: bool


class HeartbeatParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    workerId: str
    metrics: dict
    pool: str | None = None
    url: str | None = None


class HeartbeatResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ok: bool


class ListParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pool: str | None = None


class WorkerInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    pool: str
    url: str | None = None
    advertises: dict | None = None
    handlers: list[str] | None = None
    last_seen: int | None = None


class ListResult(RootModel[list[WorkerInfo]]):
    pass


WORKER_REGISTER = register(
    method="Worker.register",
    params_model=RegisterParams,
    result_model=RegisterResult,
)

WORKER_HEARTBEAT = register(
    method="Worker.heartbeat",
    params_model=HeartbeatParams,
    result_model=HeartbeatResult,
)

WORKER_LIST = register(
    method="Worker.list",
    params_model=ListParams,
    result_model=ListResult,
)
