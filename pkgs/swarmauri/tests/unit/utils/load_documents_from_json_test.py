import pytest
import json
import tempfile
import os
from swarmauri.documents.concrete.Document import Document
from swarmauri.utils.load_documents_from_json import (
    load_documents_from_json_file,
    load_documents_from_json,
)


@pytest.mark.unit
def test_load_documents_from_json_file():
    test_data = [
        {"content": "Document 1 content", "document_name": "doc1.txt"},
        {"content": "Document 2 content", "document_name": "doc2.txt"},
        {"content": "", "document_name": "empty.txt"},  # This should be skipped
    ]

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
        json.dump(test_data, temp_file)
        temp_file_path = temp_file.name

    try:
        documents = load_documents_from_json_file(temp_file_path)

        assert len(documents) == 2  # The empty document should be skipped
        assert all(isinstance(doc, Document) for doc in documents)
        assert documents[0].id == "0"
        assert documents[0].content == "Document 1 content"
        assert documents[0].metadata == {"document_name": "doc1.txt"}
        assert documents[1].id == "1"
        assert documents[1].content == "Document 2 content"
        assert documents[1].metadata == {"document_name": "doc2.txt"}
    finally:
        os.unlink(temp_file_path)


@pytest.mark.unit
def test_load_documents_from_json_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_documents_from_json_file("non_existent_file.json")
