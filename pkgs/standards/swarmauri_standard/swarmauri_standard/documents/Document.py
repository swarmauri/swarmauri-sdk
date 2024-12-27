from typing import Literal
from swarmauri_base.documents.DocumentBase import DocumentBase

class Document(DocumentBase):
    type: Literal['Document'] = 'Document'
