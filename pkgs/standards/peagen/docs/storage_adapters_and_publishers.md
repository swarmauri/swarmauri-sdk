# Storage Adapters and Publisher Plugins

Peagen writes artifacts to a pluggable storage backend and can publish events during processing. Both systems are extensible so you can integrate your own infrastructure.

## Storage Adapters

`Peagen` accepts a `storage_adapter` implementing simple `upload()` and `download()` methods. Two adapters ship with the SDK:

- `FileStorageAdapter` – stores artifacts on the local filesystem.
- `MinioStorageAdapter` – targets S3 compatible object stores.

To use a different solution, subclass one of these classes or implement the same two-method API and pass the instance when creating `Peagen`:

```python
from peagen.core import Peagen
from peagen.storage_adapters.file_storage_adapter import FileStorageAdapter

pea = Peagen(
    projects_payload_path="projects.yaml",
    storage_adapter=FileStorageAdapter("./artifacts"),
)
```

Any class providing `upload()` and `download()` can serve as the adapter, enabling integrations with cloud services or databases.

## Publisher Plugins

The CLI can emit JSON events such as `process.started` and `process.done`. The repository includes a `RedisPublisher` for Redis Pub/Sub and a `WebhookPublisher` for HTTP endpoints:

```python
from peagen.publishers.redis_publisher import RedisPublisher

bus = RedisPublisher("redis://localhost:6379/0")
bus.publish("peagen.events", {"type": "process.started"})
```

```python
from peagen.publishers.webhook_publisher import WebhookPublisher

bus = WebhookPublisher("https://example.com/peagen")
bus.publish("peagen.events", {"type": "process.started"})
```

To support another message bus, implement the same `publish()` method and use your class when wiring Peagen. See the `.peagen.toml` scaffold for configuration hints.
