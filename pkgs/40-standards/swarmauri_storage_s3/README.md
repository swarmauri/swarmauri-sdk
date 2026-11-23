# swarmauri_storage_s3

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_storage_s3</strong></p>
<p align="center">Generic S3-compatible storage adapter for SwarmauriSDK</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_storage_s3/"><img alt="pypi: swarmauri_storage_s3" src="https://img.shields.io/pypi/v/swarmauri_storage_s3"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_storage_s3/pyproject.toml"><img alt="Source version: 0.11.0.dev6" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev6&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_storage_s3/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_storage_s3/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_storage_s3/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_storage_s3/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_storage_s3/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_storage_s3/"><img alt="Monthly PyPI downloads: swarmauri_storage_s3" src="https://img.shields.io/pypi/dm/swarmauri_storage_s3"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_storage_s3/README.md"><img alt="README hits: swarmauri_storage_s3" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/40-standards/swarmauri_storage_s3/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_storage_s3/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_storage_s3/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

Generic S3-compatible storage adapter for SwarmauriSDK.

### Why This Package

`swarmauri_storage_s3` isolates this responsibility: Generic S3-compatible storage adapter for SwarmauriSDK. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_storage_s3/swarmauri_storage_s3/s3_storage_adapter.py) exposes `PackageNotFoundError`, `S3StorageAdapter`, `version`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_storage_s3` when your integration needs generic S3-compatible storage adapter for SwarmauriSDK. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Stores and retrieves objects through direct S3 client operations.
- Supports AWS S3 and S3-conformant endpoints such as MinIO, Cloudflare R2, Wasabi, Ceph, DigitalOcean Spaces, Garage, and BucketWarden when they expose the required S3 API.
- Accepts endpoint, region, credentials, TLS verification, path-style addressing, and client configuration options.
- Provides discoverable `swarmauri.storage_adapters` and `peagen.plugins.storage_adapters` entry points.

### Non-Goals

`swarmauri_storage_s3` owns generic S3-compatible storage adapter for SwarmauriSDK. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_storage_s3/pyproject.toml) declares runtime dependencies including `boto3`, `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. Read the example’s inputs and service requirements before execution.

### Installation

Install this package with `uv` or `pip`.

```bash
uv add swarmauri_storage_s3
```

```bash
pip install swarmauri_storage_s3
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_storage_s3
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_storage_s3
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_storage_s3
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_storage_s3/docs/readme/quick_start.py).

```python
from swarmauri_storage_s3 import S3StorageAdapter

adapter = S3StorageAdapter.from_uri("s3://model-artifacts/runs")
uri = adapter.put_blob("latest/result.json", b'{"status":"ok"}')
payload = adapter.get_blob("latest/result.json")

print(uri)
print(payload)
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_storage_s3` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_storage_s3/docs/readme/usage.py).

```python
from swarmauri_storage_s3 import S3StorageAdapter

adapter = S3StorageAdapter.from_uri("s3://model-artifacts/runs")
uri = adapter.put_blob("latest/result.json", b'{"status":"ok"}')
payload = adapter.get_blob("latest/result.json")

print(uri)
print(payload)
```
<!-- readme-standards:end example.usage -->

Use this adapter when the workflow should talk to an S3-compatible object API directly.


Configure provider credentials and endpoint settings in the constructor or through environment variables owned by the surrounding Swarmauri or Tigrbl workflow.

License: Apache-2.0. See `LICENSE`.

### Configuration

The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_storage_s3/swarmauri_storage_s3/s3_storage_adapter.py) references configuration keys `AWS_ACCESS_KEY_ID`, `AWS_ENDPOINT_URL`, `AWS_REGION`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`. Consult the constructor or function signature before supplying them; a referenced key is not necessarily a global environment variable.

### Error Handling

The inspected `swarmauri_storage_s3` source raises `FileNotFoundError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_storage_s3` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `PackageNotFoundError`, `S3StorageAdapter`, `version`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_storage_s3` is located in `standards` and owns generic S3-compatible storage adapter for SwarmauriSDK. Source-declared APIs include `PackageNotFoundError`, `S3StorageAdapter`, `version`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_storage_s3/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_storage_s3`.

Source-declared exports or types: `PackageNotFoundError`, `S3StorageAdapter`, `version`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_storage_s3/swarmauri_storage_s3/s3_storage_adapter.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `peagen.plugins.storage_adapters` → `s3` → `swarmauri_storage_s3.s3_storage_adapter:S3StorageAdapter`
- `swarmauri.storage_adapters` → `S3StorageAdapter` → `swarmauri_storage_s3.s3_storage_adapter:S3StorageAdapter`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_storage_s3` are `boto3`, `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_storage_s3/swarmauri_storage_s3/s3_storage_adapter.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_storage_s3` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_storage_s3`, use the source-declared public interfaces (`PackageNotFoundError`, `S3StorageAdapter`, `version`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_storage_s3` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_storage_s3/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_storage_s3`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_storage_s3/swarmauri_storage_s3/s3_storage_adapter.py). The `swarmauri_storage_s3` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_storage_s3` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_storage_s3` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/i9n/test_i9n__init__.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_storage_s3/tests/i9n/test_i9n__init__.py)
- [tests/unit/test_s3_storage_adapter.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_storage_s3/tests/unit/test_s3_storage_adapter.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_storage_s3` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_storage_s3/swarmauri_storage_s3/s3_storage_adapter.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_storage_s3` provides generic S3-compatible storage adapter for SwarmauriSDK; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_storage_s3`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_storage_s3/swarmauri_storage_s3/s3_storage_adapter.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_storage_s3` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_storage_s3/swarmauri_storage_s3/s3_storage_adapter.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_storage_s3/pyproject.toml) provide the supporting context for `swarmauri_storage_s3`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.
- [swarmauri_standard](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/30-standard-kernel/swarmauri_standard/README.md): First-party Swarmauri standard components for agents, tools, parsers, vectors, model adapters, and composable intelligence workflows.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_storage_s3](https://pypi.org/project/swarmauri_storage_s3/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_storage_s3`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/40-standards/swarmauri_storage_s3` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_storage_s3` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_storage_s3` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_storage_s3/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_storage_s3` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_storage_s3` source version is `0.11.0.dev6`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_storage_s3/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_storage_s3/NOTICE) for attribution.
<!-- readme-standards:end notices -->
