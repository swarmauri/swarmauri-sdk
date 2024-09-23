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


@pytest.mark.unit
def test_ubc_resource():
    vs = PersistentChromaDBVectorStore(
        path=URL,
        collection_name=COLLECTION_NAME,
        vector_size=100,
    )
    assert vs.resource == "VectorStore"
    assert vs.embedder.resource == "Embedding"


@pytest.mark.unit
def test_ubc_type():
    vs = PersistentChromaDBVectorStore(
        path=URL,
        collection_name=COLLECTION_NAME,
        vector_size=100,
    )
    assert vs.type == "PersistentChromaDBVectorStore"


@pytest.mark.unit
def test_serialization():
    vs = PersistentChromaDBVectorStore(
        path=URL,
        collection_name=COLLECTION_NAME,
        vector_size=100,
    )
    assert (
        vs.id
        == PersistentChromaDBVectorStore.model_validate_json(vs.model_dump_json()).id
    )


@pytest.mark.unit
def top_k_test():
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
