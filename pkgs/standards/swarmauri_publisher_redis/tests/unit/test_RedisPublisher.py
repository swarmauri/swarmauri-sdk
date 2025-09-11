import json
import logging
from unittest.mock import MagicMock, patch

import pytest
import redis
from swarmauri_publisher_redis import RedisPublisher


@pytest.fixture
def mock_redis_client():
    """Fixture to mock the redis.Redis client."""
    mock_client = MagicMock(spec=redis.Redis)
    return mock_client


@pytest.fixture
@patch("redis.from_url")
def publisher(mock_from_url, mock_redis_client):
    """Fixture to create a RedisPublisher instance with a mocked Redis client."""
    mock_from_url.return_value = mock_redis_client
    return RedisPublisher(host="localhost", port=6379, db=0)


@pytest.fixture
def publisher_with_uri():
    """Fixture to create a RedisPublisher instance using a URI."""
    with patch("redis.from_url") as mock_from_url:
        mock_from_url.return_value = MagicMock(spec=redis.Redis)
        yield RedisPublisher(uri="redis://localhost:6379/0")


@pytest.mark.unit
def test_ubc_resource(publisher):
    assert publisher.resource == "Publisher"


@pytest.mark.unit
def test_ubc_type(publisher):
    assert publisher.type == "RedisPublisher"


@pytest.mark.unit
@patch("redis.from_url")
def test_initialization_with_host_port_db(mock_from_url):
    mock_from_url.return_value = MagicMock(spec=redis.Redis)
    instance = RedisPublisher(host="testhost", port=1234, db=1)
    assert isinstance(instance.id, str)
    mock_from_url.assert_called_once_with(
        "redis://testhost:1234/1", decode_responses=True
    )


@pytest.mark.unit
@patch("redis.from_url")
def test_initialization_with_uri(mock_from_url):
    mock_from_url.return_value = MagicMock(spec=redis.Redis)
    test_uri = "redis://user:pass@customhost:5678/2"
    instance = RedisPublisher(uri=test_uri)
    assert isinstance(instance.id, str)
    mock_from_url.assert_called_once_with(test_uri, decode_responses=True)


@pytest.mark.unit
def test_initialization_missing_args():
    expected_error_message = "Redis connection configuration is incomplete: provide `uri`, or all of \\(`host`, `port`, `db`\\)\\."

    with pytest.raises(
        ValueError,
        match=expected_error_message,
    ):
        RedisPublisher()

    with pytest.raises(
        ValueError,
        match=expected_error_message,
    ):
        RedisPublisher(host="localhost")

    with pytest.raises(
        ValueError,
        match=expected_error_message,
    ):
        RedisPublisher(host="localhost", port=6379)


@pytest.mark.unit
def test_initialization_mixed_args():
    with pytest.raises(
        ValueError,
        match="Cannot specify both `uri` and individual host/port/db/password/username.",
    ):
        RedisPublisher(uri="redis://localhost:6379/0", host="otherhost")


@pytest.mark.unit
def test_serialization(publisher_with_uri):
    logging.info(
        f"Testing serialization and deserialization of RedisPublisher with URI = {publisher_with_uri}"
    )
    assert (
        publisher_with_uri.id
        == RedisPublisher.model_validate_json(publisher_with_uri.model_dump_json()).id
    )


@pytest.mark.unit
def test_publish_message(publisher):
    """Test that the publish method calls the Redis client's publish."""
    test_channel = "test_channel"
    test_payload = {"message": "hello", "value": 123}
    expected_json_payload = json.dumps(test_payload)

    publisher.publish(test_channel, test_payload)

    publisher._client.publish.assert_called_once_with(
        test_channel, expected_json_payload
    )
