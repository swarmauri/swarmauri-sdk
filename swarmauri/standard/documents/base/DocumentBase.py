from abc import ABC
from typing import Dict, Optional
from pydantic import Field, ConfigDict
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.core.documents.IDocument import IDocument
from swarmauri.standard.vectors.concrete.Vector import Vector

class DocumentBase(IDocument, ComponentBase, ABC):
    content: str
    metadata: Dict = {}
    embedding: Optional[Vector] = None
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)
    resource: Optional[str] =  Field(default=ResourceTypes.DOCUMENT.value, frozen=True)