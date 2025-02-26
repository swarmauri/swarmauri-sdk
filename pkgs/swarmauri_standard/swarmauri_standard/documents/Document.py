import warnings

from typing import Literal
from swarmauri_base.documents.DocumentBase import DocumentBase
from swarmauri_base.ComponentBase import ComponentBase


warnings.warn(
    "Importing ComponentBase from swarmauri_core is deprecated and will be "
    "removed in a future version. Please use 'from swarmauri_base import "
    "ComponentBase'",
    DeprecationWarning,
    stacklevel=2,
)



@ComponentBase.register_type(DocumentBase, "Document")
class Document(DocumentBase):
    type: Literal["Document"] = "Document"
