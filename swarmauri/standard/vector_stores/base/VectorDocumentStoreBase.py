import json
from abc import ABC, abstractmethod
from typing import List, Optional
from swarmauri.core.documents.IDocument import IDocument
from swarmauri.core.vector_stores.IVectorStore import IVectorStore

class VectorDocumentStoreBase(IVectorStore, ABC):
    """
    Abstract base class for document stores, implementing the IVectorStore interface.

    This class provides a standard API for adding, updating, getting, and deleting documents in a vector store.
    The specifics of storing (e.g., in a database, in-memory, or file system) are to be implemented by concrete subclasses.
    """

    @abstractmethod
    def add_document(self, document: IDocument) -> None:
        """
        Add a single document to the document store.

        Parameters:
        - document (IDocument): The document to be added to the store.
        """
        pass

    @abstractmethod
    def add_documents(self, documents: List[IDocument]) -> None:
        """
        Add multiple documents to the document store in a batch operation.

        Parameters:
        - documents (List[IDocument]): A list of documents to be added to the store.
        """
        pass

    @abstractmethod
    def get_document(self, doc_id: str) -> Optional[IDocument]:
        """
        Retrieve a single document by its identifier.

        Parameters:
        - doc_id (str): The unique identifier of the document to retrieve.

        Returns:
        - Optional[IDocument]: The requested document if found; otherwise, None.
        """
        pass

    @abstractmethod
    def get_all_documents(self) -> List[IDocument]:
        """
        Retrieve all documents stored in the document store.

        Returns:
        - List[IDocument]: A list of all documents in the store.
        """
        pass

    @abstractmethod
    def update_document(self, doc_id: str, updated_document: IDocument) -> None:
        """
        Update a document in the document store.

        Parameters:
        - doc_id (str): The unique identifier of the document to update.
        - updated_document (IDocument): The updated document instance.
        """
        pass

    @abstractmethod
    def delete_document(self, doc_id: str) -> None:
        """
        Delete a document from the document store by its identifier.

        Parameters:
        - doc_id (str): The unique identifier of the document to delete.
        """
        pass

    def clear_documents(self) -> None:
        """
        Deletes all documents from the vector store

        """
        self.documents = []
    
    def document_count(self):
        return len(self.documents)
    
    def document_dumps(self) -> str:
        return json.dumps([each.to_dict() for each in self.documents])

    def document_dump(self, file_path: str) -> None:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump([each.to_dict() for each in self.documents], 
                f,
                ensure_ascii=False, 
                indent=4)  

    def document_loads(self, json_data: str) -> None:
        self.documents = [globals()[each['type']].from_dict(each) for each in json.loads(json_data)]

    def document_load(self, file_path: str) -> None:
        with open(file_path, 'r', encoding='utf-8') as f:
            self.documents = [globals()[each['type']].from_dict(each) for each in json.load(file_path)]

