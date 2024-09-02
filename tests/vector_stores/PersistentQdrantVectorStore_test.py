import os
import pytest
from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.community.vector_stores.PersistentQdrantVectorStore import (
    PersistentQdrantVectorStore,
)

COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME")
URL = "http://localhost:6333"  # default URL for Qdrant


@pytest.mark.unit
def test_ubc_resource():
    vs = PersistentQdrantVectorStore(
        collection_name=COLLECTION_NAME,
        vector_size=100,
        path=URL,
    )
    assert vs.resource == "VectorStore"
    assert vs.embedder.resource == "Embedding"


@pytest.mark.unit
def test_ubc_type():
    vs = PersistentQdrantVectorStore(
        collection_name=COLLECTION_NAME,
        vector_size=100,
        path=URL,
    )
    assert vs.type == "PersistentQdrantVectorStore"


@pytest.mark.unit
def test_serialization():
    vs = PersistentQdrantVectorStore(
        collection_name=COLLECTION_NAME,
        vector_size=100,
        path=URL,
    )
    assert (
        vs.id
        == PersistentQdrantVectorStore.model_validate_json(vs.model_dump_json()).id
    )


@pytest.mark.unit
def top_k_test():
    vs = PersistentQdrantVectorStore(
        collection_name=COLLECTION_NAME,
        vector_size=100,
        path=URL,
    )
    documents = [
        Document(content="test"),
        Document(content="test1"),
        Document(content="test2"),
        Document(content="test3"),
    ]

    vs.add_documents(documents)
    assert len(vs.retrieve(query="test", top_k=2)) == 2
