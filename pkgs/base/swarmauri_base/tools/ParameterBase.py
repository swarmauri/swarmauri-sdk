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

    def __eq__(self, other: object) -> bool:  # pragma: no cover - simple equality
        if not isinstance(other, ParameterBase):
            return False
        self_dict = self.model_dump()
        other_dict = other.model_dump()
        self_dict.pop("id", None)
        other_dict.pop("id", None)
        return self_dict == other_dict
