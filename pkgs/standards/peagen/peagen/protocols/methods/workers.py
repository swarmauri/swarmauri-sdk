from __future__ import annotations

from pydantic import BaseModel, ConfigDict, RootModel

from peagen.protocols._registry import register


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


WORKER_REGISTER = register(
    method="Worker.register",
    params_model=RegisterParams,
    result_model=RegisterResult,
)


class HeartbeatParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    workerId: str
    metrics: dict
    pool: str | None = None
    url: str | None = None


class HeartbeatResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ok: bool


WORKER_HEARTBEAT = register(
    method="Worker.heartbeat",
    params_model=HeartbeatParams,
    result_model=HeartbeatResult,
)


class ListParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pool: str | None = None


class WorkerInfo(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    pool: str | None = None
    url: str | None = None
    advertises: dict | None = None
    handlers: list[str] | None = None
    last_seen: int | None = None


class ListResult(RootModel[list[WorkerInfo]]):
    model_config = ConfigDict(extra="forbid")


WORKER_LIST = register(
    method="Worker.list",
    params_model=ListParams,
    result_model=ListResult,
)


class WorkStartParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task: dict


class WorkStartResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    accepted: bool


WORK_START = register(
    method="Work.start",
    params_model=WorkStartParams,
    result_model=WorkStartResult,
)


class WorkCancelParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    taskId: str


class WorkCancelResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ok: bool


WORK_CANCEL = register(
    method="Work.cancel",
    params_model=WorkCancelParams,
    result_model=WorkCancelResult,
)


class WorkFinishedParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    taskId: str
    status: str
    result: dict | None = None


class WorkFinishedResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ok: bool


WORK_FINISHED = register(
    method="Work.finished",
    params_model=WorkFinishedParams,
    result_model=WorkFinishedResult,
)


class GuardSetParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: str
    spec: dict


class GuardSetResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ok: bool


GUARD_SET = register(
    method="Guard.set",
    params_model=GuardSetParams,
    result_model=GuardSetResult,
)
