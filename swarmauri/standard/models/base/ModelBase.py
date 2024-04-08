from abc import ABC, abstractmethod
from typing import Any
from ....core.models.IModel import IModel

class ModelBase(IModel, ABC):
    """
    Concrete implementation of the IModel abstract base class.
    This version includes managing the model name through a property and a setter.
    """
    @abstractmethod
    def __init__(self, model_name: str):
        self._model_name = model_name
    
    @property
    def model_name(self):
        return self._model_name
    
    @model_name.setter
    def model_name(self, value: str) -> None:
        """
        Property setter that sets the name of the model.

        Parameters:
        - value (str): The new name of the model.
        """
        self._model_name = value
       
    
