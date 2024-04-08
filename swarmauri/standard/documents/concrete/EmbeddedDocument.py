from typing import Optional, Any
from swarmauri.standard.documents.base.DocumentBase import DocumentBase
from swarmauri.standard.documents.base.EmbeddedBase import EmbeddedBase

class EmbeddedDocument(DocumentBase, EmbeddedBase):
    def __init__(self, doc_id,  content, metadata, embedding: Optional[Any] = None):
        DocumentBase.__init__(self, doc_id=doc_id, content=content, metadata=metadata)
        EmbeddedBase.__init__(self, embedding=embedding)

