from typing import Literal
from swarmauri.standard.documents.base.DocumentBase import DocumentBase

class Document(DocumentBase):
    type: Literal['Document'] = 'Document'