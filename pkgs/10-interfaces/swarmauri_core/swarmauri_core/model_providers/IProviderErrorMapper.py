"""Provider error mapping interface."""

from abc import ABC, abstractmethod
from typing import Any


class IProviderErrorMapper(ABC):
    @abstractmethod
    def map_error(self, error: BaseException | Any) -> BaseException: ...
