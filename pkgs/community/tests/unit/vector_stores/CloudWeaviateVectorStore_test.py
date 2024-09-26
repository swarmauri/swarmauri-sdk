import os
import pytest
from swarmauri.documents.concrete.Document import Document
from swarmauri_community.vector_stores.CloudWeaviateVectorStore import CloudWeaviateVectorStore

WEAVIATE_URL = "https://p6grmuovrkqie6kafxts2a.c0.asia-southeast1.gcp.weaviate.cloud" 
WEAVIATE_API_KEY ="kAF7ar7sZqgFyZEhS4hL9eVAJ3Br5PwJP6An"


@pytest.mark.skipif(
    not WEAVIATE_URL or not WEAVIATE_API_KEY,
    reason="Skipping due to environment variables not set",
)
@pytest.mark.unit
def test_weaviate_type():
    vs = CloudWeaviateVectorStore(
        url=WEAVIATE_URL,
        api_key=WEAVIATE_API_KEY,
        collection_name="example",
        vector_size=100,
    )
    assert vs.type == "CloudWeaviateVectorStore"



@pytest.mark.skipif(
    not WEAVIATE_URL or not WEAVIATE_API_KEY,
    reason="Skipping due to environment variables not set",
)
@pytest.mark.unit
def test_top_k():
    vs = CloudWeaviateVectorStore(
        url=WEAVIATE_URL,
        api_key=WEAVIATE_API_KEY,
        collection_name="example",
        vector_size=100,
    )
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

    vs.add_document(document1)
    vs.add_document(document2)
    assert len(vs.retrieve(query="information", top_k=1)) == 1
