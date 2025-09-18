![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

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

`swarmauri_publisher_redis` provides a Redis Pub/Sub publisher that conforms to the Swarmauri [`PublishBase`](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_base) interface. The publisher serializes dictionaries to JSON before sending them to Redis channels, making it easy to exchange structured messages across your Swarmauri deployments.

## Installation

Choose the workflow that matches your project setup:

```bash
# Using pip
pip install swarmauri_publisher_redis

# Using Poetry
poetry add swarmauri_publisher_redis

# Using uv (https://docs.astral.sh/uv/)
uv add swarmauri_publisher_redis
# or install into the active environment
uv pip install swarmauri_publisher_redis
```

## Configuration

`RedisPublisher` accepts either a complete Redis connection URI or the individual connection settings. Mixing the two configuration styles is not supported.

- `uri`: Full Redis URI such as `redis://[:password]@host:port/db`.
- `host`, `port`, `db`: Required when `uri` is not provided. The publisher constructs the URI for you.
- `username`, `password`: Optional credentials used when building the URI.

If neither a URI nor the full host/port/db combination is supplied, initialization raises a `ValueError`.

## Usage

The publisher creates a Redis client from your connection information and publishes JSON-encoded payloads.

```python
from swarmauri_publisher_redis import RedisPublisher

publisher = RedisPublisher(
    host="localhost",
    port=6379,
    db=0,
)

publisher.publish("my_channel", {"message": "Hello Redis!"})
```

### Using a Redis URI

You can also configure the publisher with a pre-built connection string:

```python
from swarmauri_publisher_redis import RedisPublisher

publisher = RedisPublisher(uri="redis://localhost:6379/0")
publisher.publish("alerts", {"severity": "info", "detail": "It works!"})
```

## Additional Notes

- Payloads are serialized with `json.dumps` before being sent to Redis.
- A Redis server must be reachable for the publish call to succeed outside of tests.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.