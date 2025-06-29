from __future__ import annotations
from typing import Optional

from pydantic import BaseModel, ConfigDict

from peagen.orm import Status
from peagen.protocols._registry import register
from peagen.schemas import TaskCreate


class SubmitParams(BaseModel):
    """Parameters for the ``Task.submit`` RPC method."""

    model_config = ConfigDict(extra="allow")

    task: TaskCreate


class SubmitResult(BaseModel):
    """Result envelope returned by ``Task.submit``."""

    model_config = ConfigDict(extra="forbid")

    pool: str
    payload: dict
    status: Status = Status.waiting
    note: str | None = None
    config_toml: str | None = None
    labels: list[str] | None = None
    result: Optional[dict] = None


# Resolve forward references after dynamic schema generation
SubmitParams.model_rebuild()


class SimpleSelectorParams(BaseModel):
    """Common selector parameter used by control RPC methods."""

    model_config = ConfigDict(extra="forbid")

    selector: str


class CountResult(BaseModel):
    """Result model containing only a count field."""

    model_config = ConfigDict(extra="forbid")

    count: int


class PatchParams(BaseModel):
    """Parameters for ``Task.patch``."""


class PatchResult(SubmitResult):
    """Result returned by ``Task.patch`` -- identical to :class:`SubmitResult`."""


class GetParams(BaseModel):
    """Parameters for ``Task.get``."""

    model_config = ConfigDict(extra="forbid")

    taskId: str


class GetResult(SubmitResult):
    """Result returned by ``Task.get`` -- identical to :class:`SubmitResult`."""


TASK_SUBMIT = register(
    method="Task.submit",
    params_model=SubmitParams,
    result_model=SubmitResult,
)


TASK_PATCH = register(
    method="Task.patch",
    params_model=SubmitParams,
    result_model=SubmitResult,
)

TASK_GET = register(
    method="Task.get",
    params_model=GetParams,
    result_model=GetResult,
)

TASK_CANCEL = register(
    method="Task.cancel",
    params_model=SimpleSelectorParams,
    result_model=CountResult,
)

TASK_PAUSE = register(
    method="Task.pause",
    params_model=SimpleSelectorParams,
    result_model=CountResult,
)

TASK_RESUME = register(
    method="Task.resume",
    params_model=SimpleSelectorParams,
    result_model=CountResult,
)

TASK_RETRY = register(
    method="Task.retry",
    params_model=SimpleSelectorParams,
    result_model=CountResult,
)

TASK_RETRY_FROM = register(
    method="Task.retry_from",
    params_model=SimpleSelectorParams,
    result_model=CountResult,
)
