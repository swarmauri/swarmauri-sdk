import pytest
from swarmauri_documentstore_redis.RedisDocumentStore import RedisDocumentStore
from swarmauri_standard.documents.Document import Document
from unittest.mock import MagicMock, patch
import json


@pytest.fixture(scope="module")
def redis_document_store():
    return RedisDocumentStore("localhost", "", 6379, 0)


@pytest.fixture(scope="module")
def mock_redis():
    with patch("redis.Redis") as mock:
        mock_instance = MagicMock()
        mock.return_value = mock_instance
        mock_instance.json.return_value = MagicMock()
        yield mock_instance


@pytest.mark.unit
def test_ubc_resource(redis_document_store):
    assert redis_document_store.resource == "DocumentStore"


@pytest.mark.unit
def test_ubc_typeredis_document_store(redis_document_store):
    assert redis_document_store.type == "RedisDocumentStore"


@pytest.mark.unit
def test_serialization(redis_document_store):
    assert (
        redis_document_store.id
        == RedisDocumentStore.model_validate_json(
            redis_document_store.model_dump_json()
        ).id
    )


@pytest.mark.unit
def test_add_document(redis_document_store, mock_redis):
    doc = Document(id="test1", content="test content")
    redis_document_store.add_document(doc)
    expected_data = doc.model_dump()
    expected_data.pop("id")
    mock_redis.json.return_value.set.assert_called_once_with(
        "test1", "$", json.dumps(expected_data)
    )


@pytest.mark.unit
def test_get_document(redis_document_store, mock_redis):
    mock_redis.json.return_value.get.return_value = json.dumps(
        {"content": "test content", "type": "Document"}
    )
    doc = redis_document_store.get_document("test1")
    assert doc["content"] == "test content"
    assert doc["type"] == "Document"


@pytest.mark.unit
def test_get_all_documents(redis_document_store, mock_redis):
    mock_redis.keys.return_value = ["doc1", "doc2"]
    mock_redis.get.side_effect = [
        json.dumps({"content": "content1", "type": "Document"}),
        json.dumps({"content": "content2", "type": "Document"}),
    ]
    docs = redis_document_store.get_all_documents()
    assert len(docs) == 2
    assert all(doc["type"] == "Document" for doc in docs)


@pytest.mark.unit
def test_update_document(redis_document_store, mock_redis):
    updated_doc = Document(id="test1", content="updated content")
    redis_document_store.update_document("test1", updated_doc)
    expected_data = updated_doc.model_dump()
    expected_data.pop("id")
    mock_redis.json.return_value.set.assert_called_with(
        "test1", "$", json.dumps(expected_data)
    )


@pytest.mark.unit
def test_delete_document(redis_document_store, mock_redis):
    redis_document_store.delete_document("test1")
    mock_redis.delete.assert_called_once_with("test1")


@pytest.mark.unit
def test_add_documents(redis_document_store, mock_redis):
    docs = [
        Document(id="test1", content="content1"),
        Document(id="test2", content="content2"),
    ]
    redis_document_store.add_documents(docs)
    assert mock_redis.pipeline.called
    pipeline = mock_redis.pipeline.return_value.__enter__.return_value
    assert len(pipeline.json.return_value.set.mock_calls) == 2


@pytest.mark.unit
def test_document_not_found(redis_document_store, mock_redis):
    mock_redis.json.return_value.get.return_value = None
    result = redis_document_store.get_document("nonexistent")
    assert result is None
