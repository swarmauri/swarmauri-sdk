from abc import ABC, abstractmethod

class IPredict(ABC):
    """
    Interface for making predictions with models.
    """

    @abstractmethod
    def predict(self, input_data) -> any:
        """
        Generate predictions based on the input data provided to the model.
        """
        pass