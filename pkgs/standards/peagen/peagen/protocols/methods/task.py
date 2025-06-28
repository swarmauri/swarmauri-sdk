from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, Field

from peagen.protocols._registry import register


class SubmitParams(BaseModel):
    template_set: str = Field(
        ..., description="Name of the template set to instantiate"
    )
    inputs: dict[str, str] = Field(
        ..., description="Template input variables (raw strings only)"
    )
    priority: int | None = Field(0, ge=0, le=9, description="Lower is higher priority")


class SubmitResult(BaseModel):
    task_id: Annotated[str, Field(pattern=r"^[A-Z0-9]{12}$")]


TASK_SUBMIT = register(
    method="Task.submit.v1",
    params_model=SubmitParams,
    result_model=SubmitResult,
)

__all__ = ["TASK_SUBMIT", "SubmitParams", "SubmitResult"]
