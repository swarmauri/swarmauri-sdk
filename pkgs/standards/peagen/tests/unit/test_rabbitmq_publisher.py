import json
from unittest.mock import MagicMock, patch

import pytest

from peagen.publishers.rabbitmq_publisher import RabbitMQPublisher


@pytest.mark.unit
def test_init_with_uri():
    fake_channel = MagicMock()
    fake_conn = MagicMock(channel=MagicMock(return_value=fake_channel))
    with patch("pika.URLParameters") as mock_params, patch(
        "pika.BlockingConnection", return_value=fake_conn
    ) as mock_conn:
        mock_params.return_value = "params"
        pub = RabbitMQPublisher(
            uri="amqp://guest:guest@localhost:5672/", exchange="ex", routing_key="rk"
        )
        mock_params.assert_called_once_with("amqp://guest:guest@localhost:5672/")
        mock_conn.assert_called_once_with("params")
        assert pub._exchange == "ex"
        assert pub._routing_key == "rk"
        assert pub._channel is fake_channel


@pytest.mark.unit
def test_init_with_host_and_port():
    fake_channel = MagicMock()
    fake_conn = MagicMock(channel=MagicMock(return_value=fake_channel))
    with patch("pika.URLParameters") as mock_params, patch(
        "pika.BlockingConnection", return_value=fake_conn
    ) as mock_conn:
        mock_params.return_value = "params"
        RabbitMQPublisher(host="localhost", port=5672)
        mock_params.assert_called_once_with("amqp://localhost:5672/")
        mock_conn.assert_called_once_with("params")


@pytest.mark.unit
def test_init_with_credentials():
    with patch("pika.URLParameters") as mock_params, patch(
        "pika.BlockingConnection", return_value=MagicMock(channel=MagicMock())
    ):
        mock_params.return_value = "params"
        RabbitMQPublisher(host="localhost", port=5672, username="user", password="pass")
        mock_params.assert_called_once_with("amqp://user:pass@localhost:5672/")


@pytest.mark.unit
def test_mixed_config_error():
    with pytest.raises(ValueError):
        RabbitMQPublisher(uri="amqp://localhost", host="localhost")


@pytest.mark.unit
def test_missing_host_port_error():
    with pytest.raises(ValueError):
        RabbitMQPublisher(host="localhost")


@pytest.mark.unit
def test_publish_message():
    fake_channel = MagicMock()
    fake_conn = MagicMock(channel=MagicMock(return_value=fake_channel))
    with patch("pika.URLParameters", return_value="params"), patch(
        "pika.BlockingConnection", return_value=fake_conn
    ):
        pub = RabbitMQPublisher(host="localhost", port=5672, exchange="ex")
        pub.publish("rk", {"a": 1})
        fake_channel.basic_publish.assert_called_once_with(
            exchange="ex",
            routing_key="rk",
            body=json.dumps({"a": 1}).encode(),
        )


