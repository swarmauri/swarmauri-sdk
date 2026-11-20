# swarmauri_publisher_rabbitmq

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_publisher_rabbitmq</strong></p>
<p align="center">A RabbitMQ publisher implementation for Swarmauri.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_publisher_rabbitmq/"><img alt="pypi: swarmauri_publisher_rabbitmq" src="https://img.shields.io/pypi/v/swarmauri_publisher_rabbitmq"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_publisher_rabbitmq/pyproject.toml"><img alt="Source version: 0.11.0.dev3" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev3&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_publisher_rabbitmq/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_publisher_rabbitmq/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_publisher_rabbitmq/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_publisher_rabbitmq/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_publisher_rabbitmq/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_publisher_rabbitmq/"><img alt="Monthly PyPI downloads: swarmauri_publisher_rabbitmq" src="https://img.shields.io/pypi/dm/swarmauri_publisher_rabbitmq"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_publisher_rabbitmq/README.md"><img alt="README hits: swarmauri_publisher_rabbitmq" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/standards/swarmauri_publisher_rabbitmq/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_publisher_rabbitmq/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_publisher_rabbitmq/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`RabbitMQPublisher` is the Swarmauri `PublishBase` implementation for RabbitMQ. The publisher opens a `pika.BlockingConnection`, ensures the target exchange exists, and emits JSON payloads using persistent delivery semantics.

### Why This Package

`swarmauri_publisher_rabbitmq` isolates this responsibility: A RabbitMQ publisher implementation for Swarmauri. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_publisher_rabbitmq/swarmauri_publisher_rabbitmq/__init__.py) exposes `RabbitMQPublisher`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_publisher_rabbitmq` when your integration needs a RabbitMQ publisher implementation for Swarmauri. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Configure using either a full AMQP URI or discrete host/port credential fields. Supplying both styles raises `ValueError`.
- Declares the target exchange as a durable direct exchange during instantiation.
- Serializes payloads with `json.dumps` and publishes with `delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE` so messages survive broker restarts.
- On `pika.exceptions.AMQPConnectionError` or `ChannelClosedByBroker` the publisher reconnects once, re-declares the exchange, and retries the publish.

### Non-Goals

`swarmauri_publisher_rabbitmq` owns a RabbitMQ publisher implementation for Swarmauri. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_publisher_rabbitmq/pyproject.toml) declares runtime dependencies including `pika`, `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. Read the example’s inputs and service requirements before execution.

### Installation

Choose the tool that fits your workflow:

```bash
# pip
pip install swarmauri_publisher_rabbitmq

# Poetry
poetry add swarmauri_publisher_rabbitmq

# uv
uv add swarmauri_publisher_rabbitmq
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_publisher_rabbitmq
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_publisher_rabbitmq
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_publisher_rabbitmq
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

Ensure RabbitMQ is reachable and that you have permission to declare the exchange. The example below shows the host/port configuration path.


The constructor builds the AMQP URI from the supplied parts, opens a blocking connection, and declares `demo_exchange` as a durable direct exchange. Each call to `publish` JSON-encodes the payload and requests persistent delivery so the message survives broker restarts.

**Connecting with an AMQP URI**

If you already have an AMQP URI, provide it directly and omit the individual connection fields:

```python
from swarmauri_publisher_rabbitmq import RabbitMQPublisher

publisher = RabbitMQPublisher(
    uri="amqp://guest:guest@localhost:5672/",
    exchange="demo_exchange",
)

publisher.publish(
    channel="demo.routing.key",
    payload={"message": "Hello RabbitMQ via URI!"},
)
```

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_publisher_rabbitmq/docs/readme/quick_start.py).

```python
# README Quickstart Example
from swarmauri_publisher_rabbitmq import RabbitMQPublisher

publisher = RabbitMQPublisher(
    host="localhost",
    port=5672,
    username="guest",
    password="guest",
    exchange="demo_exchange",
)

publisher.publish(
    channel="demo.routing.key",
    payload={"message": "Hello RabbitMQ!"},
)
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_publisher_rabbitmq` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_publisher_rabbitmq/docs/readme/usage.py).

```python
# README Quickstart Example
from swarmauri_publisher_rabbitmq import RabbitMQPublisher

