from typing import Optional, Any
from swarmauri.core.vectors.IVector import IVector
from swarmauri.standard.documents.base.EmbeddedBase import EmbeddedBase

class EmbeddedDocument(EmbeddedBase):
    def __init__(self, id,  content, metadata, embedding: Optional[IVector] = None):
        EmbeddedBase.__init__(self, id=id, content=content, metadata=metadata, embedding=embedding)
