from typing import Optional, List, Any
from abc import ABC, abstractmethod
import json
from swarmauri.core.tools.ITool import ITool
        
class ToolBase(ITool, ABC):
    
    @abstractmethod
    def __init__(self, name, description, parameters=[]):
        self._name = name
        self._description = description
        self._parameters = parameters
        self.type = "function"
        self.function = {
            "name": name,
            "description": description,
        }
        
        # Dynamically constructing the parameters schema
        properties = {}
        required = []
        
        for param in parameters:
            properties[param.name] = {
                "type": param.type,
                "description": param.description,
            }
            if param.enum:
                properties[param.name]['enum'] = param.enum

            if param.required:
                required.append(param.name)
        
        self.function['parameters'] = {
            "type": "object",
            "properties": properties,
        }
        
        if required:  # Only include 'required' if there are any required parameters
            self.function['parameters']['required'] = required


    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    @property
    def parameters(self):
        return self._parameters

    def __iter__(self):
        yield ('type', self.type)
        yield ('function', self.function)
        

    def as_dict(self):
        return {'type': self.type, 'function': self.function}
        # return self.__dict__

    def to_json(obj):
        return json.dumps(obj, default=lambda obj: obj.__dict__)

    def __getstate__(self):
        return {'type': self.type, 'function': self.function}


    def __call__(self, *args, **kwargs):
        """
        Placeholder method for executing the functionality of the tool.
        Subclasses should override this method to define specific tool behaviors.

        Parameters:
        - *args: Variable length argument list.
        - **kwargs: Arbitrary keyword arguments.
        """
        raise NotImplementedError("Subclasses must implement the call_function method.")