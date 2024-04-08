from abc import ABC, abstractmethod
from typing import Any, Optional
from swarmauri.core.models.IModel import IModel

class IAgent(ABC):

    @abstractmethod
    def exec(self, input_data: Optional[Any]) -> Any:
        """
        Executive method that triggers the agent's action based on the input data.
        """
        pass
    
    @property
    @abstractmethod
    def model(self) -> IModel:
        """
        The model property describes the computational model used by the agent.
        """
        pass
    
    @model.setter
    @abstractmethod
    def model(self) -> IModel:

        pass
