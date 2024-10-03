from typing import Optional, Literal
from pydantic import Field
from swarmauri_core.ComponentBase import ComponentBase, ResourceTypes

class VisionEmbeddingBase(ComponentBase):
    resource: Optional[str] =  Field(default=ResourceTypes.EMBEDDING.value, frozen=True)
    type: Literal['VisionEmbeddingBase'] = 'VisionEmbeddingBase'