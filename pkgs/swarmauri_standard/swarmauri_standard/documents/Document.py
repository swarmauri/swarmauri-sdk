from typing import Literal
from swarmauri_base.documents.DocumentBase import DocumentBase
from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_type(DocumentBase, "Document")
class Document(DocumentBase):
    type: Literal["Document"] = "Document"
