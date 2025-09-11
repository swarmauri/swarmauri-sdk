import json
import logging
from unittest.mock import MagicMock, patch
from urllib.parse import quote_plus

import pika
import pytest
from pydantic import ValidationError
from swarmauri_publisher_rabbitmq import RabbitMQPublisher


@pytest.fixture
def mock_pika_channel():
    """Fixture to mock pika.adapters.blocking_connection.BlockingChannel."""
    mock_chan = MagicMock(spec=pika.adapters.blocking_connection.BlockingChannel)
    return mock_chan


@pytest.fixture
def mock_pika_connection(mock_pika_channel):
    """Fixture to mock pika.BlockingConnection."""
    mock_conn = MagicMock(spec=pika.BlockingConnection)
    mock_conn.channel.return_value = mock_pika_channel
    # Mock the params.uri for reconnection logic if needed, though it's complex for unit test
    mock_conn.params = MagicMock()
    mock_conn.params.uri = "amqp://mockuser:mockpass@mockhost:5672/"
    return mock_conn


@pytest.fixture
@patch("pika.BlockingConnection")
@patch("pika.URLParameters")
def publisher(
    mock_url_params,
    mock_blocking_connection_constructor,
    mock_pika_connection,
    mock_pika_channel,
):
    """Fixture to create a RabbitMQPublisher instance with mocked Pika client."""
    mock_blocking_connection_constructor.return_value = mock_pika_connection
    mock_pika_connection.channel.return_value = mock_pika_channel

    pub = RabbitMQPublisher(
        host="localhost",
        port=5672,
        username="guest",
        password="guest",
        exchange="test_exchange",
    )
    # Allow access to the mocks for assertions in tests
    pub._mocks = {
        "url_params": mock_url_params,
        "blocking_connection_constructor": mock_blocking_connection_constructor,
        "connection": mock_pika_connection,
        "channel": mock_pika_channel,
    }
    return pub


@pytest.fixture
@patch("pika.BlockingConnection")
@patch("pika.URLParameters")
def publisher_with_uri(
    mock_url_params,
    mock_blocking_connection_constructor,
    mock_pika_connection,
    mock_pika_channel,
):
    """Fixture to create a RabbitMQPublisher instance using a URI with mocked Pika client."""
    mock_blocking_connection_constructor.return_value = mock_pika_connection
    mock_pika_connection.channel.return_value = mock_pika_channel

    test_uri = "amqps://user:secret@rabbitmq.example.com:5671/%2Fvhost"
    pub = RabbitMQPublisher(uri=test_uri, exchange="uri_exchange")
    pub._mocks = {
        "url_params": mock_url_params,
        "blocking_connection_constructor": mock_blocking_connection_constructor,
        "connection": mock_pika_connection,
        "channel": mock_pika_channel,
    }
    return pub


@pytest.mark.unit
def test_ubc_resource(publisher):
    assert publisher.resource == "Publisher"


@pytest.mark.unit
def test_ubc_type(publisher):
    assert publisher.type == "RabbitMQPublisher"


@pytest.mark.unit
@patch("pika.BlockingConnection")
@patch("pika.URLParameters")
def test_initialization_with_host_port_exchange(
    mock_url_params,
    mock_blocking_connection_constructor,
    mock_pika_connection,
    mock_pika_channel,
):
    mock_blocking_connection_constructor.return_value = mock_pika_connection
    mock_pika_connection.channel.return_value = mock_pika_channel

    instance = RabbitMQPublisher(
        host="rabbithost",
        port=1234,
        username="testuser",
        password="testpassword",
        exchange="my_direct_exchange",
    )
    assert isinstance(instance.id, str)

    expected_uri = (
        f"amqp://{quote_plus('testuser')}:{quote_plus('testpassword')}@rabbithost:1234/"
    )
    mock_url_params.assert_called_once_with(expected_uri)
    mock_blocking_connection_constructor.assert_called_once_with(
        mock_url_params.return_value
    )
    mock_pika_connection.channel.assert_called_once()
    mock_pika_channel.exchange_declare.assert_called_once_with(
        exchange="my_direct_exchange", exchange_type="direct", durable=True
    )


