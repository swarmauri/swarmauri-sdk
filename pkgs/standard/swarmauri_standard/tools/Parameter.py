from typing import Any, List, Literal, Optional
from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.tools.IParameter import IParameter


class Parameter(IParameter, ComponentBase):
    resource: Optional[str] = Field(default=ResourceTypes.PARAMETER.value, frozen=True)
    name: str
    type: Literal["string", "number", "integer", "boolean", "array", "object"]
    description: str
    required: bool = False
    enum: Optional[List[Any]] = None
    default: Optional[Any] = None
