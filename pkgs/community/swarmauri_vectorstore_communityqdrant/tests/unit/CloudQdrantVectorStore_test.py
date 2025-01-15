import os
import pytest
from swarmauri.documents.concrete.Document import Document
from swarmauri_vectorstore_communityqdrant.CloudQdrantVectorStore import (
    CloudQdrantVectorStore,
)


# Fixture to initialize CloudQdrantVectorStore and check for required environment variables
@pytest.fixture(scope="module")
def cloud_qdrant_vector_store():
    API_KEY = os.getenv("QDRANT_API_KEY")
    COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME")
    URL = os.getenv("QDRANT_URL_KEY")

    # Skip tests if required environment variables are not set
    if not API_KEY or not COLLECTION_NAME or not URL:
        pytest.skip("Skipping tests due to missing environment variables.")

    # Return the initialized vector store
    vs = CloudQdrantVectorStore(
        api_key=API_KEY,
        collection_name=COLLECTION_NAME,
        vector_size=100,
        url=URL,
    )
    return vs


@pytest.mark.unit
def test_ubc_resource(cloud_qdrant_vector_store):
    vs = cloud_qdrant_vector_store
    assert vs.resource == "VectorStore"
    assert vs.embedder.resource == "Embedding"


@pytest.mark.unit
def test_ubc_type(cloud_qdrant_vector_store):
    vs = cloud_qdrant_vector_store
    assert vs.type == "CloudQdrantVectorStore"


@pytest.mark.unit
def test_serialization(cloud_qdrant_vector_store):
    vs = cloud_qdrant_vector_store
    assert vs.id == CloudQdrantVectorStore.model_validate_json(vs.model_dump_json()).id


@pytest.mark.unit
def test_top_k(cloud_qdrant_vector_store):
    vs = cloud_qdrant_vector_store

    # Connect to the Qdrant cloud vector store
    vs.connect()

    documents = [
        Document(content="test"),
        Document(content="test1"),
        Document(content="test2"),
        Document(content="test3"),
    ]

    vs.add_documents(documents)
    assert len(vs.retrieve(query="test", top_k=2)) == 2
