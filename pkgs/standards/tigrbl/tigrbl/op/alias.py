from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .alias_spec import AliasSpec
from .types import Arity, PersistPolicy
from ..schema.types import SchemaArg


@dataclass(frozen=True)
class Alias(AliasSpec):
    alias: str
    request_schema: Optional[SchemaArg] = None
    response_schema: Optional[SchemaArg] = None
    persist: Optional[PersistPolicy] = None
    arity: Optional[Arity] = None
    rest: Optional[bool] = None
