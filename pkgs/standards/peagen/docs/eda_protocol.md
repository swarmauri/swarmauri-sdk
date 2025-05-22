# Peagen Event Protocol

Peagen publishes JSON messages to notify external systems about key events during processing. Messages are sent via a pluggable publisher interface (e.g. `RedisPublisher`).

## Event Structure

Each event is a JSON object with a top-level `type` field. Implementations may include additional fields for context.

```json
{
  "type": "process.started",
  "extra": {"project": "myproj"}
}
```

## Core Events

| Event Type               | Description                                     |
|--------------------------|-------------------------------------------------|
| `process.started`        | Emitted when `peagen process` begins processing |
| `process.done`           | Emitted after all projects are processed        |
| `peagen.experiment.done` | Emitted by the DOE generator on completion      |

## Routing Keys

Events are published on a channel or routing key. The default is `peagen.events` for general messages. `peagen.experiment.done` is a dedicated key for DOE results.

Use the CLI `--notify` flag to select the publisher and optionally override the channel:

```bash
peagen process projects.yaml --notify redis://localhost:6379/0/custom.events
```

The path component (`/custom.events`) becomes the channel name. See `storage_adapters_and_publishers.md` for configuring publishers.
