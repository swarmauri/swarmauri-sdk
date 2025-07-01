from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from .._registry import register


class FinishedParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    taskId: str
    status: str
    result: dict | None = None


class FinishedResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ok: bool


WORK_FINISHED = register(
    method="Work.finished",
    params_model=FinishedParams,
    result_model=FinishedResult,
)


class StartParams(BaseModel):
    """Parameters for the ``Work.start`` RPC method."""

    model_config = ConfigDict(extra="forbid")

    task: dict


class StartResult(BaseModel):
    """Return value for ``Work.start``."""

    model_config = ConfigDict(extra="forbid")

    accepted: bool


WORK_START = register(
    method="Work.start",
    params_model=StartParams,
    result_model=StartResult,
)


class CancelParams(BaseModel):
    """Parameters for the ``Work.cancel`` RPC method."""

    model_config = ConfigDict(extra="forbid")

    taskId: str


class CancelResult(BaseModel):
    """Return value for ``Work.cancel``."""

    model_config = ConfigDict(extra="forbid")

    ok: bool


WORK_CANCEL = register(
    method="Work.cancel",
    params_model=CancelParams,
    result_model=CancelResult,
)
