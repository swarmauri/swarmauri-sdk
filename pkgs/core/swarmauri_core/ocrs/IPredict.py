from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Iterator


class IPredict(ABC):
    """
    Interface focusing on the basic properties and settings essential for defining models.
    """

    @abstractmethod
    def predict(self, *args, **kwargs) -> Any:
        """
        Generate predictions based on the input data provided to the model.
        """
        pass

    @abstractmethod
    async def apredict(self, *args, **kwargs) -> Any:
        """
        Generate predictions based on the input data provided to the model.
        """
        pass

    @abstractmethod
    def stream(self, *args, **kwargs) -> Iterator[Any]:
        """
        Generate predictions based on the input data provided to the model.
        """
        pass

    @abstractmethod
    async def astream(self, *args, **kwargs) -> AsyncIterator[Any]:
        """
        Generate predictions based on the input data provided to the model.
        """
        pass

    @abstractmethod
    def batch(self, *args, **kwargs) -> list[Any]:
        """
        Generate predictions based on the input data provided to the model.
        """
        pass

    @abstractmethod
    async def abatch(self, *args, **kwargs) -> list[Any]:
        """
        Generate predictions based on the input data provided to the model.
        """
        pass
