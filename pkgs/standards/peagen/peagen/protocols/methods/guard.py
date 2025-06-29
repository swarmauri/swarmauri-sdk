from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from .._registry import register


class SetParams(BaseModel):
    """Parameters for the ``Guard.set`` RPC method."""

    model_config = ConfigDict(extra="forbid")

    label: str
    spec: dict


class SetResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ok: bool


GUARD_SET = register(
    method="Guard.set",
    params_model=SetParams,
    result_model=SetResult,
)
