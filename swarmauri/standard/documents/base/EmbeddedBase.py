from abc import ABC
from typing import List, Any
from swarmauri.core.documents.IEmbed import IEmbed
from swarmauri.core.vectors.IVector import IVector

class EmbeddedBase(IEmbed, ABC):
    def __init__(self, embedding: IVector):
        self._embedding = embedding

    def __str__(self):
        return f"EmbeddedDocument ID: {self.id}, Content: {self.content}, Metadata: {self.metadata}, embedding={self.embedding}"

    def __repr__(self):
        return f"EmbeddedDocument(id={self.id}, content={self.content}, metadata={self.metadata}, embedding={self.embedding})"

    def to_dict(self):
        return self.__dict__

    @property
    def embedding(self) -> IVector:
        return self._embedding

    @embedding.setter
    def embedding(self, value: IVector) -> None:
        self._embedding = value