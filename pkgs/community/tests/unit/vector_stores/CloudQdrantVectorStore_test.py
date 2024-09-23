import os
import pytest
from swarmauri.documents.concrete.Document import Document
from swarmauri_community.community.vector_stores.CloudQdrantVectorStore import (
    CloudQdrantVectorStore,
)

API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME")
URL = os.getenv("QDRANT_URL_KEY")


@pytest.mark.skipif(
    not os.getenv("QDRANT_API_KEY"),
    reason="Skipping due to environment variable not set",
)
@pytest.mark.unit
def test_ubc_resource():
    vs = CloudQdrantVectorStore(
        api_key=API_KEY,
        collection_name=COLLECTION_NAME,
        vector_size=100,
        url=URL,
    )
    assert vs.resource == "VectorStore"
    assert vs.embedder.resource == "Embedding"


@pytest.mark.skipif(
    not os.getenv("QDRANT_API_KEY"),
    reason="Skipping due to environment variable not set",
)
@pytest.mark.unit
def test_ubc_type():
    vs = CloudQdrantVectorStore(
        api_key=API_KEY,
        collection_name=COLLECTION_NAME,
        vector_size=100,
        url=URL,
    )
    assert vs.type == "CloudQdrantVectorStore"


@pytest.mark.skipif(
    not os.getenv("QDRANT_API_KEY"),
    reason="Skipping due to environment variable not set",
)
@pytest.mark.unit
def test_serialization():
    vs = CloudQdrantVectorStore(
        api_key=API_KEY,
        collection_name=COLLECTION_NAME,
        vector_size=100,
        url=URL,
    )
    assert vs.id == CloudQdrantVectorStore.model_validate_json(vs.model_dump_json()).id


@pytest.mark.skipif(
    not os.getenv("QDRANT_API_KEY"),
    reason="Skipping due to environment variable not set",
)
@pytest.mark.unit
def top_k_test():
    vs = CloudQdrantVectorStore(
        api_key=API_KEY,
        collection_name=COLLECTION_NAME,
        vector_size=100,
        url=URL,
    )
    documents = [
        Document(content="test"),
        Document(content="test1"),
        Document(content="test2"),
        Document(content="test3"),
    ]

    vs.add_documents(documents)
    assert len(vs.retrieve(query="test", top_k=2)) == 2
