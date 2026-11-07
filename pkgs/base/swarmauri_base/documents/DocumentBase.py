from typing import Literal

from pydantic import ConfigDict, Field
from swarmauri_core.documents.IDocument import IDocument
from swarmauri_core.vectors.IVector import IVector

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes


@ComponentBase.register_model()
class DocumentBase(IDocument, ComponentBase):
    content: str
    metadata: dict = {}
    embedding: IVector | None = None
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)
    resource: str | None = Field(
        default=ResourceTypes.DOCUMENT.value, frozen=True
    )
    type: Literal["DocumentBase"] = "DocumentBase"
