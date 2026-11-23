# swarmauri_transport_aws_eventstream

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_transport_aws_eventstream</strong></p>
<p align="center">Amazon Bedrock bidirectional EventStream transport for Swarmauri live models.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_transport_aws_eventstream/"><img alt="pypi: swarmauri_transport_aws_eventstream" src="https://img.shields.io/pypi/v/swarmauri_transport_aws_eventstream"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_aws_eventstream/pyproject.toml"><img alt="Source version: 0.1.0.dev2" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.1.0.dev2&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_aws_eventstream/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_aws_eventstream/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_aws_eventstream/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_aws_eventstream/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_aws_eventstream/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_transport_aws_eventstream/"><img alt="Monthly PyPI downloads: swarmauri_transport_aws_eventstream" src="https://img.shields.io/pypi/dm/swarmauri_transport_aws_eventstream"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_aws_eventstream/README.md"><img alt="README hits: swarmauri_transport_aws_eventstream" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/40-standards/swarmauri_transport_aws_eventstream/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_aws_eventstream/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_aws_eventstream/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

[![Downloads](https://img.shields.io/pypi/dm/swarmauri_transport_aws_eventstream)](https://pypi.org/project/swarmauri_transport_aws_eventstream/)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/40-standards/swarmauri_transport_aws_eventstream.svg)](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/40-standards/swarmauri_transport_aws_eventstream)
[![Python](https://img.shields.io/pypi/pyversions/swarmauri_transport_aws_eventstream)](https://pypi.org/project/swarmauri_transport_aws_eventstream/)
[![License](https://img.shields.io/pypi/l/swarmauri_transport_aws_eventstream)](LICENSE)
[![Version](https://img.shields.io/pypi/v/swarmauri_transport_aws_eventstream?label=swarmauri_transport_aws_eventstream&color=green)](https://pypi.org/project/swarmauri_transport_aws_eventstream/)

`swarmauri_transport_aws_eventstream` adapts Amazon Bedrock's Smithy
bidirectional EventStream operation to Swarmauri's
`IBidirectionalStreamClient` and `IBidirectionalStreamConnection` contracts.
The AWS SDK owns HTTP/2 framing, credential-chain resolution, and SigV4 request
and message signing; this package owns the Swarmauri lifecycle and JSON event
mapping.

### Why This Package

`swarmauri_transport_aws_eventstream` isolates this responsibility: Amazon Bedrock bidirectional EventStream transport for Swarmauri live models. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_aws_eventstream/swarmauri_transport_aws_eventstream/__init__.py) exposes `AwsEventStreamClient`, `AwsEventStreamCodec`, `AwsEventStreamConnection`, `AwsEventStreamError`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_transport_aws_eventstream` when your integration needs amazon Bedrock bidirectional EventStream transport for Swarmauri live models. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Sends and receives JSON events over `InvokeModelWithBidirectionalStream`.
- Supports explicit temporary credentials, the default AWS credential chain,
  and named profiles.
- Exposes synchronous and asynchronous Swarmauri connection APIs.
- Converts AWS stream exception events into `AwsEventStreamError`.
- Keeps credentials out of serialized component state.

The codec and package metadata support Python 3.10 through 3.14. Amazon's
official `aws-sdk-bedrock-runtime` currently requires Python 3.12, so opening a
live Bedrock connection requires Python 3.12.

### Non-Goals

`swarmauri_transport_aws_eventstream` owns amazon Bedrock bidirectional EventStream transport for Swarmauri live models. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_aws_eventstream/pyproject.toml) declares runtime dependencies including `botocore`, `swarmauri-base`, `swarmauri-core`, `aws-sdk-bedrock-runtime`. Read the example’s inputs and service requirements before execution.

### Installation

```bash
uv add swarmauri_transport_aws_eventstream
```

```bash
pip install swarmauri_transport_aws_eventstream
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_transport_aws_eventstream
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_transport_aws_eventstream
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_transport_aws_eventstream
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_aws_eventstream/docs/readme/quick_start.py).

```python
import importlib

package = importlib.import_module("swarmauri_transport_aws_eventstream")
assert package.__name__ == "swarmauri_transport_aws_eventstream"
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

This quick start is explicitly an import smoke check for `swarmauri_transport_aws_eventstream`. It confirms that the documented namespace loads; it does not demonstrate or certify a complete application workflow. The detailed source and retained usage guidance below describe the integration boundary.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_aws_eventstream/docs/readme/usage.py).

```python
import importlib

package = importlib.import_module("swarmauri_transport_aws_eventstream")
assert package.__name__ == "swarmauri_transport_aws_eventstream"
```
<!-- readme-standards:end example.usage -->

Use the client directly when you already have a Bedrock model ID:

```python
from swarmauri_transport_aws_eventstream import AwsEventStreamClient

client = AwsEventStreamClient(region="us-east-1")
connection = await client.aconnect(
    "https://bedrock-runtime.us-east-1.amazonaws.com",
    model_id="amazon.nova-sonic-v1:0",
)

await connection.asend({"event": {"sessionStart": {}}})
async for event in connection.aiter_events():
    print(event)
await connection.aclose()
```

`NovaSonicLiveModel` configures this transport automatically. Pass an
`AmazonNovaProvider` when you need a named profile, explicit temporary
credentials, a different region, or a custom Bedrock runtime endpoint.

### Configuration

Configure `swarmauri_transport_aws_eventstream` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_aws_eventstream/swarmauri_transport_aws_eventstream/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_aws_eventstream/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_transport_aws_eventstream` source raises `AwsEventStreamError`, `EOFError`, `RuntimeError`, `TypeError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_transport_aws_eventstream` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `AwsEventStreamClient`, `AwsEventStreamCodec`, `AwsEventStreamConnection`, `AwsEventStreamError`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_transport_aws_eventstream` is located in `standards` and owns amazon Bedrock bidirectional EventStream transport for Swarmauri live models. Source-declared APIs include `AwsEventStreamClient`, `AwsEventStreamCodec`, `AwsEventStreamConnection`, `AwsEventStreamError`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_aws_eventstream/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_transport_aws_eventstream`.

Source-declared exports or types: `AwsEventStreamClient`, `AwsEventStreamCodec`, `AwsEventStreamConnection`, `AwsEventStreamError`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_aws_eventstream/swarmauri_transport_aws_eventstream/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.transports` → `AwsEventStreamClient` → `swarmauri_transport_aws_eventstream:AwsEventStreamClient`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_transport_aws_eventstream` are `botocore`, `swarmauri-base`, `swarmauri-core`, `aws-sdk-bedrock-runtime`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_aws_eventstream/swarmauri_transport_aws_eventstream/__init__.py).

### Protocol Consumers

Direct consumers in this checkout’s package manifests include `swarmauri_live_model_amazon_nova`. These edges describe declared dependencies, not protocol-conformance evidence.

### Extensions

For `swarmauri_transport_aws_eventstream`, use the source-declared public interfaces (`AwsEventStreamClient`, `AwsEventStreamCodec`, `AwsEventStreamConnection`, `AwsEventStreamError`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_transport_aws_eventstream` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_aws_eventstream/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_transport_aws_eventstream`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_aws_eventstream/swarmauri_transport_aws_eventstream/__init__.py). The `swarmauri_transport_aws_eventstream` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_transport_aws_eventstream` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_transport_aws_eventstream` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/unit/test_async_connect.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_aws_eventstream/tests/unit/test_async_connect.py)
- [tests/unit/test_aws_eventstream.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_aws_eventstream/tests/unit/test_aws_eventstream.py)
- [tests/unit/test_import.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_aws_eventstream/tests/unit/test_import.py)
- [tests/unit/test_package_contract.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_aws_eventstream/tests/unit/test_package_contract.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_transport_aws_eventstream` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_aws_eventstream/swarmauri_transport_aws_eventstream/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_transport_aws_eventstream` provides amazon Bedrock bidirectional EventStream transport for Swarmauri live models; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_transport_aws_eventstream`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_aws_eventstream/swarmauri_transport_aws_eventstream/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_transport_aws_eventstream` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_aws_eventstream/swarmauri_transport_aws_eventstream/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_aws_eventstream/pyproject.toml) provide the supporting context for `swarmauri_transport_aws_eventstream`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.

### Project Links

<!-- readme-standards:begin project-links -->
- [Documentation](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/40-standards/swarmauri_transport_aws_eventstream#readme)
- [Homepage](https://github.com/swarmauri/swarmauri-sdk)
- [Repository](https://github.com/swarmauri/swarmauri-sdk)
- [Source](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/40-standards/swarmauri_transport_aws_eventstream)
- [pypi: swarmauri_transport_aws_eventstream](https://pypi.org/project/swarmauri_transport_aws_eventstream/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_transport_aws_eventstream`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/40-standards/swarmauri_transport_aws_eventstream` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_transport_aws_eventstream` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_transport_aws_eventstream` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_aws_eventstream/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_transport_aws_eventstream` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_transport_aws_eventstream` source version is `0.1.0.dev2`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_aws_eventstream/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_aws_eventstream/NOTICE) for attribution.
<!-- readme-standards:end notices -->
