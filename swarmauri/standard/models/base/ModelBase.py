from abc import ABC, abstractmethod
from typing import Any, Union, Optional
from dataclasses import dataclass, field
from swarmauri.core.models.IModel import IModel
from swarmauri.core.models.IPredict import IPredict
from swarmauri.core.BaseComponent import BaseComponent, ResourceTypes

@dataclass
class ModelBase(IPredict, IModel, BaseComponent):
    model_name: Optional[str] = None
    resource: Optional[str] =  field(default=ResourceTypes.MODEL.value)

    def __post_init__(self):
        if not self.model_name:
            raise ValueError('Must define model_name.')
            
    @property
    def model_name(self):
        return self._model_name
    
    @model_name.setter
    def model_name(self, value: Union[str, None]) -> None:
        """
        Property setter that sets the name of the model.

        Parameters:
        - value (str): The new name of the model.
        """
        self._model_name = value