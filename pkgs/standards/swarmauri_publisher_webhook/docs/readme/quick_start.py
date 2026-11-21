from swarmauri_publisher_webhook import WebhookPublisher

publisher = WebhookPublisher(url="https://your-webhook-endpoint.com/hook")

publisher.publish(
    channel="my_data_stream",
    payload={"message": "Hello, webhook!", "value": 123},
)
