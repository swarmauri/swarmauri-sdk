from typing import Optional, Literal
from pydantic import Field
from swarmauri_core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.embeddings.IVectorize import IVectorize
from swarmauri_core.embeddings.IFeature import IFeature
from swarmauri_core.embeddings.ISaveModel import ISaveModel

class EmbeddingBase(IVectorize, IFeature, ISaveModel, ComponentBase):
    resource: Optional[str] =  Field(default=ResourceTypes.EMBEDDING.value, frozen=True)
    type: Literal['EmbeddingBase'] = 'EmbeddingBase'
        
