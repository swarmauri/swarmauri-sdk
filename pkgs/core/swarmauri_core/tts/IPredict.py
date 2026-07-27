from abc import ABC, abstractmethod


class IPredict(ABC):
    """
    Interface focusing on the basic properties and settings essential for
    defining models.
    """

    @abstractmethod
    def predict(self, *args, **kwargs) -> any:
        """
        Generate predictions based on the input data provided to the model.
        """

    @abstractmethod
    async def apredict(self, *args, **kwargs) -> any:
        """
        Generate predictions based on the input data provided to the model.
        """

    @abstractmethod
    def stream(self, *args, **kwargs) -> any:
        """
        Generate predictions based on the input data provided to the model.
        """

    @abstractmethod
    async def astream(self, *args, **kwargs) -> any:
        """
        Generate predictions based on the input data provided to the model.
        """

    @abstractmethod
    def batch(self, *args, **kwargs) -> any:
        """
        Generate predictions based on the input data provided to the model.
        """

    @abstractmethod
    async def abatch(self, *args, **kwargs) -> any:
        """
        Generate predictions based on the input data provided to the model.
        """
