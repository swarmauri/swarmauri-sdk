import pytest
from swarmauri.documents.concrete.Document import Document
from swarmauri.vector_stores.concrete.MlmVectorStore import MlmVectorStore


@pytest.mark.unit
def test_ubc_resource():
    vs = MlmVectorStore()
    assert vs.resource == "VectorStore"
    assert vs.embedder.resource == "Embedding"


@pytest.mark.unit
def test_ubc_type():
    vs = MlmVectorStore()
    assert vs.type == "MlmVectorStore"


@pytest.mark.unit
def test_serialization():
    vs = MlmVectorStore()
    assert vs.id == MlmVectorStore.model_validate_json(vs.model_dump_json()).id


@pytest.mark.unit
def test_top_k():
    vs = MlmVectorStore()
    documents = [
        Document(content="test"),
        Document(content="test1"),
        Document(content="test2"),
        Document(content="test3"),
    ]

    vs.add_documents(documents)
    assert len(vs.retrieve(query="test", top_k=2)) == 2
