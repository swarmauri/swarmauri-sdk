# Git Filters and Publisher Plugins

Peagen writes artifacts through pluggable **git filters** and can publish events during processing. These systems are extensible so you can integrate your own infrastructure. Filter implementations are provided as standalone packages under ``swarmauri-gitfilter-*``.

``storage_adapters`` have been deprecated. Use ``peagen init filter`` to set up a git filter instead and reference it via ``[storage.filters]`` in ``.peagen.toml``.

Workspaces themselves may be managed in a Git repository using the
``vcs`` plugin group. See :doc:`git_vcs` for details.

## Git Filters

``Peagen`` now accepts a ``git_filter`` implementing ``upload()`` and ``download()`` methods. Install the appropriate package—such as ``swarmauri-gitfilter-minio``, ``swarmauri-gitfilter-gh-release``, or ``swarmauri-gitfilter-s3fs``—to enable a filter. Credentials may be provided under the corresponding ``[storage.filters.<name>]`` tables in ``.peagen.toml``.

Enable any of these via `.peagen.toml` using the `[storage.filters.<name>]`
tables. For example:

```toml
[storage]
default_filter = "file"

[storage.filters.file]
output_dir = "./peagen_artifacts"

[storage.filters.minio]
endpoint = "localhost:9000"
bucket = "peagen"

[storage.filters.github]
token = "ghp_..."
org = "my-org"
repo = "my-repo"

[storage.filters.gh_release]
token = "ghp_..."
org = "my-org"
repo = "my-repo"
tag = "v1.0.0"
```

To use a different solution, subclass one of these classes or implement the same two-method API and pass the instance when creating `Peagen`:

```python
from peagen.core import Peagen
from peagen.plugins import PluginManager

pm = PluginManager({})
MinioFilter = pm.get("git_filters", "minio")

pea = Peagen(
    projects_payload_path="projects.yaml",
    git_filter=MinioFilter.from_uri("s3://localhost:9000/peagen"),
)
```

Any class providing `upload()` and `download()` can serve as the adapter, enabling integrations with cloud services or databases. The `upload()` method should return the artifact URI so Peagen can reference it in Git commits and task payloads.

## Publisher Plugins

The CLI can emit JSON events such as `process.started` and `process.done`. The repository includes a `RedisPublisher` for Redis Pub/Sub and a `WebhookPublisher` for HTTP endpoints:


```python
from peagen.plugins import PluginManager

pm = PluginManager({})
RedisPublisher = pm.get("publishers", "redis")

bus = RedisPublisher("redis://localhost:6379/0")
bus.publish("peagen.events", {"type": "process.started"})
```

```python
WebhookPublisher = pm.get("publishers", "webhook")

bus = WebhookPublisher("https://example.com/peagen")
bus.publish("peagen.events", {"type": "process.started"})
```

You can also publish events to RabbitMQ using `RabbitMQPublisher`:

```python
RabbitMQPublisher = pm.get("publishers", "rabbitmq")

bus = RabbitMQPublisher(host="localhost", port=5672, exchange="", routing_key="peagen.events")
bus.publish("peagen.events", {"type": "process.started"})
```

To support another message bus, implement the same `publish()` method and use your class when wiring Peagen. See the `.peagen.toml` scaffold for configuration hints.
