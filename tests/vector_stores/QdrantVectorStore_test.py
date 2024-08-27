import os
import pytest
from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.community.vector_stores.QdrantVectorStore import QdrantVectorStore

URL = os.getenv("QDRANT_URL_KEY")
API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME")


@pytest.mark.unit
def test_ubc_resource():
    vs = QdrantVectorStore(
        url=URL,
        api_key=API_KEY,
        collection_name=COLLECTION_NAME,
        vector_size=100,
    )
    assert vs.resource == "VectorStore"
    assert vs.embedder.resource == "Embedding"


@pytest.mark.unit
def test_ubc_type():
    vs = QdrantVectorStore(
        url=URL,
        api_key=API_KEY,
        collection_name=COLLECTION_NAME,
        vector_size=100,
    )
    assert vs.type == "QdrantVectorStore"


@pytest.mark.unit
def test_serialization():
    vs = QdrantVectorStore(
        url=URL,
        api_key=API_KEY,
        collection_name=COLLECTION_NAME,
        vector_size=100,
    )
    assert vs.id == QdrantVectorStore.model_validate_json(vs.model_dump_json()).id


@pytest.mark.unit
def top_k_test():
    vs = QdrantVectorStore(
        url=URL,
        api_key=API_KEY,
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
