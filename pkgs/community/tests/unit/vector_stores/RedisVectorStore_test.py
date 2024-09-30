import pytest
import numpy as np
from swarmauri.documents.concrete.Document import Document
from swarmauri_community.vector_stores.RedisVectorStore import RedisVectorStore
from swarmauri.documents.concrete.Document import Document
from dotenv import load_dotenv
from os import getenv

load_dotenv()

REDIS_HOST = 'getenv("REDIS_HOST")'
REDIS_PORT = getenv("REDIS_PORT", "12648")
REDIS_PASSWORD = getenv("REDIS_PASSWORD")
# REDIS_HOST = 'redis-15893.c305.ap-south-1-1.ec2.redns.redis-cloud.com'
# REDIS_PORT = '15893'
# REDIS_PASSWORD = 'jeIzN3EU3yf7oZrUfR9i1T8jaeGPGupb'

@pytest.fixture(scope="module")
def vector_store():
    if not all([REDIS_HOST, REDIS_PORT, REDIS_PASSWORD]):
        pytest.skip("Skipping due to environment variable not set")
    vector_store = RedisVectorStore(
        redis_host=REDIS_HOST,
        redis_port=REDIS_PORT,
        redis_password=REDIS_PASSWORD,  # Replace with your password if needed
        embedding_dimension=8000,  # Adjust based on your embedder
    )
    return vector_store


# Create a sample document
@pytest.fixture
def sample_document():
    return Document(
        id="test_doc1",
        content="This is a test document for unit testing.",
        metadata={"category": "test"},
    )


@pytest.mark.unit
def test_ubc_resource(vector_store):
    assert vector_store.resource == "VectorStore"


@pytest.mark.unit
def test_ubc_type(vector_store):
    assert vector_store.type == "RedisVectorStore"


@pytest.mark.unit
def top_k_test(vector_store):
    documents = [
        Document(content="test"),
        Document(content="test1"),
        Document(content="test2"),
        Document(content="test3"),
    ]

    vector_store.add_documents(documents)
    assert len(vector_store.retrieve(query="test", top_k=2)) == 2


@pytest.mark.unit
def test_add_and_get_document(vector_store, sample_document):
    vector_store.connect()
    vector_store.add_document(sample_document)

    retrieved_doc = vector_store.get_document("test_doc1")

    assert retrieved_doc is not None
    assert retrieved_doc.id == "test_doc1"
    assert retrieved_doc.content == "This is a test document for unit testing."
    assert retrieved_doc.metadata == {"category": "test"}


@pytest.mark.unit
def test_delete_document(vector_store, sample_document):
    vector_store.add_document(sample_document)
    vector_store.delete_document("test_doc1")

    retrieved_doc = vector_store.get_document("test_doc1")
    assert retrieved_doc is None


@pytest.mark.unit
def test_retrieve_similar_documents(vector_store):
    doc1 = Document(
        id="doc1",
        content="Sample document content about testing.",
        metadata={"category": "sample"},
    )
    doc2 = Document(
        id="doc2",
        content="Another test document for retrieval.",
        metadata={"category": "sample"},
    )

    vector_store.add_document(doc1)
    vector_store.add_document(doc2)

    similar_docs = vector_store.retrieve("test document", top_k=2)

    assert len(similar_docs) == 2
    assert similar_docs[0].id == "doc1" or similar_docs[0].id == "doc2"
    assert similar_docs[1].id == "doc1" or similar_docs[1].id == "doc2"
