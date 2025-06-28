from __future__ import annotations


from pydantic import BaseModel, ConfigDict

from peagen.protocols._registry import register


class SubmitParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pool: str
    payload: dict


class SubmitResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task_id: str


TASK_SUBMIT = register(
    method="Task.submit.v1",
    params_model=SubmitParams,
    result_model=SubmitResult,
)
