import os
import pytest
from swarmauri.documents.concrete.Document import Document
from swarmauri_community.vector_stores.concrete.CloudWeaviateVectorStore import (
    CloudWeaviateVectorStore,
)
from dotenv import load_dotenv

load_dotenv()

WEAVIATE_URL = os.getenv("WEAVIATE_URL")
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY")
# WEAVIATE_URL = "https://p6grmuovrkqie6kafxts2a.c0.asia-southeast1.gcp.weaviate.cloud"
# WEAVIATE_API_KEY = "kAF7ar7sZqgFyZEhS4hL9eVAJ3Br5PwJP6An"

@pytest.fixture(scope="module")
def vector_store():
    if not all([WEAVIATE_URL, WEAVIATE_API_KEY]):
        pytest.skip("Skipping due to environment variable not set")
    vs = CloudWeaviateVectorStore(
        url=WEAVIATE_URL,
        api_key=WEAVIATE_API_KEY,
        collection_name="example",
        vector_size=100,
    )
    return vs


@pytest.mark.unit
def test_ubc_type(vector_store):
    assert vector_store.type == "CloudWeaviateVectorStore"

@pytest.mark.unit
def test_ubc_resource(vector_store):
    assert vector_store.resource == "VectorStore"
    assert vector_store.embedder.resource == "Embedding"


@pytest.mark.unit
def test_serialization(vector_store):
    """
    Test to verify serialization and deserialization of CloudWeaviateVectorStore.
    """
    assert (
        vector_store.id
        == CloudWeaviateVectorStore.model_validate_json(
            vector_store.model_dump_json()
        ).id
    )


@pytest.mark.unit
def test_top_k(vector_store):

    document1 = Document(
        id="doc-001",
        content="This is the content of the first document.",
        metadata={"author": "Alice", "date": "2024-09-25"},
    )
    document2 = Document(
        id="doc-002",
        content="The second document contains different information.",
        metadata={"author": "Bob", "date": "2024-09-26"},
    )
    vector_store.connect()
    vector_store.add_document(document1)
    vector_store.add_document(document2)
    assert len(vector_store.retrieve(query="information", top_k=1)) == 1
