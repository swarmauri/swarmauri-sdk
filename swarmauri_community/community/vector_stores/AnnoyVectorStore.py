import os
import json
import pickle
import tempfile
from typing import List, Union
from annoy import AnnoyIndex
from swarmauri.core.documents.IDocument import IDocument
from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.standard.vector_stores.base.SaveLoadStoreBase import SaveLoadStoreBase
from swarmauri.standard.vector_stores.base.VectorDocumentStoreRetrieveBase import VectorDocumentStoreRetrieveBase

from swarmauri.standard.vectorizers.concrete.Doc2VecVectorizer import Doc2VecVectorizer
#from swarmauri.standard.distances.concrete.CosineDistance import CosineDistance

class AnnoyVectorStore(SaveLoadStoreBase, VectorDocumentStoreRetrieveBase):
    """
    AnnoyVectorStore is a concrete implementation that integrates functionality
    for saving, loading, storing, and retrieving vector documents, leveraging Annoy as the backend.
    """

    def __init__(self, dimension: int, metric='euclidean', num_trees=10):
        self.dimension = dimension
        self.vectorizer = Doc2VecVectorizer()
        self.metric = metric
        self.num_trees = num_trees
        self.index = AnnoyIndex(dimension, metric)
        self.documents = []  # List of documents
        self.id_to_index = {}  # Mapping from document ID to index in Annoy
        SaveLoadStoreBase.__init__(self, self.vectorizer, [])

    def get_state(self) -> dict:
        """
        Retrieve the internal state of the vector store to be saved.
        
        Returns:
            dict: The internal state of the vector store.
        """
        return {
            'documents': [doc.to_dict() for doc in self.documents],
            'id_to_index': self.id_to_index
        }

    def set_state(self, state: dict) -> None:
        """
        Set the internal state of the vector store when loading.
        
        Parameters:
            state (dict): The state to set to the vector store.
        """
        self.documents = [Document.from_dict(doc_dict) for doc_dict in state.get('documents', [])]
        self.id_to_index = state['id_to_index']
        for idx, document in enumerate(self.documents):
            self.index.add_item(idx, document.content)
        self.index.build(self.num_trees)

    def add_document(self, document: IDocument) -> None:
        """
        Add a single document to the document store.
        
        Parameters:
            document (IDocument): The document to be added to the store.
        """
        index = len(self.documents)
        self.documents.append(document)
        self.index.add_item(index, document.content)
        self.id_to_index[document.id] = index
        try:
            self.index.build(self.num_trees)
        except Exception as e:
            self._rebuild_index()

    def add_documents(self, documents: List[IDocument]) -> None:
        """
        Add multiple documents to the document store in a batch operation.
        
        Parameters:
            documents (List[IDocument]): A list of documents to be added to the store.
        """
        start_idx = len(self.documents)
        self.documents.extend(documents)
        for i, doc in enumerate(documents):
            idx = start_idx + i
            self.index.add_item(idx, doc.content)
            self.id_to_index[doc.id] = idx
        try:
            self.index.build(self.num_trees)
        except Exception as e:
            self._rebuild_index()

    def get_document(self, id: str) -> Union[IDocument, None]:
        """
        Retrieve a single document by its identifier.
        
        Parameters:
            id (str): The unique identifier of the document to retrieve.
        
        Returns:
            Union[IDocument, None]: The requested document if found; otherwise, None.
        """
        index = self.id_to_index.get(id)
        if index is not None:
            return self.documents[index]
        return None

    def get_all_documents(self) -> List[IDocument]:
        """
        Retrieve all documents stored in the document store.
        
        Returns:
            List[IDocument]: A list of all documents in the store.
        """
        return self.documents

    def delete_document(self, id: str) -> None:
        """
        Delete a document from the document store by its identifier.
        
        Parameters:
            id (str): The unique identifier of the document to delete.
        """
        if id in self.id_to_index:
            index = self.id_to_index.pop(id)
            self.documents.pop(index)
            self._rebuild_index()

    def update_document(self, id: str, updated_document: IDocument) -> None:
        """
        Update a document in the document store.
        
        Parameters:
            id (str): The unique identifier of the document to update.
            updated_document (IDocument): The updated document instance.
        """
        if id in self.id_to_index:
            index = self.id_to_index[id]
            self.documents[index] = updated_document
            self._rebuild_index()

    def clear_documents(self) -> None:
        """
        Deletes all documents from the vector store
        """
        self.documents = []
        self.doc_id_to_index = {}
        self.index = AnnoyIndex(self.dimension, self.metric)

    def document_count(self) -> int:
        """
        Returns the number of documents in the store.
        """
        return len(self.documents)

    def retrieve(self, query: List[float], top_k: int = 5) -> List[IDocument]:
        """
        Retrieve the top_k most relevant documents based on the given query.
        
        Args:
            query (List[float]): The content of the document for retrieval.
            top_k (int): The number of top relevant documents to retrieve.
        
        Returns:
            List[IDocument]: A list of the top_k most relevant documents.
        """
        indices = self.index.get_nns_by_vector(query, top_k, include_distances=False)
        return [self.documents[idx] for idx in indices]

    def save_store(self, directory_path: str) -> None:
        """
        Saves the state of the vector store to the specified directory. This includes
        both the vectorizer's model and the stored documents or vectors.

        Parameters:
            directory_path (str): The directory path where the store's state will be saved.
        """
        state = self.get_state()
        os.makedirs(directory_path, exist_ok=True)
        state_file = os.path.join(directory_path, 'store_state.json')
        index_file = os.path.join(directory_path, 'annoy_index.ann')

        with open(state_file, 'w') as f:
            json.dump(state, f, indent=4)
        self.index.save(index_file)

    def load_store(self, directory_path: str) -> None:
        """
        Loads the state of the vector store from the specified directory. This includes
        both the vectorizer's model and the stored documents or vectors.

        Parameters:
            directory_path (str): The directory path from where the store's state will be loaded.
        """
        state_file = os.path.join(directory_path, 'store_state.json')
        index_file = os.path.join(directory_path, 'annoy_index.ann')

        with open(state_file, 'r') as f:
            state = json.load(f)
        self.set_state(state)
        self.index.load(index_file)

    def save_parts(self, directory_path: str, chunk_size: int = 10485760) -> None:
        """
        Save the model in parts to handle large files by splitting them.
        """
        state = self.get_state()
        os.makedirs(directory_path, exist_ok=True)
        temp_state_file = tempfile.NamedTemporaryFile(delete=False)

        try:
            pickle.dump(state, temp_state_file)
            temp_state_file.close()

            with open(temp_state_file.name, 'rb') as src:
                part_num = 0
                while True:
                    chunk = src.read(chunk_size)
                    if not chunk:
                        break
                    with open(os.path.join(directory_path, f'state_part_{part_num}.pkl'), 'wb') as dest:
                        dest.write(chunk)
                    part_num += 1
        finally:
            os.remove(temp_state_file.name)

        index_file = os.path.join(directory_path, 'annoy_index.ann')
        self.index.save(index_file)

        with open(index_file, 'rb') as src:
            part_num = 0
            while True:
                chunk = src.read(chunk_size)
                if not chunk:
                    break
                with open(os.path.join(directory_path, f'index_part_{part_num}.ann'), 'wb') as dest:
                    dest.write(chunk)
                part_num += 1

    def load_parts(self, directory_path: str, state_file_pattern: str, index_file_pattern: str) -> None:
        """
        Load and combine model parts from a directory.
        """
        temp_state_file = tempfile.NamedTemporaryFile(delete=False)
        try:
            with open(temp_state_file.name, 'ab') as dest:
                part_num = 0
                while True:
                    part_file_path = os.path.join(directory_path, state_file_pattern.format(part_num))
                    if not os.path.isfile(part_file_path):
                        break
                    with open(part_file_path, 'rb') as src:
                        chunk = src.read()
                        dest.write(chunk)
                    part_num += 1

            with open(temp_state_file.name, 'rb') as src:
                state = pickle.load(src)
            self.set_state(state)
        finally:
            os.remove(temp_state_file.name)

        index_file = os.path.join(directory_path, 'annoy_index.ann')
        self.index.load(index_file)

    def _rebuild_index(self):
        """
        Rebuild the Annoy index from the current documents.
        """
        self.index = AnnoyIndex(self.dimension, self.metric)
        for idx, document in enumerate(self.documents):
            self.index.add_item(idx, document.content)
        self.index.build(self.num_trees)