import os
import pytest
from swarmauri.documents.concrete.Document import Document
from swarmauri_community.vector_stores.PineconeVectorStore import PineconeVectorStore

API_KEY = os.getenv("PINECONE_API_KEY")

# Skipif decorator
pinecone_not_configured = pytest.mark.skipif(
    not API_KEY, reason="Skipping due to PINECONE_API_KEY environment variable not set"
)


# Fixture for creating a PineconeVectorStore instance
@pytest.fixture
def vector_store():
    vs = PineconeVectorStore(
        api_key=API_KEY,
        collection_name="example",
        vector_size=100,
    )
    vs.connect()
    return vs


@pytest.mark.unit
@pinecone_not_configured
def test_ubc_resource(vector_store):
    assert vector_store.resource == "VectorStore"
    assert vector_store.embedder.resource == "Embedding"


@pytest.mark.unit
@pinecone_not_configured
def test_ubc_type(vector_store):
    assert vector_store.type == "PineconeVectorStore"


@pytest.mark.unit
@pinecone_not_configured
def test_serialization(vector_store):
    assert (
        vector_store.id
        == PineconeVectorStore.model_validate_json(vector_store.model_dump_json()).id
    )


@pytest.mark.unit
@pinecone_not_configured
def test_top_k(vector_store):
    documents = [
        Document(content="test"),
        Document(content="test1"),
        Document(content="test2"),
        Document(content="test3"),
    ]

    vector_store.add_documents(documents)
    assert len(vector_store.retrieve(query="test", top_k=2)) == 2