@pytest.mark.unit
@patch("pika.BlockingConnection")
@patch("pika.URLParameters")
def test_initialization_with_uri_exchange(
    mock_url_params,
    mock_blocking_connection_constructor,
    mock_pika_connection,
    mock_pika_channel,
):
    mock_blocking_connection_constructor.return_value = mock_pika_connection
    mock_pika_connection.channel.return_value = mock_pika_channel

    test_uri = "amqp://user:pass@customhost:5678/vhost_path"
    instance = RabbitMQPublisher(uri=test_uri, exchange="another_exchange")
    assert isinstance(instance.id, str)

    mock_url_params.assert_called_once_with(test_uri)
    mock_blocking_connection_constructor.assert_called_once_with(
        mock_url_params.return_value
    )
    mock_pika_connection.channel.assert_called_once()
    mock_pika_channel.exchange_declare.assert_called_once_with(
        exchange="another_exchange", exchange_type="direct", durable=True
    )


@pytest.mark.unit
def test_initialization_missing_args():
    with pytest.raises(
        ValidationError, match="Field required"
    ):  # Pydantic v2 for missing 'exchange'
        RabbitMQPublisher(host="localhost", port=5672)

    with pytest.raises(ValueError, match="When no `uri` is given, `host` is required."):
        RabbitMQPublisher(exchange="test_exchange")  # Missing host

    # Port has a default, so this is okay if host and exchange are provided
    try:
        with patch("pika.BlockingConnection"), patch("pika.URLParameters"):
            RabbitMQPublisher(host="localhost", exchange="test_exchange")
    except ValueError:
        pytest.fail(
            "Initialization should succeed if host and exchange are provided, port has default"
        )


@pytest.mark.unit
def test_initialization_mixed_args():
    with pytest.raises(
        ValueError,
        match="Cannot specify both `uri` and individual host/port/username/password.",
    ):
        RabbitMQPublisher(
            uri="amqp://localhost", host="otherhost", exchange="test_exchange"
        )


@pytest.mark.unit
def test_serialization(publisher_with_uri):
    logging.info(
        f"Testing serialization and deserialization of RabbitMQPublisher with URI = {publisher_with_uri.uri}, Exchange = {publisher_with_uri.exchange}"
    )
    # To make this test pass, the mocked pika objects need to be setup during model_validate_json
    # This is complex. A simpler check is that the config fields are preserved.
    original_dump = publisher_with_uri.model_dump()

    with patch("pika.BlockingConnection"), patch("pika.URLParameters"):
        rehydrated_publisher = RabbitMQPublisher.model_validate(original_dump)

    assert publisher_with_uri.id == rehydrated_publisher.id  # id is from ComponentBase
    assert publisher_with_uri.uri == rehydrated_publisher.uri
    assert publisher_with_uri.exchange == rehydrated_publisher.exchange
    assert publisher_with_uri.type == rehydrated_publisher.type


@pytest.mark.unit
def test_publish_message(publisher):
    """Test that the publish method calls the Pika channel's basic_publish."""
    test_routing_key = "test_routing_key"
    test_payload = {"message": "hello rabbit", "value": 456}
    expected_json_payload_bytes = json.dumps(test_payload).encode()

    publisher.publish(test_routing_key, test_payload)

    publisher._mocks["channel"].basic_publish.assert_called_once_with(
        exchange=publisher.exchange,
        routing_key=test_routing_key,
        body=expected_json_payload_bytes,
        properties=pika.BasicProperties(
            delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
        ),
    )


@pytest.mark.unit
@patch("pika.BlockingConnection")
@patch("pika.URLParameters")
def test_del_closes_connection(
    mock_url_params,
    mock_blocking_connection_constructor,
    mock_pika_connection,
    mock_pika_channel,
):
    """Test that __del__ attempts to close the connection."""
    mock_blocking_connection_constructor.return_value = mock_pika_connection
    mock_pika_connection.channel.return_value = mock_pika_channel
    mock_pika_connection.is_closed = False  # Simulate open connection

    publisher_instance = RabbitMQPublisher(
        host="localhost", exchange="del_test_exchange"
    )

    del publisher_instance
    mock_pika_connection.close.assert_called_once()
