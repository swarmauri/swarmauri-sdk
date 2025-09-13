![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_publisher_webhook/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_publisher_webhook" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_publisher_webhook/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_publisher_webhook.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_publisher_webhook/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_publisher_webhook" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_publisher_webhook/">
        <img src="https://img.shields.io/pypi/l/swarmauri_publisher_webhook" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_publisher_webhook/">
        <img src="https://img.shields.io/pypi/v/swarmauri_publisher_webhook?label=swarmauri_publisher_webhook&color=green" alt="PyPI - swarmauri_publisher_webhook"/></a>

</p>

---

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
