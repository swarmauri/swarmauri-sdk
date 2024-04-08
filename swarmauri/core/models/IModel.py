from abc import ABC, abstractmethod

class IModel(ABC):
    """
    Interface focusing on the basic properties and settings essential for defining models.
    """

    @property
    @abstractmethod
    def model_name(self) -> str:
        """
        Get the name of the model.
        """
        pass

    @model_name.setter
    @abstractmethod
    def model_name(self, value: str) -> None:
        """
        Set the name of the model.
        """
        pass