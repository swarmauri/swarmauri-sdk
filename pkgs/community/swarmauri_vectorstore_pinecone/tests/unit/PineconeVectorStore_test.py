import os
import pytest
from swarmauri_standard.documents.Document import Document
from swarmauri_vectorstore_pinecone.PineconeVectorStore import (
    PineconeVectorStore,
)
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("PINECONE_API_KEY")


# Fixture for creating a PineconeVectorStore instance
@pytest.fixture
def vector_store():
    if not API_KEY:
        pytest.skip("Skipping due to environment variable 'PINECONE_API_KEY' not set")
    vs = PineconeVectorStore(
        api_key=API_KEY,
        collection_name="example",
        vector_size=100,
    )
    vs.connect()
    return vs


@pytest.mark.unit
def test_ubc_resource(vector_store):
    assert vector_store.resource == "VectorStore"
    assert vector_store.embedder.resource == "Embedding"


@pytest.mark.unit
def test_ubc_type(vector_store):
    assert vector_store.type == "PineconeVectorStore"


@pytest.mark.unit
def test_serialization(vector_store):
    assert (
        vector_store.id
        == PineconeVectorStore.model_validate_json(vector_store.model_dump_json()).id
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
    assert len(vector_store.retrieve(query="test", top_k=2)) == 2
