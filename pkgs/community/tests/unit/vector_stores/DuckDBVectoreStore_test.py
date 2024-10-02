import os
import pytest
import numpy as np
from swarmauri.documents.concrete.Document import Document
from swarmauri.vectors.concrete.Vector import Vector
from swarmauri_community.vector_stores.DuckDBVectoreStore import (
    DuckDBVectorStore,
)


# Fixture for creating a DuckDBVectorStore instance
@pytest.fixture
def vector_store():
    # Use in-memory database for testing
    vs = DuckDBVectorStore(db_path=":memory:", vector_size=100, metric="cosine")
    return vs


@pytest.mark.unit
def test_initialization(vector_store):
    assert vector_store.type == "DuckDBVectorStore"
    assert vector_store.vector_size == 100
    assert vector_store.metric == "cosine"


@pytest.mark.unit
def test_add_and_get_document(vector_store):
    doc = Document(
        id="test_id",
        content="test content",
        embedding=Vector(value=np.random.rand(100).tolist()),
    )
    vector_store.add_document(doc)

    retrieved_doc = vector_store.get_document("test_id")
    assert retrieved_doc is not None
    assert retrieved_doc.id == doc.id
    assert retrieved_doc.content == doc.content


@pytest.mark.unit
def test_add_and_get_multiple_documents(vector_store):
    docs = [
        Document(
            id=f"test_id_{i}",
            content=f"test content {i}",
            embedding=Vector(value=np.random.rand(100).tolist()),
        )
        for i in range(3)
    ]
    vector_store.add_documents(docs)

    all_docs = vector_store.get_all_documents()
    assert len(all_docs) == 3


@pytest.mark.unit
def test_update_document(vector_store):
    # First, add a document
    doc = Document(
        id="test_id",
        content="test content",
        embedding=Vector(value=np.random.rand(100).tolist()),
    )
    vector_store.add_document(doc)

    # Then, update the document
    updated_doc = Document(
        id="test_id",
        content="updated content",
        embedding=Vector(value=np.random.rand(100).tolist()),
    )
    vector_store.update_document(updated_doc)

    # Verify the update
    retrieved_doc = vector_store.get_document("test_id")
    assert retrieved_doc.content == "updated content"

    # Test updating a non-existent document (should insert)
    new_doc = Document(
        id="new_test_id",
        content="new content",
        embedding=Vector(value=np.random.rand(100).tolist()),
    )
    vector_store.update_document(new_doc)

    # Verify the insertion
    new_retrieved_doc = vector_store.get_document("new_test_id")
    assert new_retrieved_doc is not None
    assert new_retrieved_doc.content == "new content"


@pytest.mark.unit
def test_delete_document(vector_store):
    # First, add a document
    doc = Document(
        id="test_id",
        content="test content",
        embedding=Vector(value=np.random.rand(100).tolist()),
    )
    vector_store.add_document(doc)
    assert vector_store.count_documents() == 1

    # Then, delete the document
    vector_store.delete_document(doc.id)
    assert vector_store.count_documents() == 0
    assert vector_store.get_document(doc.id) is None


@pytest.mark.unit
def test_delete_multiple_documents(vector_store):
    # Add multiple documents
    docs = [
        Document(
            id=f"test_id_{i}",
            content=f"test content {i}",
            embedding=Vector(value=np.random.rand(100).tolist()),
        )
        for i in range(3)
    ]
    vector_store.add_documents(docs)
    assert vector_store.count_documents() == 3

    # Delete multiple documents
    doc_ids = [doc.id for doc in docs[:2]]
    vector_store.delete_documents(doc_ids)
    assert vector_store.count_documents() == 1


@pytest.mark.unit
def test_clear_documents(vector_store):
    docs = [
        Document(
            id=f"test_id_{i}",
            content=f"test content {i}",
            embedding=Vector(value=np.random.rand(100).tolist()),
        )
        for i in range(3)
    ]
    vector_store.add_documents(docs)
    assert vector_store.count_documents() == 3

    vector_store.clear_documents()
    assert vector_store.count_documents() == 0


@pytest.mark.unit
def test_retrieve(vector_store):
    # Add some documents with known vectors
    docs = [
        Document(
            id=f"test_id_{i}",
            content=f"test content {i}",
            embedding=Vector(value=np.array([float(i)] * 100)),
        )
        for i in range(5)
    ]
    vector_store.add_documents(docs)

    # Create a query vector
    query_vector = Vector(value=np.array([0.5] * 100))

    # Retrieve similar documents
    results = vector_store.retrieve(query_vector, top_k=3)

    assert len(results) == 3
    assert all(isinstance(r, dict) for r in results)
    assert all(
        {"id", "content", "metadata", "embedding", "distance"}.issubset(r.keys())
        for r in results
    )
