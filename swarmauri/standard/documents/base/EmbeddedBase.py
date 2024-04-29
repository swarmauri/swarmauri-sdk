from abc import ABC
from typing import List, Any, Optional
import importlib
from swarmauri.core.documents.IEmbed import IEmbed
from swarmauri.standard.vectors.base.VectorBase import VectorBase
from swarmauri.standard.documents.base.DocumentBase import DocumentBase

class EmbeddedBase(DocumentBase, IEmbed, ABC):
    def __init__(self, id: str = "", content: str = "", metadata: dict = {}, embedding: VectorBase = None):
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
        vector_data = data.pop("embedding", None)
        if vector_data:
            vector_type = vector_data.pop('type', None)
            if vector_type:
                module = importlib.import_module(f"swarmauri.standard.vectors.concrete.{vector_type}")
                vector_class = getattr(module, vector_type)
                vector = vector_class.from_dict(vector_data)
            else:
                vector = None
        else:
            vector = None 
        return cls(**data, embedding=vector)