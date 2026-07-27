from typing import Literal

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.documents.DocumentBase import DocumentBase


@ComponentBase.register_type(DocumentBase, "Document")
class Document(DocumentBase):
    type: Literal["Document"] = "Document"
