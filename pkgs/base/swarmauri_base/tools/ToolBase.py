from abc import ABC, abstractmethod
from typing import Optional, List, Any, Literal
from pydantic import Field
from swarmauri_core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.tools.base.ParameterBase import ParameterBase as Parameter
from swarmauri_core.tools.ITool import ITool


class ToolBase(ITool, ComponentBase, ABC):
    name: str
    description: Optional[str] = None
    parameters: List[Parameter] = Field(default_factory=list)
    resource: Optional[str] = Field(default=ResourceTypes.TOOL.value)
    type: Literal["ToolBase"] = "ToolBase"

    def call(self, *args, **kwargs):
        return self.__call__(*args, **kwargs)

    @abstractmethod
    def __call__(self, *args, **kwargs):
        raise NotImplementedError("Subclasses must implement the __call__ method.")


# #def __getstate__(self):
# return {'type': self.type, 'function': self.function}


# def __iter__(self):
#    yield ('type', self.type)
#    yield ('function', self.function)

# @property
# def function(self):
#     # Dynamically constructing the parameters schema
#     properties = {}
#     required = []

#     for param in self.parameters:
#         properties[param.name] = {
#             "type": param.type,
#             "description": param.description,
#         }
#         if param.enum:
#             properties[param.name]['enum'] = param.enum

#         if param.required:
#             required.append(param.name)

#     function = {
#         "name": self.name,
#         "description": self.description,
#         "parameters": {
#             "type": "object",
#             "properties": properties,
#         }
#     }

#     if required:  # Only include 'required' if there are any required parameters
#         function['parameters']['required'] = required
#     return function

# def as_dict(self):
#    #return asdict(self)
#     return {'type': self.type, 'function': self.function}
