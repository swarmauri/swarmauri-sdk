from __future__ import annotations



from pydantic import BaseModel
from peagen.protocols._registry import register


class SubmitParams(BaseModel):
    pass


class SubmitResult(BaseModel):
    pass


TASK_SUBMIT = register(
    method="Task.submit.v1",
    params_model=SubmitParams,  # type: ignore[name-defined]
    result_model=SubmitResult,  # type: ignore[name-defined]
)
