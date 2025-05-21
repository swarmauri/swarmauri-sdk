# Event-Driven Architecture (EDA) Protocol

Peagen can emit JSON events during processing to integrate with external workflows. This document outlines the common event types, payload structure, and routing conventions used by the CLI and library.

## Core Event Types

- `process.started` – emitted when a generation run begins.
- `process.done` – emitted after all files have been rendered. Includes the total runtime in seconds.
- `peagen.experiment.done` – sent by `peagen experiment` when a design of experiments expansion completes.

Additional custom events may be published by plugins or downstream tools, but the above form the core API guaranteed by Peagen.

## Payload Schema

Each event payload is a JSON object with a required top-level `type` key. Additional fields provide metadata about the run or experiment. Typical fields include:

- `seconds` – runtime duration for `process.done` events.
- `output` – path to the generated artifact or experiment bundle.
- `count` – number of design points produced by `peagen experiment`.
- `uri` – notification target used when publishing.

Publishers may attach extra keys as needed. Consumers should handle unknown fields gracefully.

## Routing Keys

By default events are published to the `peagen.events` channel. Specific events may use dedicated subjects such as `peagen.experiment.done`. When using the CLI, the channel can be overridden via the notifier URI:

```bash
peagen process --notify redis://localhost:6379/0/mychannel
```

Here `mychannel` becomes the routing key instead of `peagen.events`.

## Related Documentation

Examples of publishing events are shown in the [README](../README.md) and in [storage_adapters_and_publishers.md](storage_adapters_and_publishers.md). Use those snippets as a starting point when wiring Peagen into your own message bus.
