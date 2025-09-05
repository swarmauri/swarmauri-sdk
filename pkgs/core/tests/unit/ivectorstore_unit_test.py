import pytest
from swarmauri_core.vector_stores.IVectorStore import IVectorStore


@pytest.mark.unit
def test_ivectorstore_methods_are_abstract():
    method_names = [
        "add_document",
        "add_documents",
        "get_document",
        "get_all_documents",
        "delete_document",
        "clear_documents",
        "update_document",
        "document_count",
    ]
    for name in method_names:
        assert hasattr(IVectorStore, name)
        method = getattr(IVectorStore, name)
        assert getattr(method, "__isabstractmethod__", False)
