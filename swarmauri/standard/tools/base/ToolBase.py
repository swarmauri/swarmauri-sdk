from abc import ABC, abstractmethod
from typing import Optional, List, Any
from dataclasses import dataclass, field, asdict
import json
from swarmauri.core.tools.ITool import ITool
from swarmauri.core.BaseComponent import BaseComponent, ResourceTypes
from swarmauri.standard.tools.concrete.Parameter import Parameter

@dataclass
class ToolBase(ITool, BaseComponent, ABC):
    id: Optional[str] = None
    owner: Optional[str] = None
    name: Optional[str] = None
    host: Optional[str] = None
    members: List[str] = field(default_factory=list)
    #resource: Optional[str] = None
    description: Optional[str] = None
    parameters: List[Parameter] = field(default_factory=list)
    type: str = field(init=False, default="function")
    #function: dict = field(init=False)

    def __post_init__(self):
        if not self.name:
            self.name = self.__class__.__name__
            
        if not self.description:
            raise ValueError('Tool must have a description.')



        # Assuming BaseComponent initialization if needed
        BaseComponent.__init__(self, 
                               id=self.id, 
                               owner=self.owner, 
                               name=self.name, 
                               host=self.host, 
                               members=self.members, 
                               resource=ResourceTypes.TOOL.value)



    @property
    def parameters(self):
        return self._parameters

    @parameters.setter
    def parameters(self, value) -> None:
        self._parameters = value
    
    def call(self, *args, **kwargs):
        return self.__call__(*args, **kwargs)
    
    @abstractmethod
    def __call__(self, *args, **kwargs):
        """
        Placeholder method for executing the functionality of the tool.
        Subclasses should override this method to define specific tool behaviors.

        Parameters:
        - *args: Variable length argument list.
        - **kwargs: Arbitrary keyword arguments.
        """
        raise NotImplementedError("Subclasses must implement the __call__ method.")



    def __getstate__(self):
        return {'type': self.type, 'function': self.function}



    def __iter__(self):
        yield ('type', self.type)
        yield ('function', self.function)

    @property
    def function(self):
        # Dynamically constructing the parameters schema
        properties = {}
        required = []

        for param in self.parameters:
            properties[param.name] = {
                "type": param.type,
                "description": param.description,
            }
            if param.enum:
                properties[param.name]['enum'] = param.enum

            if param.required:
                required.append(param.name)

        function = {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": properties,
            }
        }
        
        if required:  # Only include 'required' if there are any required parameters
            function['parameters']['required'] = required
        return function

    def as_dict(self):
        #return asdict(self)
        return {'type': self.type, 'function': self.function}

    
    def to_json(self):
        return json.dumps(self, default=lambda self: self.__dict__)