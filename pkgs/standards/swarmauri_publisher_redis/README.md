![Swarmauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_publisher_redis/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_publisher_redis" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_publisher_redis/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_publisher_redis.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_publisher_redis/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_publisher_redis" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_publisher_redis/">
        <img src="https://img.shields.io/pypi/l/swarmauri_publisher_redis" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_publisher_redis/">
        <img src="https://img.shields.io/pypi/v/swarmauri_publisher_redis?label=swarmauri_publisher_redis&color=green" alt="PyPI - swarmauri_publisher_redis"/></a>

</p>

---

# Swarmauri Redis Publisher

This package provides a Redis Pub/Sub publisher implementation conforming to the Swarmauri `PublishBase` interface.

## Installation

```bash
# Add installation instructions if applicable, e.g., pip install .
```

## Usage

```python
from swarmauri_publisher_redis import RedisPublisher

# Example usage
publisher = RedisPublisher(host="localhost", port=6379, db=0)
publisher.publish("my_channel", {"message": "Hello Redis!"})
```