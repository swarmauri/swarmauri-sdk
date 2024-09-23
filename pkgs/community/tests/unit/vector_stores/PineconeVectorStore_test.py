import os
import pytest
from swarmauri.documents.concrete.Document import Document
from swarmauri_community.vector_stores.PineconeVectorStore import PineconeVectorStore

API_KEY = os.getenv("PINECONE_API_KEY")


@pytest.mark.skipif(
    not os.getenv("PINECONE_API_KEY"),
    reason="Skipping due to environment variable not set",
)
@pytest.mark.unit
def test_ubc_resource():
    vs = PineconeVectorStore(
        api_key=API_KEY,
        collection_name="example",
        vector_size=100,
    )
    assert vs.resource == "VectorStore"
    assert vs.embedder.resource == "Embedding"


@pytest.mark.skipif(
    not os.getenv("PINECONE_API_KEY"),
    reason="Skipping due to environment variable not set",
)
@pytest.mark.unit
def test_ubc_type():
    vs = PineconeVectorStore(
        api_key=API_KEY,
        collection_name="example",
        vector_size=100,
    )
    assert vs.type == "PineconeVectorStore"


@pytest.mark.skipif(
    not os.getenv("PINECONE_API_KEY"),
    reason="Skipping due to environment variable not set",
)
@pytest.mark.unit
def test_serialization():
    vs = PineconeVectorStore(
        api_key=API_KEY,
        collection_name="example",
        vector_size=100,
    )
    assert vs.id == PineconeVectorStore.model_validate_json(vs.model_dump_json()).id


@pytest.mark.skipif(
    not os.getenv("PINECONE_API_KEY"),
    reason="Skipping due to environment variable not set",
)
@pytest.mark.unit
def test_top_k():
    vs = PineconeVectorStore(
        api_key=API_KEY,
        collection_name="example",
        vector_size=100,
    )
    vs.connect()
    documents = [
        Document(content="test"),
        Document(content="test1"),
        Document(content="test2"),
        Document(content="test3"),
    ]

    vs.add_documents(documents)
    assert len(vs.retrieve(query="test", top_k=2)) == 2
