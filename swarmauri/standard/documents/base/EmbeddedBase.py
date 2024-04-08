from abc import ABC
from typing import List, Any
from swarmauri.core.documents.IEmbed import IEmbed
from swarmauri.core.vectors.IVector import IVector

class EmbeddedBase(IEmbed, ABC):
    def __init__(self, embedding):
        self._embedding = embedding
            
    @property
    def embedding(self) -> IVector:
        return self._embedding

    @embedding.setter
    def embedding(self, value: IVector) -> None:
        self._embedding = value