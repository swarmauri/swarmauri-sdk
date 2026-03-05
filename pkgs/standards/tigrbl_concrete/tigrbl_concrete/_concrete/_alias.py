from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from tigrbl_core._spec.alias_spec import AliasSpec
from .types import Arity, PersistPolicy
from ..schema.types import SchemaArg


@dataclass(frozen=True)
class Alias(AliasSpec):
    _alias: str
    _request_schema: Optional[SchemaArg] = None
    _response_schema: Optional[SchemaArg] = None
    _persist: Optional[PersistPolicy] = None
    _arity: Optional[Arity] = None
    _rest: Optional[bool] = None

    @property
    def alias(self) -> str:
        return self._alias

    @property
    def request_schema(self) -> Optional[SchemaArg]:
        return self._request_schema

    @property
    def response_schema(self) -> Optional[SchemaArg]:
        return self._response_schema

    @property
    def persist(self) -> Optional[PersistPolicy]:
        return self._persist

    @property
    def arity(self) -> Optional[Arity]:
        return self._arity

    @property
    def rest(self) -> Optional[bool]:
        return self._rest
