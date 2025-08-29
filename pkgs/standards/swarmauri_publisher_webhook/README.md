# Swarmauri Webhook Publisher

A Swarmauri component for publishing messages to an HTTP webhook endpoint.

## Installation

```bash
pip install swarmauri_publisher_webhook
```

## Usage

```python
from swarmauri_publisher_webhook import WebhookPublisher

publisher = WebhookPublisher(url="https://your-webhook-endpoint.com/hook")

publisher.publish(
    channel="my_data_stream",
    payload={"message": "Hello, webhook!", "value": 123}
)
```
