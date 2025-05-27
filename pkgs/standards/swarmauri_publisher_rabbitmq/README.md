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