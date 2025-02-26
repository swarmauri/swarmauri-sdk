import warnings

from typing import Optional, Literal
from pydantic import Field

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes


warnings.warn(
    "Importing ComponentBase from swarmauri_core is deprecated and will be "
    "removed in a future version. Please use 'from swarmauri_base import "
    "ComponentBase'",
    DeprecationWarning,
    stacklevel=2,
)



class VisionDistanceBase(ComponentBase):
    resource: Optional[str] = Field(default=ResourceTypes.DISTANCE.value, frozen=True)
    type: Literal["VisionDistanceBase"] = "VisionDistanceBase"
