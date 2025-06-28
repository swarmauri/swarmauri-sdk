from __future__ import annotations

from typing import Dict, Optional, List

from pydantic import BaseModel, ConfigDict

from peagen.protocols._registry import register


class PoolNameParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str


class PoolCreateResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str


POOL_CREATE = register(
    method="Pool.create",
    params_model=PoolNameParams,
    result_model=PoolCreateResult,
)


class PoolJoinResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    memberId: str


POOL_JOIN = register(
    method="Pool.join",
    params_model=PoolNameParams,
    result_model=PoolJoinResult,
)


class PoolListParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    poolName: str
    limit: Optional[int] = None
    offset: int = 0


class PoolListResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tasks: List[Dict]


POOL_LIST_TASKS = register(
    method="Pool.listTasks",
    params_model=PoolListParams,
    result_model=PoolListResult,
)
