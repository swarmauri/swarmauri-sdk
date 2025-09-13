<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_light_mg8cmd.png">
  <source media="(prefers-color-scheme: light)" srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
  <!-- Fallback below (see #2) -->
  <img alt="Swarmauri Logo" src="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
</picture>

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