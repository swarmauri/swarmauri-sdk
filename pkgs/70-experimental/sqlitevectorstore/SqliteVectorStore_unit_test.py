import pytest
from swarmauri_standard.documents.Document import Document
from swarmauri_standard.vector_stores.SqliteVectorStore import SqliteVectorStore


@pytest.mark.unit
def test_ubc_resource():
    vs = SqliteVectorStore()
    assert vs.resource == "VectorStore"
    assert vs.embedder.resource == "Embedding"


@pytest.mark.unit
def test_ubc_type():
    vs = SqliteVectorStore()
    assert vs.type == "SqliteVectorStore"


@pytest.mark.unit
def test_serialization():
    vs = SqliteVectorStore()
    assert vs.id == SqliteVectorStore.model_validate_json(vs.model_dump_json()).id


@pytest.mark.unit
def test_top_k():
    vs = SqliteVectorStore()
    documents = [
        Document(content="test"),
        Document(content="test1"),
        Document(content="test2"),
        Document(content="test3"),
    ]

    vs.add_documents(documents)
    assert len(vs.retrieve(query="test", top_k=2)) == 2
