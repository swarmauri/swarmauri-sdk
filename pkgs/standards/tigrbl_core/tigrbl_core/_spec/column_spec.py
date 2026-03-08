from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, Optional

from .._spec.field_spec import FieldSpec as F
from .._spec.io_spec import IOSpec as IO
from .._spec.storage_spec import StorageSpec as S


class ColumnSpec(ABC):
    """Core interface for column declaration specs."""

    @property
    @abstractmethod
    def storage(self) -> S | None: ...

    @property
    @abstractmethod
    def field(self) -> F: ...

    @property
    @abstractmethod
    def io(self) -> IO: ...

    @property
    @abstractmethod
    def default_factory(self) -> Optional[Callable[[dict], Any]]: ...

    @property
    @abstractmethod
    def read_producer(self) -> Optional[Callable[[object, dict], Any]]: ...


__all__ = ["ColumnSpec"]
