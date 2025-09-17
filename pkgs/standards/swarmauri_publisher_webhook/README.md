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

`WebhookPublisher` is a Swarmauri component that delivers JSON events to an HTTP
endpoint. It keeps an internal `httpx.Client` session for efficient reuse and
raises a `RuntimeError` when the webhook cannot be reached or responds with a
non-success status code.

## Installation

Choose the tool that fits your workflow:

```bash
# pip
pip install swarmauri_publisher_webhook

# Poetry
poetry add swarmauri_publisher_webhook

# uv (install the tool if you do not already have it)
curl -LsSf https://astral.sh/uv/install.sh | sh
uv add swarmauri_publisher_webhook
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

The publisher posts a JSON object shaped as `{"channel": ..., "payload": ...}`
to the configured URL. Wrap calls to `publish` in your own error handling if you
need to catch connectivity or webhook-side failures.
