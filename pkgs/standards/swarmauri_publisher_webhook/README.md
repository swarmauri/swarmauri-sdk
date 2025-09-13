<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_light_mg8cmd.png">
  <source media="(prefers-color-scheme: light)" srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
  <!-- Fallback below (see #2) -->
  <img alt="Swarmauri Logo" src="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
</picture>

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
