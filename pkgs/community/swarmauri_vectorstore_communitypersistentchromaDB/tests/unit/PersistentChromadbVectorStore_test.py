import os
import pytest
from swarmauri_standard.documents.Document import Document
from swarmauri_vectorstore_communitypersistentchromaDB.PersistentChromaDBVectorStore import (
    PersistentChromaDBVectorStore,
)

PATH = os.getenv(
    "CHROMADB_PATH", "./chromadb_data"
)  # This is a placeholder, the actual value is not provided
COLLECTION_NAME = os.getenv("CHROMADB_COLLECTION_NAME", "test_collection")


# Fixture for creating a PersistentChromaDBVectorStore instance
@pytest.fixture
def vector_store():
    if not PATH or not COLLECTION_NAME:
        pytest.skip("ChromaDB is not properly configured")
    vs = PersistentChromaDBVectorStore(
        path=PATH,
        collection_name=COLLECTION_NAME,
        vector_size=100,
    )
    return vs


@pytest.mark.unit
def test_ubc_resource(vector_store):
    assert vector_store.resource == "VectorStore"
    assert vector_store.embedder.resource == "Embedding"


@pytest.mark.unit
def test_ubc_type(vector_store):
    assert vector_store.type == "PersistentChromaDBVectorStore"


@pytest.mark.unit
def test_serialization(vector_store):
    assert (
        vector_store.id
        == vector_store.model_validate_json(vector_store.model_dump_json()).id
    )


@pytest.mark.unit
def test_top_k(vector_store):
    vs = vector_store
    vs.connect()
    documents = [
        Document(content="test"),
        Document(content="test1"),
        Document(content="test2"),
        Document(content="test3"),
    ]

    vs.add_documents(documents)
    assert len(vs.retrieve(query="test", top_k=2)) == 2
