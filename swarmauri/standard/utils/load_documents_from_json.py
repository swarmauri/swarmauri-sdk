import json
from typing import List
from swarmauri.standard.documents.concrete.Document import Document

def load_documents_from_json(json_file_path):
    documents = []
    with open(json_file_path, 'r') as f:
        data = json.load(f)
    documents = [Document(doc_id=str(_), content=doc['content'], metadata={"document_name": doc['document_name']}) for _, doc in enumerate(data) if doc['content']]
    return documents