import json
from typing import List
from swarmauri.standard.documents.concrete.EmbeddedDocument import EmbeddedDocument

def load_documents_from_json_file(json_file_path):
    documents = []
    with open(json_file_path, 'r') as f:
        data = json.load(f)

    documents = [
        EmbeddedDocument(id=str(_), 
        content=doc['content'], 
        metadata={"document_name": doc['document_name']}) 
        for _, doc in enumerate(data) if doc['content']
        ]

    return documents

def load_documents_from_json(json):
    documents = []
    data = json.loads(json)
    documents = [
        EmbeddedDocument(id=str(_), 
        content=doc['content'], 
        metadata={"document_name": doc['document_name']}) 
        for _, doc in enumerate(data) if doc['content']
        ]
    return documents
