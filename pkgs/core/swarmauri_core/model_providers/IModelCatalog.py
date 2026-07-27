"""Model catalog interface."""

from abc import ABC, abstractmethod
from typing import Any, Iterable, Optional


class IModelCatalog(ABC):
    @abstractmethod
    def list_models(self) -> Iterable[Any]: ...

    @abstractmethod
    def get_model(self, name: str) -> Optional[Any]: ...

    @abstractmethod
    def refresh(self) -> Iterable[Any]: ...

    @abstractmethod
    async def arefresh(self) -> Iterable[Any]: ...
