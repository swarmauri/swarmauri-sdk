from typing import Any, Optional
from abc import ABC
from swarmauri.core.agents.IAgent import IAgent
from swarmauri.core.models.IModel import IModel



class AgentBase(IAgent, ABC):
    def __init__(self, model: IModel):
        self._model = model

    @property
    def model(self) -> IModel:
        return self._model
    
    @model.setter
    def model(self, value) -> None:
        self._model = value        

    def exec(self, input_str: Optional[Any]) -> Any:
        raise NotImplementedError('The `exec` function has not been implemeneted on this class.')
    
    def __getattr__(self, name):
        # Example of transforming attribute name from simplified to internal naming convention
        internal_name = f"_{name}"
        if internal_name in self.__dict__:
            return self.__dict__[internal_name]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def __setattr__(self, name, value):
        # Direct assignment to the __dict__ to bypass any potential infinite recursion
        # from setting attributes that do not explicitly exist.
        object.__setattr__(self, name, value) 
        
        
    def __str__(self):
        class_name = self.__class__.__name__
        variables_str = ", ".join(f"{k}={v}" for k, v in self.__dict__.items())
        return f"<{class_name} {variables_str}>"
        
    def __repr__(self):
        class_name = self.__class__.__name__
        variables_str = ", ".join(f"{k}={v}" for k, v in self.__dict__.items())
        return f"{class_name} ({variables_str})"