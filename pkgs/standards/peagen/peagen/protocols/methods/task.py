from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from peagen.protocols._registry import register


TASK_SUBMIT = register(
    method="Task.submit.v1",
    params_model=SubmitParams,
    result_model=SubmitResult,
)
