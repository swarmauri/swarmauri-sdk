from abc import ABC, abstractmethod
from typing import Any

class ISaveModel(ABC):
    """
    Interface to abstract the ability to save and load models.
    """

    @abstractmethod
    def save_model(self, path: str) -> None:
        """
        Saves the model to the specified directory.

        Parameters:
        - path (str): The directory path where the model will be saved.
        """
        pass

    @abstractmethod
    def load_model(self, path: str) -> Any:
        """
        Loads a model from the specified directory.

        Parameters:
        - path (str): The directory path from where the model will be loaded.

        Returns:
        - Returns an instance of the loaded model.
        """
        pass