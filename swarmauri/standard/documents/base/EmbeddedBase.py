from abc import ABC
from typing import List, Any, Optional
from swarmauri.core.documents.IEmbed import IEmbed
from swarmauri.core.vectors.IVector import IVector
from swarmauri.standard.documents.base.DocumentBase import DocumentBase

class EmbeddedBase(DocumentBase, IEmbed, ABC):
    def __init__(self, id, content, metadata, embedding: IVector):
        DocumentBase.__init__(self, id, content, metadata)
        self._embedding = embedding

    def __str__(self):
        return f"EmbeddedDocument ID: {self.id}, Content: {self.content}, Metadata: {self.metadata}, embedding={self.embedding}"

    def __repr__(self):
        return f"EmbeddedDocument(id={self.id}, content={self.content}, metadata={self.metadata}, embedding={self.embedding})"

    def to_dict(self):
        document_dict = DocumentBase.to_dict(self)
        document_dict.update({"type": self.__class__.__name__})
        document_dict.update({"embedding": self.embedding})
        return document_dict

    @classmethod
    def from_dict(cls, data):
        data.pop("type") 
        return cls(**data)
  
    @property
    def embedding(self) -> IVector:
        return self._embedding

    @embedding.setter
    def embedding(self, value: IVector) -> None:
        self._embedding = value