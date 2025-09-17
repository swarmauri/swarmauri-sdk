![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_publisher_rabbitmq/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_publisher_rabbitmq" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_publisher_rabbitmq/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_publisher_rabbitmq.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_publisher_rabbitmq/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_publisher_rabbitmq" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_publisher_rabbitmq/">
        <img src="https://img.shields.io/pypi/l/swarmauri_publisher_rabbitmq" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_publisher_rabbitmq/">
        <img src="https://img.shields.io/pypi/v/swarmauri_publisher_rabbitmq?label=swarmauri_publisher_rabbitmq&color=green" alt="PyPI - swarmauri_publisher_rabbitmq"/></a>

</p>

---

# Swarmauri RabbitMQ Publisher

`RabbitMQPublisher` is the Swarmauri `PublishBase` implementation for RabbitMQ. The publisher opens a `pika.BlockingConnection`, ensures the target exchange exists, and emits JSON payloads using persistent delivery semantics.

## Highlights

- Configure using either a full AMQP URI or discrete host/port credential fields. Supplying both styles raises `ValueError`.
- Declares the target exchange as a durable direct exchange during instantiation.
- Serializes payloads with `json.dumps` and publishes with `delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE` so messages survive broker restarts.
- On `pika.exceptions.AMQPConnectionError` or `ChannelClosedByBroker` the publisher reconnects once, re-declares the exchange, and retries the publish.

## Installation

Choose the tool that fits your workflow:

```bash
# pip
pip install swarmauri_publisher_rabbitmq

# Poetry
poetry add swarmauri_publisher_rabbitmq

# uv
uv add swarmauri_publisher_rabbitmq
```

## Configuration

`RabbitMQPublisher` extends `PublishBase` and supports the following fields:

| Field | Required | Description |
| --- | --- | --- |
| `exchange` | ✅ | The exchange name to declare and publish to. Declared as a durable direct exchange. |
| `uri` | ⚪️ | Full AMQP URI. When provided, omit `host`/`port`/`username`/`password`. |
| `host` | ⚪️ | RabbitMQ host. Required when `uri` is omitted. |
| `port` | ⚪️ | RabbitMQ port. Supply the broker port (for example `5672`); the publisher does not insert a default when constructing the URI. |
| `username` | ⚪️ | Username used in the URI when `uri` is omitted. Automatically URL-encoded. |
| `password` | ⚪️ | Password used in the URI when `uri` is omitted. Automatically URL-encoded. |

The `publish(channel, payload)` method treats `channel` as the RabbitMQ routing key. `payload` must be JSON serialisable because it is serialized with `json.dumps` before publishing.

## Quickstart

Ensure RabbitMQ is reachable and that you have permission to declare the exchange. The example below shows the host/port configuration path.

```python
# README Quickstart Example
from swarmauri_publisher_rabbitmq import RabbitMQPublisher

publisher = RabbitMQPublisher(
    host="localhost",
    port=5672,
    username="guest",
    password="guest",
    exchange="demo_exchange",
)

publisher.publish(
    channel="demo.routing.key",
    payload={"message": "Hello RabbitMQ!"},
)
```

The constructor builds the AMQP URI from the supplied parts, opens a blocking connection, and declares `demo_exchange` as a durable direct exchange. Each call to `publish` JSON-encodes the payload and requests persistent delivery so the message survives broker restarts.

### Connecting with an AMQP URI

If you already have an AMQP URI, provide it directly and omit the individual connection fields:

```python
from swarmauri_publisher_rabbitmq import RabbitMQPublisher

publisher = RabbitMQPublisher(
    uri="amqp://guest:guest@localhost:5672/",
    exchange="demo_exchange",
)

publisher.publish(
    channel="demo.routing.key",
    payload={"message": "Hello RabbitMQ via URI!"},
)
```

## Behavior notes

- Credentials are URL-encoded via `urllib.parse.quote_plus` when constructing an AMQP URI from discrete fields, and a username can be supplied without a password if the broker permits it.
- `pika.BasicProperties` is called with `delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE`.
- If RabbitMQ closes the channel or the connection drops, the publisher closes the connection, recreates it with the original URI, re-declares the exchange, and retries the publish once.
- When the publisher instance is garbage-collected it closes the open connection if it is still active.
