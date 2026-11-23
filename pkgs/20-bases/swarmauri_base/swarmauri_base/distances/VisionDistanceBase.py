import warnings
from typing import Literal

from pydantic import Field

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes

warnings.warn(
    (
        "VisionDistanceBase is deprecated and will be removed from "
        "the active Swarmauri workspace by v0.12.0."
    ),
    DeprecationWarning,
    stacklevel=2,
)


class VisionDistanceBase(ComponentBase):
    """Deprecated compatibility base for vision distance components."""

    resource: str | None = Field(
        default=ResourceTypes.DISTANCE.value, frozen=True
    )
    type: Literal["VisionDistanceBase"] = "VisionDistanceBase"
