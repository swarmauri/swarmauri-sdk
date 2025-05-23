import json
from unittest.mock import MagicMock, patch

import pytest

from peagen.publishers.redis_publisher import RedisPublisher


@pytest.mark.unit
def test_init_with_uri():
    fake = MagicMock()
    with patch("redis.from_url", return_value=fake) as mock_from_url:
        pub = RedisPublisher(uri="redis://localhost:6379/0")
        assert pub._client is fake
        mock_from_url.assert_called_once_with(
            "redis://localhost:6379/0", decode_responses=True
        )


@pytest.mark.unit
def test_init_with_host_port_db():
    fake = MagicMock()
    with patch("redis.from_url", return_value=fake) as mock_from_url:
        RedisPublisher(host="localhost", port=6379, db=1)
        mock_from_url.assert_called_once_with(
            "redis://localhost:6379/1", decode_responses=True
        )


@pytest.mark.unit
def test_init_with_auth():
    fake = MagicMock()
    with patch("redis.from_url", return_value=fake) as mock_from_url:
        RedisPublisher(
            host="localhost", port=6379, db=0, username="user", password="pass"
        )
        mock_from_url.assert_called_once_with(
            "redis://user:pass@localhost:6379/0", decode_responses=True
        )


@pytest.mark.unit
def test_mixed_config_error():
    with pytest.raises(ValueError):
        RedisPublisher(uri="redis://localhost", host="localhost")


@pytest.mark.unit
def test_missing_opts_error():
    with pytest.raises(ValueError):
        RedisPublisher(host="localhost", port=6379)


@pytest.mark.unit
def test_publish_json():
    client = MagicMock()
    with patch("redis.from_url", return_value=client):
        pub = RedisPublisher(uri="redis://localhost:6379/0")
        pub.publish("chan", {"a": 1})
        client.publish.assert_called_once_with("chan", json.dumps({"a": 1}))

