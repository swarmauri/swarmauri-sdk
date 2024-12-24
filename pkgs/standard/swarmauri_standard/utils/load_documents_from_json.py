import json
from typing import List
from swarmauri_standard.documents.Document import Document

def load_documents_from_json_file(json_file_path):
    documents = []
    with open(json_file_path, 'r') as f:
        data = json.load(f)

    documents = [
        Document(id=str(_), 
        content=doc['content'], 
        metadata={"document_name": doc['document_name']}) 
        for _, doc in enumerate(data) if doc['content']
        ]

    return documents

def load_documents_from_json(json):
    documents = []
    data = json.loads(json)
    documents = [
        Document(id=str(_), 
        content=doc['content'], 
        metadata={"document_name": doc['document_name']}) 
        for _, doc in enumerate(data) if doc['content']
        ]
    return documents
