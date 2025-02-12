from unittest.mock import MagicMock, patch

import pytest
from swarmauri_standard.documents.Document import Document
from swarmauri_vectorstore_redis.RedisDocumentRetriever import RedisDocumentRetriever


@pytest.fixture
def mock_redis_client():
    """Fixture for a mocked Redis client."""
    mock_client = MagicMock()
    mock_client.search.return_value = MagicMock(docs=[])
    return mock_client


@pytest.fixture
def retriever():
    """Fixture for a RedisDocumentRetriever instance."""

    return RedisDocumentRetriever(
        redis_idx_name="test_index", redis_host="localhost", redis_port=6379
    )

@pytest.mark.unit
def test_ubc_resource(retriever):
    assert retriever.resource == "DocumentStore"


@pytest.mark.unit
def test_ubc_type(retriever):
    assert retriever.type == "RedisDocumentRetriever"


@pytest.mark.unit
def test_serialization(retriever):
    assert (
        retriever.id
        == RedisDocumentRetriever.model_validate_json(
            retriever.model_dump_json()
        ).id
    )


@pytest.mark.unit
def test_lazy_client_initialization(retriever):
    """Test lazy initialization of Redis client."""
    with patch(
        "swarmauri_vectorstore_redis.RedisDocumentRetriever.Client"
    ) as mock_client_class:
        # Trigger client initialization.
        _ = retriever.redis_client
        mock_client_class.assert_called_once_with(
            "test_index", host="localhost", port=6379
        )


@pytest.mark.unit
def test_retrieve_documents(retriever):
    """Test document retrieval functionality using the Document class."""
    # Create real Document instances.
    doc1 = Document(id="doc1", content="Test document 1", metadata={"field1": "value1"})

    doc2 = Document(id="doc2", content="Test document 2", metadata={"field2": "value2"})

    with patch(
        "swarmauri_vectorstore_redis.RedisDocumentRetriever.Client"
    ) as mock_client_class:
        mock_client = mock_client_class.return_value
        # Simulate a search result returning our Document instances.
        mock_client.search.return_value = MagicMock(docs=[doc1, doc2])
        results = retriever.retrieve("test query", top_k=2)
        # Verify the returned documents.
        assert len(results) == 2
        assert results[0].id == "doc1"
        assert results[0].content == "Test document 1"
        assert results[1].id == "doc2"
        assert results[1].content == "Test document 2"
