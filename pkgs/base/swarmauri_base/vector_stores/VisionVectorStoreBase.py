from typing import Literal

from pydantic import Field

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes


class VisionVectorStoreBase(ComponentBase):
    resource: str | None = Field(
        default=ResourceTypes.EMBEDDING.value, frozen=True
    )
    type: Literal["VisionVectorStoreBase"] = "VisionVectorStoreBase"
