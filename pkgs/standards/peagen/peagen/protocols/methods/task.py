from __future__ import annotations


from pydantic import BaseModel, ConfigDict

from peagen.protocols._registry import register


class SubmitParams(BaseModel):
    """Parameters for the ``Task.submit`` RPC method."""

    model_config = ConfigDict(extra="forbid")

    template_set: str
    inputs: dict
    priority: int | None = None


class SubmitResult(BaseModel):
    """Result envelope returned by ``Task.submit``."""

    model_config = ConfigDict(extra="forbid")

    taskId: str


class PatchParams(BaseModel):
    """Parameters for the ``Task.patch`` RPC method."""

    model_config = ConfigDict(extra="forbid")

    taskId: str
    changes: dict


class PatchResult(BaseModel):
    """Patched task representation."""

    model_config = ConfigDict(extra="forbid")

    id: str
    tenant_id: str
    git_reference_id: str | None = None
    pool: str
    payload: dict
    status: str
    note: str | None = None
    spec_hash: str
    date_created: str
    last_modified: str
    labels: list[str] | None = None
    result: dict | None = None


class SimpleSelectorParams(BaseModel):
    """Common selector parameter used by control RPC methods."""

    model_config = ConfigDict(extra="forbid")

    selector: str


class CountResult(BaseModel):
    """Result model containing only a count field."""

    model_config = ConfigDict(extra="forbid")

    count: int


class GetParams(BaseModel):
    """Parameters for ``Task.get``."""

    model_config = ConfigDict(extra="forbid")

    taskId: str


class GetResult(PatchResult):
    """Result returned by ``Task.get`` -- identical to :class:`PatchResult`."""



TASK_SUBMIT = register(
    method="Task.submit",
    params_model=SubmitParams,
    result_model=SubmitResult,
)


TASK_PATCH = register(
    method="Task.patch",
    params_model=PatchParams,
    result_model=PatchResult,
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
