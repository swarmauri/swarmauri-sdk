# Storage Adapters and Publisher Plugins

Peagen writes artifacts to a pluggable storage backend and can publish events during processing. Both systems are extensible so you can integrate your own infrastructure. The SDK bundles several implementations under ``peagen.plugins`` for convenience.

## Storage Adapters

`Peagen` accepts a `storage_adapter` implementing simple `upload()` and `download()` methods. Four adapters ship with the SDK:

- `FileStorageAdapter` – stores artifacts on the local filesystem.
- `MinioStorageAdapter` – targets S3 compatible object stores.
- `GithubStorageAdapter` – saves files into a GitHub repository.
- `GithubReleaseStorageAdapter` – uploads artifacts as release assets and
  exposes a `root_uri` like `ghrel://org/repo/tag/` for retrieval.
- `GitHttpStorageAdapter` – pushes to and fetches from a git HTTP server using
  URIs like `git+http://host/repo.git#branch/prefix`.

Enable any of these via `.peagen.toml` using the `[storage.adapters.<name>]`
tables. For example:

```toml
[storage]
default_storage_adapter = "file"

[storage.adapters.file]
output_dir = "./peagen_artifacts"

[storage.adapters.minio]
endpoint = "localhost:9000"
bucket = "peagen"

[storage.adapters.github]
token = "ghp_..."
org = "my-org"
repo = "my-repo"

[storage.adapters.gh_release]
token = "ghp_..."
org = "my-org"
repo = "my-repo"
tag = "v1.0.0"
```

To use a different solution, subclass one of these classes or implement the same two-method API and pass the instance when creating `Peagen`:

```python
from peagen.core import Peagen
from peagen.plugins.storage_adapters.file_storage_adapter import FileStorageAdapter

pea = Peagen(
    projects_payload_path="projects.yaml",
    storage_adapter=FileStorageAdapter("./artifacts"),
)
```

Any class providing `upload()` and `download()` can serve as the adapter, enabling integrations with cloud services or databases. The `upload()` method should return the artifact URI so Peagen can reference it in manifests and task payloads.

## Publisher Plugins

The CLI can emit JSON events such as `process.started` and `process.done`. The repository includes a `RedisPublisher` for Redis Pub/Sub and a `WebhookPublisher` for HTTP endpoints:


```python
from peagen.plugins.publishers.redis_publisher import RedisPublisher

bus = RedisPublisher("redis://localhost:6379/0")
bus.publish("peagen.events", {"type": "process.started"})
```

```python
from peagen.plugins.publishers.webhook_publisher import WebhookPublisher

bus = WebhookPublisher("https://example.com/peagen")
bus.publish("peagen.events", {"type": "process.started"})
```

You can also publish events to RabbitMQ using `RabbitMQPublisher`:

```python
from peagen.plugins.publishers.rabbitmq_publisher import RabbitMQPublisher

bus = RabbitMQPublisher(host="localhost", port=5672, exchange="", routing_key="peagen.events")
bus.publish("peagen.events", {"type": "process.started"})
```

To support another message bus, implement the same `publish()` method and use your class when wiring Peagen. See the `.peagen.toml` scaffold for configuration hints.
