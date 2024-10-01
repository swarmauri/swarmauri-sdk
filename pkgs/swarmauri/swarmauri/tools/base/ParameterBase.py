from typing import Optional, List, Any
from pydantic import Field
from swarmauri_core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.tools.IParameter import IParameter


class ParameterBase(IParameter, ComponentBase):
    name: str
    description: str
    required: bool = False
    enum: Optional[List[str]] = None
    resource: Optional[str] =  Field(default=ResourceTypes.PARAMETER.value)
    type: str # THIS DOES NOT USE LITERAL
