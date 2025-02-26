import warnings

from typing import Literal, Optional

from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.embeddings.IFeature import IFeature
from swarmauri_core.embeddings.ISaveModel import ISaveModel
from swarmauri_core.embeddings.IVectorize import IVectorize


warnings.warn(
    "Importing ComponentBase from swarmauri_core is deprecated and will be "
    "removed in a future version. Please use 'from swarmauri_base import "
    "ComponentBase'",
    DeprecationWarning,
    stacklevel=2,
)



@ComponentBase.register_model()
class EmbeddingBase(IVectorize, IFeature, ISaveModel, ComponentBase):
    resource: Optional[str] = Field(default=ResourceTypes.EMBEDDING.value, frozen=True)
    type: Literal["EmbeddingBase"] = "EmbeddingBase"
