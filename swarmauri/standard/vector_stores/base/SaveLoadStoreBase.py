import json
import os
from typing import List
import importlib 
from swarmauri.core.vector_stores.ISaveLoadStore import ISaveLoadStore
from swarmauri.standard.documents import DocumentBase
from swarmauri.core.vectorizers.IVectorize import IVectorize

class SaveLoadStoreBase(ISaveLoadStore):
    """
    Base class for vector stores with built-in support for saving and loading
    the vectorizer's model and the documents.
    """
    
    def __init__(self, vectorizer: IVectorize, documents: List[DocumentBase]):
        self.vectorizer = vectorizer
        self.documents = documents
    
    def save_store(self, directory_path: str) -> None:
        """
        Saves both the vectorizer's model and the documents.
        """
        # Ensure the directory exists
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
            
        # Save the vectorizer model
        model_path = os.path.join(directory_path, "vectorizer_model")
        self.vectorizer.save_model(model_path)
        
        # Save documents
        documents_path = os.path.join(directory_path, "documents.json")
        with open(documents_path, 'w', encoding='utf-8') as f:
            json.dump([each.to_dict() for each in self.documents], 
                f,
                ensure_ascii=False, 
                indent=4)

    
    def load_store(self, directory_path: str) -> None:
        """
        Loads both the vectorizer's model and the documents.
        """
        # Load the vectorizer model
        model_path = os.path.join(directory_path, "vectorizer_model")
        self.vectorizer.load_model(model_path)
        
        # Load documents
        documents_path = os.path.join(directory_path, "documents.json")
        with open(documents_path, 'r', encoding='utf-8') as f:
            self.documents = [self._load_document(each) for each in json.load(f)]

    def _load_document(self, data):
        document_type = data.pop("type", None) 
        if document_type:
            module = importlib.import_module(f"swarmauri.standard.documents.concrete.{document_type}")
            document_class = getattr(module, document_type)
            document = document_class.from_dict(**data)
            return document
        else:
            raise ValueError("Unknown document type")
        
