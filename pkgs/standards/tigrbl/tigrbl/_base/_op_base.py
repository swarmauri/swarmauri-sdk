from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from .._spec.op_spec import OpSpec


class OpBase(OpSpec, ABC):
    """Abstract operation descriptor base built on top of :class:`OpSpec`."""

    __slots__ = ()

    @abstractmethod
    def __set_name__(self, owner: type, name: str) -> None: ...

    @abstractmethod
    def install_engines(
        self, *, router: Any | None = None, model: type | None = None
    ) -> None: ...
