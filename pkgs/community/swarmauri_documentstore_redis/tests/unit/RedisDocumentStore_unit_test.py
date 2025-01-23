import pytest
from swarmauri_documentstore_redis.RedisDocumentStore import RedisDocumentStore


@pytest.fixture(scope="module")
def redis_document_store():
    return RedisDocumentStore("localhost", "", 6379, 0)


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
