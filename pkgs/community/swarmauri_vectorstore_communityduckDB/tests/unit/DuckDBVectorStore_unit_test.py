import pytest
import os
import json
from swarmauri_standard.documents.Document import Document
from swarmauri_vectorstore_communityduckDB.DuckDBVectorStore import DuckDBVectorStore


@pytest.fixture(params=[":memory:", "test_db.db"])
def vector_store(request, tmp_path):
    if request.param == ":memory:":
        vs = DuckDBVectorStore(database_name=":memory:")
    else:
        db_path = tmp_path / request.param
        vs = DuckDBVectorStore(database_name=str(db_path), persist_dir=str(tmp_path))
    vs.connect()
    yield vs
    vs.disconnect()
    if request.param != ":memory:":
        os.remove(db_path)


@pytest.fixture
def sample_documents():
    return [
        Document(
            id="1",
            content="The quick brown fox jumps over the lazy dog",
            metadata={"animal": "fox"},
        ),
        Document(
            id="2",
            content="A lazy dog sleeps all day not fox",
            metadata={"animal": "dog"},
        ),
        Document(
            id="3",
            content="The brown fox is quick and clever",
            metadata={"animal": "fox"},
        ),
    ]


@pytest.mark.unit
def test_ubc_resource(vector_store):
    assert vector_store.resource == "VectorStore"
    assert vector_store.embedder.resource == "Embedding"


@pytest.mark.unit
def test_ubc_type(vector_store):
    assert vector_store.type == "DuckDBVectorStore"


@pytest.mark.unit
def test_serialization(vector_store):
    assert (
        vector_store.id
        == vector_store.model_validate_json(vector_store.model_dump_json()).id
    )


def test_add_and_get_document(vector_store):
    doc = Document(
        id="test1", content="This is a test document", metadata={"key": "value"}
    )
    vector_store.add_document(doc)

    retrieved_doc = vector_store.get_document("test1")
    assert retrieved_doc is not None
    assert retrieved_doc.id == doc.id
    assert retrieved_doc.content == doc.content
    assert retrieved_doc.metadata == doc.metadata


def test_add_and_get_multiple_documents(vector_store, sample_documents):
    vector_store.add_documents(sample_documents)

    all_docs = vector_store.get_all_documents()
    assert len(all_docs) == len(sample_documents)
    assert set(doc.id for doc in all_docs) == set(doc.id for doc in sample_documents)


def test_delete_document(vector_store):
    doc = Document(id="test_delete", content="This document will be deleted")
    vector_store.add_document(doc)

    vector_store.delete_document("test_delete")
    assert vector_store.get_document("test_delete") is None


def test_update_document(vector_store):
    original_doc = Document(id="test_update", content="Original content")
    vector_store.add_document(original_doc)

    # Delete the old document before adding the updated one
    vector_store.delete_document("test_update")

    updated_doc = Document(id="test_update", content="Updated content")
    vector_store.add_document(updated_doc)

    retrieved_doc = vector_store.get_document("test_update")
    assert retrieved_doc.content == "Updated content"


def test_persistence(tmp_path):
    db_path = tmp_path / "persist_test.db"
    vs1 = DuckDBVectorStore(database_name=str(db_path), persist_dir=str(tmp_path))
    vs1.connect()

    doc = Document(id="persist_test", content="This document should persist")
    vs1.add_document(doc)
    vs1.disconnect()

    vs2 = DuckDBVectorStore.from_local(str(db_path))
    vs2.connect()
    retrieved_doc = vs2.get_document("persist_test")
    assert retrieved_doc is not None
    assert retrieved_doc.content == "This document should persist"
    vs2.disconnect()

    os.remove(db_path)


def test_metadata_query(vector_store, sample_documents):
    vector_store.add_documents(sample_documents)

    fox_docs = [
        doc
        for doc in vector_store.get_all_documents()
        if doc.metadata.get("animal") == "fox"
    ]
    assert len(fox_docs) == 2


def test_retrieve(vector_store, sample_documents):
    vector_store.add_documents(sample_documents)

    results = vector_store.retrieve("fox jumping", top_k=2)
    assert len(results) == 2
    assert all("fox" in doc.content.lower() for doc in results)


def test_model_dump_json(vector_store, sample_documents):
    vector_store.add_documents(sample_documents)

    dumped = vector_store.model_dump_json()
    loaded = json.loads(dumped)

    assert loaded["type"] == "DuckDBVectorStore"
    assert loaded["database_name"] == vector_store.database_name
    assert loaded["table_name"] == vector_store.table_name

    # Ensure the connection is closed during serialization
    assert vector_store._conn is None
