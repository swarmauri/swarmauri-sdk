from __future__ import annotations


from typing import Dict

from pydantic import BaseModel, ConfigDict

from peagen.protocols._registry import register


class SubmitParams(BaseModel):
    model_config = ConfigDict(extra="allow")

    pool: str
    payload: Dict
    taskId: str | None = None


class SubmitResult(BaseModel):
    model_config = ConfigDict(extra="allow")

    taskId: str


TASK_SUBMIT = register(
    method="Task.submit.v1",
    params_model=SubmitParams,
    result_model=SubmitResult,
)
