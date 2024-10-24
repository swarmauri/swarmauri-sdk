import pytest
from swarmauri.documents.concrete.Document import Document
from swarmauri.vector_stores.concrete.TfidfVectorStore import TfidfVectorStore


@pytest.mark.unit
def test_ubc_resource():
    vs = TfidfVectorStore()
    assert vs.resource == "VectorStore"
    assert vs.embedder.resource == "Embedding"


@pytest.mark.unit
def test_ubc_type():
    vs = TfidfVectorStore()
    assert vs.type == "TfidfVectorStore"


@pytest.mark.unit
def test_serialization():
    vs = TfidfVectorStore()
    assert vs.id == TfidfVectorStore.model_validate_json(vs.model_dump_json()).id


@pytest.mark.unit
def test_top_k():
    vs = TfidfVectorStore()
    documents = [
        Document(content="test"),
        Document(content="test1"),
        Document(content="test2"),
        Document(content="test3"),
    ]

    vs.add_documents(documents)
    assert len(vs.retrieve(query="test", top_k=2)) == 2
