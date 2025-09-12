![Swarmauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

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

This package provides a RabbitMQ publisher implementation conforming to the Swarmauri `PublishBase` interface.

## Installation

This package is part of the Swarmauri SDK monorepo.

## Usage

```python
from swarmauri_publisher_rabbitmq import RabbitMQPublisher

# Example usage with host/port
publisher = RabbitMQPublisher(
    host="localhost",
    port=5672,
    username="guest",
    password="guest",
    exchange="my_exchange"
)
publisher.publish(channel="my_routing_key", payload={"message": "Hello RabbitMQ!"})

# Example usage with URI
# publisher_uri = RabbitMQPublisher(
#     uri="amqp://guest:guest@localhost:5672/",
#     exchange="my_exchange"
# )
# publisher_uri.publish(channel="my_routing_key", payload={"message": "Hello via URI!"})
```