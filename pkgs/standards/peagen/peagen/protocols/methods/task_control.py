from __future__ import annotations

from typing import Dict

from pydantic import BaseModel, ConfigDict

from peagen.protocols._registry import register


class TaskIdSelectorParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    selector: str


class CountResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    count: int


class TaskIdParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    taskId: str


class PatchParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    taskId: str
    changes: Dict


class GenericResult(BaseModel):
    """Placeholder result model for miscellaneous RPC calls."""

    model_config = ConfigDict(extra="allow")


TASK_CANCEL = register(
    method="Task.cancel",
    params_model=TaskIdSelectorParams,
    result_model=CountResult,
)

TASK_PAUSE = register(
    method="Task.pause",
    params_model=TaskIdSelectorParams,
    result_model=CountResult,
)

TASK_RESUME = register(
    method="Task.resume",
    params_model=TaskIdSelectorParams,
    result_model=CountResult,
)

TASK_RETRY = register(
    method="Task.retry",
    params_model=TaskIdSelectorParams,
    result_model=CountResult,
)

TASK_RETRY_FROM = register(
    method="Task.retry_from",
    params_model=TaskIdSelectorParams,
    result_model=CountResult,
)

TASK_PATCH = register(
    method="Task.patch",
    params_model=PatchParams,
    result_model=GenericResult,
)

TASK_GET = register(
    method="Task.get",
    params_model=TaskIdParams,
    result_model=GenericResult,
)

GUARD_SET = register(
    method="Guard.set",
    params_model=PatchParams,
    result_model=GenericResult,
)
