from typing import Optional, List
from pydantic import Field

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.tools.IParameter import IParameter


@ComponentBase.register_model()
class ParameterBase(IParameter, ComponentBase):
    name: str
    description: str
    required: bool = False
    enum: Optional[List[str]] = None
    resource: Optional[str] = Field(default=ResourceTypes.PARAMETER.value)
    input_type: str
