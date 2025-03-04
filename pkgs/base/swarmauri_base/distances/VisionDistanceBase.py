from typing import Optional, Literal
from pydantic import Field

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes


class VisionDistanceBase(ComponentBase):
    resource: Optional[str] = Field(default=ResourceTypes.DISTANCE.value, frozen=True)
    type: Literal["VisionDistanceBase"] = "VisionDistanceBase"
