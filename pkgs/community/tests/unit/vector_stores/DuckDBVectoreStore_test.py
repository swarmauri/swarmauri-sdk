import os
import pytest
from swarmauri.documents.concrete.Document import Document
from swarmauri_community.vector_stores.DuckDBVectoreStore import (
    DuckDBVectorStore,
)


@pytest.fixture
def vector_store(tmp_path):
    db_path = str(tmp_path / "test.duckdb")
    vs = DuckDBVectorStore(vector_size=100, db_path=db_path, persist_dir=str(tmp_path))
    yield vs
    vs.disconnect()


@pytest.mark.unit
def test_ubc_resource(vector_store):
    assert vector_store.resource == "VectorStore"
    assert vector_store._embedder.resource == "Embedding"


@pytest.mark.unit
def test_ubc_type(vector_store):
    assert vector_store.type == "DuckDBVectorStore"


@pytest.mark.unit
def test_serialization(vector_store):
    assert (
        vector_store.id
        == DuckDBVectorStore.model_validate_json(vector_store.model_dump_json()).id
    )


@pytest.mark.unit
def test_top_k(vector_store):
    documents = [
        Document(content="test"),
        Document(content="test1"),
        Document(content="test2"),
        Document(content="test3"),
    ]

    vector_store.add_documents(documents)
    results = vector_store.retrieve(query="test", top_k=2)
    assert len(results) == 2
    assert all("test" in doc.content for doc in results)
