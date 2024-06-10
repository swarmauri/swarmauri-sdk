from abc import ABC, abstractmethod
from typing import Optional, List, Any
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.core.tools.IParameter import IParameter


class ParameterBase(IParameter, ComponentBase, ABC):
    name: str
    type: str
    description: str
    required: bool = False
    enum: Optional[List[str]] = None
    resource: Optional[str] =  field(default=ResourceTypes.PARAMETER.value)