publisher = RabbitMQPublisher(
    host="localhost",
    port=5672,
    username="guest",
    password="guest",
    exchange="demo_exchange",
)

publisher.publish(
    channel="demo.routing.key",
    payload={"message": "Hello RabbitMQ!"},
)
```
<!-- readme-standards:end example.usage -->

### Configuration

`RabbitMQPublisher` extends `PublishBase` and supports the following fields:

| Field | Required | Description |
| --- | --- | --- |
| `exchange` | Yes | The exchange name to declare and publish to. Declared as a durable direct exchange. |
| `uri` | Optional | Full AMQP URI. When provided, omit `host`/`port`/`username`/`password`. |
| `host` | Optional | RabbitMQ host. Required when `uri` is omitted. |
| `port` | Optional | RabbitMQ port. Supply the broker port (for example `5672`); the publisher does not insert a default when constructing the URI. |
| `username` | Optional | Username used in the URI when `uri` is omitted. Automatically URL-encoded. |
| `password` | Optional | Password used in the URI when `uri` is omitted. Automatically URL-encoded. |

The `publish(channel, payload)` method treats `channel` as the RabbitMQ routing key. `payload` must be JSON serialisable because it is serialized with `json.dumps` before publishing.

### Error Handling

The inspected `swarmauri_publisher_rabbitmq` source raises `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_publisher_rabbitmq` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `RabbitMQPublisher`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_publisher_rabbitmq` is located in `standards` and owns a RabbitMQ publisher implementation for Swarmauri. Source-declared APIs include `RabbitMQPublisher`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_publisher_rabbitmq/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_publisher_rabbitmq`.

Source-declared exports or types: `RabbitMQPublisher`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_publisher_rabbitmq/swarmauri_publisher_rabbitmq/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.publishers` → `RabbitMQPublisher` → `swarmauri_publisher_rabbitmq.rabbitmq_publisher:RabbitMQPublisher`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_publisher_rabbitmq` are `pika`, `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_publisher_rabbitmq/swarmauri_publisher_rabbitmq/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_publisher_rabbitmq` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_publisher_rabbitmq`, use the source-declared public interfaces (`RabbitMQPublisher`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_publisher_rabbitmq` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_publisher_rabbitmq/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_publisher_rabbitmq`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_publisher_rabbitmq/swarmauri_publisher_rabbitmq/__init__.py). The `swarmauri_publisher_rabbitmq` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_publisher_rabbitmq` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_publisher_rabbitmq` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_readme_example.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_publisher_rabbitmq/tests/test_readme_example.py)
- [tests/unit/test_RabbitMQPublisher.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_publisher_rabbitmq/tests/unit/test_RabbitMQPublisher.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_publisher_rabbitmq` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_publisher_rabbitmq/swarmauri_publisher_rabbitmq/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_publisher_rabbitmq` provides a RabbitMQ publisher implementation for Swarmauri; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_publisher_rabbitmq`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_publisher_rabbitmq/swarmauri_publisher_rabbitmq/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_publisher_rabbitmq` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_publisher_rabbitmq/swarmauri_publisher_rabbitmq/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_publisher_rabbitmq/pyproject.toml) provide the supporting context for `swarmauri_publisher_rabbitmq`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.
- [swarmauri_standard](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/swarmauri_standard/README.md): First-party Swarmauri standard components for agents, tools, parsers, vectors, model adapters, and composable intelligence workflows.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_publisher_rabbitmq](https://pypi.org/project/swarmauri_publisher_rabbitmq/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.

### Development Setup

Work from the `pkgs/standards/swarmauri_publisher_rabbitmq` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

**Behavior notes**

- Credentials are URL-encoded via `urllib.parse.quote_plus` when constructing an AMQP URI from discrete fields, and a username can be supplied without a password if the broker permits it.
- `pika.BasicProperties` is called with `delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE`.
- If RabbitMQ closes the channel or the connection drops, the publisher closes the connection, recreates it with the original URI, re-declares the exchange, and retries the publish once.
- When the publisher instance is garbage-collected it closes the open connection if it is still active.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_publisher_rabbitmq` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_publisher_rabbitmq/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_publisher_rabbitmq` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_publisher_rabbitmq` source version is `0.11.0.dev3`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_publisher_rabbitmq/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_publisher_rabbitmq/NOTICE) for attribution.
<!-- readme-standards:end notices -->
