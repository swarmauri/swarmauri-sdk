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
