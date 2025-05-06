from abc import ABC, abstractmethod


class IPredictVision(ABC):
    """
    Interface focusing on the basic properties and settings essential for defining models.
    """

    @abstractmethod
    def predict_vision(self, *args, **kwargs) -> any:
        """
        Generate predictions based on the input data provided to the model.
        """
        pass

    @abstractmethod
    async def apredict_vision(self, *args, **kwargs) -> any:
        """
        Generate predictions based on the input data provided to the model.
        """
        pass

    @abstractmethod
    def batch(self, *args, **kwargs) -> any:
        """
        Generate predictions based on the input data provided to the model.
        """
        pass

    @abstractmethod
    async def abatch(self, *args, **kwargs) -> any:
        """
        Generate predictions based on the input data provided to the model.
        """
        pass
