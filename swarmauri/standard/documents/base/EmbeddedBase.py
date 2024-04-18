from abc import ABC
from typing import List, Any, Optional
from swarmauri.core.documents.IEmbed import IEmbed
from swarmauri.standard.vectors.base.VectorBase import VectorBase
from swarmauri.standard.documents.base.DocumentBase import DocumentBase

class EmbeddedBase(DocumentBase, IEmbed, ABC):
    def __init__(self, id, content, metadata, embedding: VectorBase):
        DocumentBase.__init__(self, id, content, metadata)
        self._embedding = embedding
        
    @property
    def embedding(self) -> VectorBase:
        return self._embedding

    @embedding.setter
    def embedding(self, value: VectorBase) -> None:
        self._embedding = value

    def __str__(self):
        return f"EmbeddedDocument ID: {self.id}, Content: {self.content}, Metadata: {self.metadata}, embedding={self.embedding}"

    def __repr__(self):
        return f"EmbeddedDocument(id={self.id}, content={self.content}, metadata={self.metadata}, embedding={self.embedding})"

    def to_dict(self):
        document_dict = super().to_dict()
        document_dict.update({
            "type": self.__class__.__name__,
            "embedding": self.embedding.to_dict() if hasattr(self.embedding, 'to_dict') else self.embedding
            })

        return document_dict

    @classmethod
    def from_dict(cls, data):
        data.pop("type", None) 
        embedding_data = data.pop("embedding", None)
        if embedding_data:
            embedding_type = embedding_data.pop('type', None)
            if embedding_type:
                module = importlib.import_module(f"swarmauri.standard.vectors.concrete.{embedding_type}")
                embedding_class = getattr(module, embedding_type)
                embedding = embedding_class.from_dict(**embedding_data)
            else:
                embedding = None
        else:
            embedding = None
        return cls(**data, embedding=embedding)