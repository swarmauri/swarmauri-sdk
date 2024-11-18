from typing import Literal
from swarmauri.documents.base.DocumentBase import DocumentBase

class Document(DocumentBase):
    type: Literal['Document'] = 'Document'
