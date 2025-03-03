from typing import Literal, Optional

from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.embeddings.IFeature import IFeature
from swarmauri_core.embeddings.ISaveModel import ISaveModel
from swarmauri_core.embeddings.IVectorize import IVectorize


@ComponentBase.register_model()
class EmbeddingBase(IVectorize, IFeature, ISaveModel, ComponentBase):
    resource: Optional[str] = Field(default=ResourceTypes.EMBEDDING.value, frozen=True)
    type: Literal["EmbeddingBase"] = "EmbeddingBase"
