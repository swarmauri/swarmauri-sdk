from typing import Dict, Optional, Literal
from pydantic import Field, ConfigDict

from swarmauri_core.documents.IDocument import IDocument
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_standard.vectors.Vector import Vector


@ComponentBase.register_model()
class DocumentBase(IDocument, ComponentBase):
    content: str
    metadata: Dict = {}
    embedding: Optional[Vector] = None
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)
    resource: Optional[str] = Field(default=ResourceTypes.DOCUMENT.value, frozen=True)
    type: Literal["DocumentBase"] = "DocumentBase"
