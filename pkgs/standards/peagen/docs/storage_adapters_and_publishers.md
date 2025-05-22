# Storage Adapters and Publisher Plugins

Peagen writes artifacts to a pluggable storage backend and can publish events during processing. Both systems are extensible so you can integrate your own infrastructure.

## Storage Adapters

`Peagen` accepts a `storage_adapter` implementing simple `upload()` and `download()` methods. Four adapters ship with the SDK:

- `FileStorageAdapter` – stores artifacts on the local filesystem.
- `MinioStorageAdapter` – targets S3 compatible object stores.
- `GithubStorageAdapter` – saves files into a GitHub repository.
- `GithubReleaseStorageAdapter` – uploads artifacts as release assets.

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
from peagen.storage_adapters.file_storage_adapter import FileStorageAdapter

pea = Peagen(
    projects_payload_path="projects.yaml",
    storage_adapter=FileStorageAdapter("./artifacts"),
)
```

Any class providing `upload()` and `download()` can serve as the adapter, enabling integrations with cloud services or databases.

## Publisher Plugins

The CLI can emit JSON events such as `process.started` and `process.done`. One built-in publisher ships with the SDK:

- `RedisPublisher` – sends messages via Redis Pub/Sub.

Enable it in `.peagen.toml` using the `[publishers.adapters.redis]` table:

```toml
[publishers]
default_publisher = "redis"

[publishers.adapters.redis]
uri = "redis://localhost:6379/0"
channel = "peagen.events"
```

You can also instantiate it programmatically:

```python
from peagen.publishers.redis_publisher import RedisPublisher

bus = RedisPublisher("redis://localhost:6379/0")
bus.publish("peagen.events", {"type": "process.started"})
```

To support another message bus, implement the same `publish()` method and use your class when wiring Peagen. See the `.peagen.toml` scaffold for configuration hints.
