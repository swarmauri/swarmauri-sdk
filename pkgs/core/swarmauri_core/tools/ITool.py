from abc import ABC, abstractmethod
from collections.abc import Awaitable
from typing import Any

ToolResult = Any | Awaitable[Any]


class ITool(ABC):
    @abstractmethod
    def call(self, *args: Any, **kwargs: Any) -> ToolResult: ...

    @abstractmethod
    def __call__(self, *args: Any, **kwargs: Any) -> ToolResult: ...

    @abstractmethod
    def batch(
        self, inputs: list[Any], *args: Any, **kwargs: Any
    ) -> list[ToolResult]: ...
