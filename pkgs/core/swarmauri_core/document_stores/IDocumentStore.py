from abc import ABC, abstractmethod
from typing import List, Union

from swarmauri_core.documents.IDocument import IDocument


class IDocumentStore(ABC):
    """
    Interface for a Document Store responsible for storing, indexing, and
    retrieving documents.
    """

    @abstractmethod
    def add_document(self, document: IDocument) -> None:
        """
        Stores a single document in the document store.

        Parameters:
        - document (IDocument): The document to store.
        """

    @abstractmethod
    def add_documents(self, documents: list[IDocument]) -> None:
        """
        Stores multiple documents in the document store.

        Parameters:
        - documents (List[IDocument]): The list of documents to store.
        """

    @abstractmethod
    def get_document(self, doc_id: str) -> Union[IDocument, None]:
        """
        Retrieves a document by its ID.

        Parameters:
        - doc_id (str): The unique identifier for the document.

        Returns:
        - Union[IDocument, None]: The requested document, or None if not found.
        """

    @abstractmethod
    def get_all_documents(self) -> list[IDocument]:
        """
        Retrieves all documents stored in the document store.

        Returns:
        - List[IDocument]: A list of all documents.
        """

    @abstractmethod
    def delete_document(self, doc_id: str) -> None:
        """
        Deletes a document from the document store by its ID.

        Parameters:
        - doc_id (str): The unique identifier of the document to delete.
        """

    @abstractmethod
    def update_document(
        self, doc_id: str, updated_document: IDocument
    ) -> None:
        """
        Updates a document in the document store.

        Parameters:
        - doc_id (str): The unique identifier for the document to update.
        - updated_document (IDocument): The updated document object.

        Note: It's assumed that the updated_document will retain the same
        doc_id but may have different content or metadata.
        """

    @abstractmethod
    def document_count(self) -> int:
        pass
