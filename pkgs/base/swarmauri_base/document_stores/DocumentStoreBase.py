import json
from abc import abstractmethod
from typing import Literal

from pydantic import ConfigDict, Field
from swarmauri_core.document_stores.IDocumentStore import IDocumentStore
from swarmauri_core.documents.IDocument import IDocument

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes


@ComponentBase.register_model()
class DocumentStoreBase(IDocumentStore, ComponentBase):
    """
    Abstract base class for document stores, implementing the IDocumentStore
    interface.

    This class provides a standard API for adding, updating, getting, and
    deleting documents in a store.
    The specifics of storing (e.g., in a database, in-memory, or file system)
    are to be implemented by concrete subclasses.
    """

    resource: ResourceTypes = Field(default=ResourceTypes.DOCUMENT_STORE.value)
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)
    type: Literal["DocumentStoreBase"] = "DocumentStoreBase"

    @abstractmethod
    def add_document(self, document: IDocument) -> None:
        """
        Add a single document to the document store.

        Parameters:
        - document (IDocument): The document to be added to the store.
        """

    @abstractmethod
    def add_documents(self, documents: list[IDocument]) -> None:
        """
        Add multiple documents to the document store in a batch operation.

        Parameters:
        - documents (List[IDocument]): A list of documents to be added to the
          store.
        """

    @abstractmethod
    def get_document(self, doc_id: str) -> IDocument | None:
        """
        Retrieve a single document by its identifier.

        Parameters:
        - doc_id (str): The unique identifier of the document to retrieve.

        Returns:
        - Optional[IDocument]: The requested document if found; otherwise,
          None.
        """

    @abstractmethod
    def get_all_documents(self) -> list[IDocument]:
        """
        Retrieve all documents stored in the document store.

        Returns:
        - List[IDocument]: A list of all documents in the store.
        """

    @abstractmethod
    def update_document(
        self, doc_id: str, updated_document: IDocument
    ) -> None:
        """
        Update a document in the document store.

        Parameters:
        - doc_id (str): The unique identifier of the document to update.
        - updated_document (IDocument): The updated document instance.
        """

    @abstractmethod
    def delete_document(self, doc_id: str) -> None:
        """
        Delete a document from the document store by its identifier.

        Parameters:
        - doc_id (str): The unique identifier of the document to delete.
        """

    def document_count(self):
        return len(self.documents)

    def dump(self, file_path):
        with open(file_path, "w") as f:
            json.dumps([each.__dict__ for each in self.documents], f, indent=4)

    def load(self, file_path):
        with open(file_path, "r") as f:
            self.documents = json.loads(f)
