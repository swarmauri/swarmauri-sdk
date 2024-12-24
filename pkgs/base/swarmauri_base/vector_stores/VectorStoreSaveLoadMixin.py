from typing import List
import os
from pydantic import BaseModel
import json
import glob
import importlib 
from swarmauri_core.vector_stores.IVectorStoreSaveLoad import IVectorStoreSaveLoad
from swarmauri_standard.documents.Document import Document

class VectorStoreSaveLoadMixin(IVectorStoreSaveLoad, BaseModel):
    """
    Base class for vector stores with built-in support for saving and loading
    the vectorizer's model and the documents.
    """
    
    
    def save_store(self, directory_path: str) -> None:
        """
        Saves both the vectorizer's model and the documents.
        """
        # Ensure the directory exists
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
            
        # Save the vectorizer model
        model_path = os.path.join(directory_path, "embedding_model")
        self._vectorizer.save_model(model_path)
        
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
        model_path = os.path.join(directory_path, "embedding_model")
        self.vectorizer.load_model(model_path)
        
        # Load documents
        documents_path = os.path.join(directory_path, "documents.json")
        with open(documents_path, 'r', encoding='utf-8') as f:
            self.documents = [self._load_document(each) for each in json.load(f)]

    def _load_document(self, data):
        document_type = data.pop("type") 
        if document_type:
            module = importlib.import_module(f"swarmauri.documents.concrete.{document_type}")
            document_class = getattr(module, document_type)
            document = document_class.from_dict(data)
            return document
        else:
            raise ValueError("Unknown document type")

    def save_parts(self, directory_path: str, chunk_size: int = 10485760) -> None:
        """
        Splits the file into parts if it's too large and saves those parts individually.
        """
        file_number = 1
        model_path = os.path.join(directory_path, "embedding_model")
        parts_directory = os.path.join(directory_path, "parts")
        
        if not os.path.exists(parts_directory):
            os.makedirs(parts_directory)



        with open(f"{model_path}/model.safetensors", 'rb') as f:
            chunk = f.read(chunk_size)
            while chunk:
                with open(f"{parts_directory}/model.safetensors.part{file_number:03}", 'wb') as chunk_file:
                    chunk_file.write(chunk)
                file_number += 1
                chunk = f.read(chunk_size)

        # Split the documents into parts and save them
        documents_dir = os.path.join(directory_path, "documents")

        self._split_json_file(directory_path, chunk_size=chunk_size)


    def _split_json_file(self, directory_path: str, max_records=100, chunk_size: int = 10485760):    
        # Read the input JSON file
        combined_documents_file_path = os.path.join(directory_path, "documents.json")

        # load the master JSON file
        with open(combined_documents_file_path , 'r') as file:
            data = json.load(file)

        # Set and Create documents parts folder if it does not exist
        documents_dir = os.path.join(directory_path, "documents")
        if not os.path.exists(documents_dir):
            os.makedirs(documents_dir)
        current_batch = []
        file_index = 1
        current_size = 0
        
        for record in data:
            current_batch.append(record)
            current_size = len(json.dumps(current_batch).encode('utf-8'))
            
            # Check if current batch meets the splitting criteria
            if len(current_batch) >= max_records or current_size >= chunk_size:
                # Write current batch to a new file
                output_file = f'document_part_{file_index}.json'
                output_file = os.path.join(documents_dir, output_file)
                with open(output_file, 'w') as outfile:
                    json.dump(current_batch, outfile)
                
                # Prepare for the next batch
                current_batch = []
                current_size = 0
                file_index += 1

        # Check if there's any remaining data to be written
        if current_batch:
            output_file = f'document_part_{file_index}.json'
            output_file = os.path.join(documents_dir, output_file)
            with open(output_file, 'w') as outfile:
                json.dump(current_batch, outfile)

    def load_parts(self, directory_path: str, file_pattern: str = '*.part*') -> None:
        """
        Combines file parts from a directory back into a single file and loads it.
        """
        model_path = os.path.join(directory_path, "embedding_model")
        parts_directory = os.path.join(directory_path, "parts")
        output_file_path = os.path.join(model_path, "model.safetensors")

        parts = sorted(glob.glob(os.path.join(parts_directory, file_pattern)))
        with open(output_file_path, 'wb') as output_file:
            for part in parts:
                with open(part, 'rb') as file_part:
                    output_file.write(file_part.read())

        # Load the combined_model now        
        model_path = os.path.join(directory_path, "embedding_model")
        self._vectorizer.load_model(model_path)

        # Load document files
        self._load_documents(directory_path)
        

    def _load_documents(self, directory_path: str) -> None:
        """
        Loads the documents from parts stored in the given directory.
        """
        part_paths = glob.glob(os.path.join(directory_path, "documents/*.json"))
        for part_path in part_paths:
            with open(part_path, "r") as f:
                part_documents = json.load(f)
                for document_data in part_documents:
                    document_type = document_data.pop("type")
                    document_module = importlib.import_module(f"swarmauri.documents.concrete.{document_type}")
                    document_class = getattr(document_module, document_type)
                    document = document_class.from_dict(document_data)
                    self.documents.append(document)