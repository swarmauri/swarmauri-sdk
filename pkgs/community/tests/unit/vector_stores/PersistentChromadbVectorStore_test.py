import os
import pytest
from swarmauri.documents.concrete.Document import Document
from swarmauri_community.vector_stores.PersistentChromaDBVectorStore import (
    PersistentChromaDBVectorStore,
)

URL = os.getenv(
    "./chromadb_data"
)  # This is a placeholder, the actual value is not provided
COLLECTION_NAME = os.getenv("Chromadb_COLLECTION_NAME", "test_collection")


# Fixture for creating a PersistentChromaDBVectorStore instance
@pytest.fixture
def vector_store():
    return PersistentChromaDBVectorStore(
        path=URL,
        collection_name=COLLECTION_NAME,
        vector_size=100,
    )


# Skipif condition
chromadb_not_configured = pytest.mark.skipif(
    URL is None or COLLECTION_NAME is None, reason="ChromaDB is not properly configured"
)


@pytest.mark.unit
@chromadb_not_configured
def test_ubc_resource(vector_store):
    assert vector_store.resource == "VectorStore"
    assert vector_store.embedder.resource == "Embedding"


@pytest.mark.unit
@chromadb_not_configured
def test_ubc_type(vector_store):
    assert vector_store.type == "PersistentChromaDBVectorStore"


@pytest.mark.unit
@chromadb_not_configured
def test_serialization(vector_store):
    assert (
        vector_store.id
        == PersistentChromaDBVectorStore.model_validate_json(
            vector_store.model_dump_json()
        ).id
    )


@pytest.mark.unit
@chromadb_not_configured
def test_top_k():
    vs = PersistentChromaDBVectorStore(
        path=URL,
        collection_name=COLLECTION_NAME,
        vector_size=100,
    )
    documents = [
        Document(content="test"),
        Document(content="test1"),
        Document(content="test2"),
        Document(content="test3"),
    ]

    vs.add_documents(documents)
    assert len(vs.retrieve(query="test", top_k=2)) == 2
