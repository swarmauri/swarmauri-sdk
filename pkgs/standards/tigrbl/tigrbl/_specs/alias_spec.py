from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

from ..op.types import Arity, PersistPolicy

if TYPE_CHECKING:  # pragma: no cover
    from ..schema.types import SchemaArg


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
