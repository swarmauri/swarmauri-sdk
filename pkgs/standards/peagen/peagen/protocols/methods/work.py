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
