from typing import Literal

from pydantic import Field
from swarmauri_core.embeddings.IFeature import IFeature
from swarmauri_core.embeddings.ISaveModel import ISaveModel
from swarmauri_core.embeddings.IVectorize import IVectorize

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes


@ComponentBase.register_model()
class EmbeddingBase(IVectorize, IFeature, ISaveModel, ComponentBase):
    resource: str | None = Field(
        default=ResourceTypes.EMBEDDING.value, frozen=True
    )
    type: Literal["EmbeddingBase"] = "EmbeddingBase"
