from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

from .._spec.op_spec import Arity, PersistPolicy

if TYPE_CHECKING:  # pragma: no cover
    from .._spec.schema_spec import SchemaArg


class AliasSpec(ABC):
    @property
    @abstractmethod
    def alias(self) -> str: ...

    @property
    @abstractmethod
    def request_schema(self) -> Optional[SchemaArg]: ...

    @property
    @abstractmethod
    def response_schema(self) -> Optional[SchemaArg]: ...

    @property
    @abstractmethod
    def persist(self) -> Optional[PersistPolicy]: ...

    @property
    @abstractmethod
    def arity(self) -> Optional[Arity]: ...

    @property
    @abstractmethod
    def rest(self) -> Optional[bool]: ...
