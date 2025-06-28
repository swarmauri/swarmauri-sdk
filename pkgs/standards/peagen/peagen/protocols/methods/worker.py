from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict

from peagen.protocols._registry import register


class RegisterParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    workerId: str
    pool: str
    url: str
    advertises: Dict
    handlers: Optional[List[str]] = None


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
    metrics: Dict
    pool: Optional[str] = None
    url: Optional[str] = None


class HeartbeatResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ok: bool


WORKER_HEARTBEAT = register(
    method="Worker.heartbeat",
    params_model=HeartbeatParams,
    result_model=HeartbeatResult,
)


class WorkerListParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pool: Optional[str] = None


class WorkerListResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    workers: List[Dict]


WORKER_LIST = register(
    method="Worker.list",
    params_model=WorkerListParams,
    result_model=WorkerListResult,
)


class WorkFinishedParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    taskId: str
    status: str
    result: Optional[Dict] = None


class WorkFinishedResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ok: bool


WORK_FINISHED = register(
    method="Work.finished",
    params_model=WorkFinishedParams,
    result_model=WorkFinishedResult,
)


class WorkStartParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task: Dict


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
