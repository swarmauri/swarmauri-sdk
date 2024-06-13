from typing import List, Union, Any
from swarmauri.standard.vectors.concrete.Vector import Vector

from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.core.embeddings.IVectorize import IVectorize
from swarmauri.core.embeddings.IFeature import IFeature
from swarmauri.core.embeddings.ISaveModel import ISaveModel

class EmbeddingBase(IVectorize, IFeature, ISaveModel, ComponentBase):
    resource: Optional[str] =  Field(default=ResourceTypes.DOCUMENT.value)