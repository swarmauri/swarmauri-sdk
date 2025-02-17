import pytest
from swarmauri_standard.documents.Document import Document
from swarmauri_community.vector_stores.concrete.AnnoyVectorStore import AnnoyVectorStore


# Fixture for creating an AnnoyVectorStore instance
@pytest.fixture
def vector_store():
    vs = AnnoyVectorStore(
        collection_name="test_annoy",
        vector_size=100,
    )
    vs.connect()
    yield vs
    # Cleanup after tests
    vs.delete()


@pytest.mark.unit
def test_ubc_resource(vector_store):
    assert vector_store.resource == "VectorStore"
    assert vector_store.embedder.resource == "Embedding"


@pytest.mark.unit
def test_ubc_type(vector_store):
    assert vector_store.type == "AnnoyVectorStore"


@pytest.mark.unit
def test_serialization(vector_store):
    assert (
        vector_store.id
        == AnnoyVectorStore.model_validate_json(vector_store.model_dump_json()).id
    )


@pytest.mark.unit
def test_top_k(vector_store):
    documents = [
        Document(content="test"),
        Document(content="test1"),
        Document(content="test2"),
        Document(content="test3"),
    ]

    vector_store.add_documents(documents)
    results = vector_store.retrieve(query="test", top_k=2)
    assert len(results) == 2


@pytest.mark.unit
def test_document_count(vector_store):
    documents = [
        Document(content="test1"),
        Document(content="test2"),
        Document(content="test3"),
    ]

    vector_store.add_documents(documents)
    assert vector_store.document_count() == 3


@pytest.mark.unit
def test_get_document(vector_store):
    doc = Document(content="test document")
    vector_store.add_document(doc)
    retrieved_doc = vector_store.get_document(doc.id)
    assert retrieved_doc.id == doc.id
    assert retrieved_doc.content == doc.content
