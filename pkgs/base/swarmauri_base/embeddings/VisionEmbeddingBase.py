from typing import Literal

from pydantic import Field

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes


class VisionEmbeddingBase(ComponentBase):
    resource: str | None = Field(
        default=ResourceTypes.EMBEDDING.value, frozen=True
    )
    type: Literal["VisionEmbeddingBase"] = "VisionEmbeddingBase"
