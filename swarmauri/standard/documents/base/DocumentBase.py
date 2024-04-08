from abc import ABC, abstractmethod
from typing import Dict
from swarmauri.core.documents.IDocument import IDocument

class DocumentBase(IDocument, ABC):
    
    def __init__(self, doc_id,  content, metadata):
        self._id = doc_id
        self._content = content
        self._metadata = metadata        
    
    def __str__(self):
        return f"Document ID: {self.id}, Content: {self.content}, Metadata: {self.metadata}"

    def __repr__(self):
        return f"Document(id={self.id}, content={self.content}, metadata={self.metadata})"

    def as_dict(self):
        return self.__dict__
    
    @property
    def id(self) -> str:
        """
        Get the document's ID.
        """
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        """
        Set the document's ID.
        """
        self._id = value

    @property
    def content(self) -> str:
        """
        Get the document's content.
        """
        return self._content

    @content.setter
    def content(self, value: str) -> None:
        """
        Set the document's content.
        """
        if value:
            self._content = value
        else:
            raise ValueError('Cannot create a document with no content.')

    @property
    def metadata(self) -> Dict:
        """
        Get the document's metadata.
        """
        return self._metadata

    @metadata.setter
    def metadata(self, value: Dict) -> None:
        """
        Set the document's metadata.
        """
        self._metadata = value