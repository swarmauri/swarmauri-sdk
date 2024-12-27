import pytest
import tempfile
import os
from swarmauri.documents.concrete.Document import Document
from swarmauri.vector_stores.concrete.SqliteVectorStore import (
    SqliteVectorStore,
)


@pytest.fixture
def sqlite_db():
    # Create a temporary file that will act as the SQLite database
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_db:
        db_path = temp_db.name
    yield db_path
    # Clean up the temporary database file after the test
    os.remove(db_path)


@pytest.mark.unit
def test_ubc_resource(sqlite_db):
    vs = SqliteVectorStore(db_path=sqlite_db)
    assert vs.resource == "VectorStore"
    # assert vs.embedder.resource == "Embedding"


@pytest.mark.unit
def test_ubc_type(sqlite_db):
    vs = SqliteVectorStore(db_path=sqlite_db)
    assert vs.type == "SqliteVectorStore"


@pytest.mark.unit
def test_serialization(sqlite_db):
    vs = SqliteVectorStore(db_path=sqlite_db)
    assert vs.id == SqliteVectorStore.model_validate_json(vs.model_dump_json()).id


@pytest.mark.unit
def test_top_k(sqlite_db):
    vs = SqliteVectorStore(db_path=sqlite_db)
    documents = [
        Document(
            id="1",
            content="test",
            metadata={},
            embedding={"value": [0.1, 0.2, 0.3]},
        ),
        Document(
            id="2",
            content="test1",
            metadata={},
            embedding={"value": [0.4, 0.5, 0.6]},
        ),
        Document(
            id="3",
            content="test2",
            metadata={},
            embedding={"value": [0.7, 0.8, 0.9]},
        ),
        Document(
            id="4",
            content="test3",
            metadata={},
            embedding={"value": [0.1, 0.2, 0.2]},
        ),
    ]

    vs.add_documents(documents)
    assert len(vs.retrieve(query_vector=[0.1, 0.2, 0.25], top_k=2)) == 2
