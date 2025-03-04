import os
import pytest
from swarmauri.documents.concrete.Document import Document
from swarmauri_community.vector_stores.concrete.PersistentQdrantVectorStore import (
    PersistentQdrantVectorStore,
)

COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME")
URL = "http://localhost:6333"  # default URL for Qdrant

# Skipif decorator
qdrant_not_configured = pytest.mark.skipif(
    not COLLECTION_NAME,
    reason="Skipping due to QDRANT_COLLECTION_NAME environment variable not set",
)


# Fixture for creating a PersistentQdrantVectorStore instance
@pytest.fixture
def vector_store():
    vs = PersistentQdrantVectorStore(
        collection_name=COLLECTION_NAME,
        vector_size=100,
        path=URL,
    )
    vs.connect()
    return vs


@pytest.mark.unit
@qdrant_not_configured
def test_ubc_resource(vector_store):
    assert vector_store.resource == "VectorStore"
    assert vector_store.embedder.resource == "Embedding"


@pytest.mark.unit
@qdrant_not_configured
def test_ubc_type(vector_store):
    assert vector_store.type == "PersistentQdrantVectorStore"


@pytest.mark.unit
@qdrant_not_configured
def test_serialization(vector_store):
    assert (
        vector_store.id
        == PersistentQdrantVectorStore.model_validate_json(
            vector_store.model_dump_json()
        ).id
    )


@pytest.mark.unit
@qdrant_not_configured
def test_top_k(vector_store):
    documents = [
        Document(content="test"),
        Document(content="test1"),
        Document(content="test2"),
        Document(content="test3"),
    ]

    vector_store.add_documents(documents)
    assert len(vector_store.retrieve(query="test", top_k=2)) == 2
