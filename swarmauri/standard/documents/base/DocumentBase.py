from abc import ABC
from typing import Dict
from pydantic import Field, ConfigDict
from swarmauri.core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri.core.documents.IDocument import IDocument
from swarmauri.core.vectors.IVector import IVector

class DocumentBase(IDocument, ComponentBase, ABC):
    content: str
    metadata: Dict = {}
    embedding: IVector = None
    model_config = ConfigDict(extra='forbid', arbitrary_types_allowed=True)
    resource: Optional[str] =  Field(default=ResourceTypes.DOCUMENT.value)