import pytest
from unittest.mock import patch, MagicMock
from swarmauri_standard.documents.Document import Document
from swarmauri_vectorstore_neo4j.Neo4jVectorStore import Neo4jVectorStore


@pytest.fixture
def mock_driver():
    """Mock Neo4j driver"""
    mock_driver = MagicMock()
    mock_session = MagicMock()
    mock_transaction = MagicMock()

    # Set up the session context manager behavior
    mock_session.__enter__.return_value = mock_session
    mock_session.run.return_value = mock_transaction

    # Set up the driver's session method
    mock_driver.session.return_value = mock_session

    return mock_driver


@pytest.fixture
def vector_store(mock_driver):
    """Fixture for Neo4jVectorStore with mocked driver"""
    with patch("neo4j.GraphDatabase.driver", return_value=mock_driver):
        store = Neo4jVectorStore(
            uri="bolt://localhost:7687",
            user="neo4j",
            password="password",
            collection_name="TestCollection",
        )
        yield store


@pytest.mark.unit
def test_ubc_resource(vector_store):
    assert vector_store.resource == "VectorStore"


@pytest.mark.unit
def test_ubc_type(vector_store):
    assert vector_store.type == "Neo4jVectorStore"


@pytest.mark.unit
def test_serialization(vector_store):
    assert (
        vector_store.id
        == Neo4jVectorStore.model_validate_json(vector_store.model_dump_json()).id
    )


@pytest.mark.unit
def test_add_document(vector_store, mock_driver):
    """Test adding a single document"""
    doc = Document(id="doc1", content="Test content", metadata={"key": "value"})

    # Reset the mock to clear initialization calls
    mock_session = mock_driver.session().__enter__()
    mock_session.run.reset_mock()

    vector_store.add_document(doc)

    # Verify the correct query was executed
    mock_session.run.assert_called_once()
    call_args = mock_session.run.call_args[0][0]
    assert "MERGE (d:Document {id: $id})" in call_args


@pytest.mark.unit
def test_get_document(vector_store, mock_driver):
    """Test retrieving a document"""
    # Create a mock record with proper string metadata
    mock_record = {
        "id": "doc1",
        "content": "Test content",
        "metadata": '{"key": "value"}',
    }

    mock_session = mock_driver.session().__enter__()
    mock_session.run().single.return_value = mock_record

    result = vector_store.get_document("doc1")

    assert result.id == "doc1"
    assert result.content == "Test content"
    assert result.metadata == {"key": "value"}


@pytest.mark.unit
def test_retrieve(vector_store, mock_driver):
    """Test document retrieval with similarity search"""
    mock_records = [
        {
            "id": "doc1",
            "content": "Content 1",
            "metadata": '{"key": "value1"}',
            "distance": 0.5,
        },
        {
            "id": "doc2",
            "content": "Content 2",
            "metadata": '{"key": "value2"}',
            "distance": 0.8,
        },
    ]

    mock_session = mock_driver.session().__enter__()
    mock_session.run.return_value = mock_records

    results = vector_store.retrieve("test query", top_k=2)

    assert len(results) == 2
    assert results[0].id == "doc1"
    assert results[1].id == "doc2"


@pytest.mark.unit
def test_delete_document(vector_store, mock_driver):
    """Test document deletion"""
    # Reset the mock to clear initialization calls
    mock_session = mock_driver.session().__enter__()
    mock_session.run.reset_mock()

    vector_store.delete_document("doc1")

    mock_session.run.assert_called_once()
    call_args = mock_session.run.call_args[0][0]
    assert "MATCH (d:Document {id: $id})" in call_args
    assert "DETACH DELETE d" in call_args


@pytest.mark.unit
def test_update_document(vector_store, mock_driver):
    """Test document update"""
    doc = Document(
        id="doc1", content="Updated content", metadata={"key": "updated_value"}
    )

    # Reset the mock to clear initialization calls
    mock_session = mock_driver.session().__enter__()
    mock_session.run.reset_mock()

    vector_store.update_document("doc1", doc)

    mock_session.run.assert_called_once()
    call_args = mock_session.run.call_args[0][0]
    assert "MATCH (d:Document {id: $id})" in call_args
    assert "SET d.content = $content" in call_args
