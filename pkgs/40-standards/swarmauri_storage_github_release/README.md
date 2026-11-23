# swarmauri_storage_github_release

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_storage_github_release</strong></p>
<p align="center">GitHub Release storage adapter for Peagen</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_storage_github_release/"><img alt="pypi: swarmauri_storage_github_release" src="https://img.shields.io/pypi/v/swarmauri_storage_github_release"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_storage_github_release/pyproject.toml"><img alt="Source version: 0.11.0.dev3" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev3&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_storage_github_release/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_storage_github_release/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_storage_github_release/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_storage_github_release/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_storage_github_release/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_storage_github_release/"><img alt="Monthly PyPI downloads: swarmauri_storage_github_release" src="https://img.shields.io/pypi/dm/swarmauri_storage_github_release"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_storage_github_release/README.md"><img alt="README hits: swarmauri_storage_github_release" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/40-standards/swarmauri_storage_github_release/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_storage_github_release/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_storage_github_release/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

Stores and retrieves artifacts as assets on a GitHub release. The adapter is
designed to plug directly into the Swarmauri/Peagen storage interfaces while
still being usable as a standalone utility.

### Why This Package

`swarmauri_storage_github_release` isolates this responsibility: GitHub Release storage adapter for Peagen. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_storage_github_release/swarmauri_storage_github_release/gh_release_storage_adapter.py) exposes `GithubReleaseStorageAdapter`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_storage_github_release` when your integration needs gitHub Release storage adapter for Peagen. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- **Automatic release management** ? a release is created on-demand when the
  requested tag does not already exist.
- **`ghrel://` addressing** ? the adapter exposes a `root_uri` and returns
  fully-qualified URIs (e.g. `ghrel://org/repo/tag/path`) from `upload` calls.
- **Prefix-aware paths** ? supply an optional `prefix` to group related assets
  underneath a pseudo-directory on the release.
- **Bulk helpers** ? use `upload_dir` and `download_dir` to synchronise entire
  directories, or `iter_prefix` to discover stored assets.
- **Configuration friendly** ? `GithubReleaseStorageAdapter.from_uri` reads
  credentials from the `GITHUB_TOKEN` environment variable for simple
  environment-driven configuration in workflows.

### Non-Goals

`swarmauri_storage_github_release` owns gitHub Release storage adapter for Peagen. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

- A GitHub personal access token (PAT) or GitHub App token with sufficient
  permissions to view, create and manage releases on the target repository.
- Network access to the GitHub REST API (provided by `PyGithub`).
- Python 3.10 through 3.14.

### Installation

**Install uv (optional)**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Add the package with uv**

```bash
uv add swarmauri_storage_github_release
```

**Add with Poetry**

```bash
poetry add swarmauri_storage_github_release
```

**Install with pip**

```bash
pip install swarmauri_storage_github_release
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_storage_github_release
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_storage_github_release
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_storage_github_release
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_storage_github_release/docs/readme/quick_start.py).

```python
from io import BytesIO

from pydantic import SecretStr

from swarmauri_storage_github_release import GithubReleaseStorageAdapter

adapter = GithubReleaseStorageAdapter(
    token=SecretStr("ghp_example-token"),
    org="example-org",
    repo="example-repo",
    tag="v1.0.0",
    prefix="artifacts",
    release_name="Example release",
    message="Artifacts published by our workflow.",
)

print(adapter.root_uri)

uri = adapter.upload("artifact.txt", BytesIO(b"important payload"))
downloaded_payload = adapter.download("artifact.txt").read()
assets = list(adapter.iter_prefix(""))

print(uri)
print(downloaded_payload)
print(assets)
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_storage_github_release` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_storage_github_release/docs/readme/usage.py).

```python
from io import BytesIO

from pydantic import SecretStr

from swarmauri_storage_github_release import GithubReleaseStorageAdapter

adapter = GithubReleaseStorageAdapter(
    token=SecretStr("ghp_example-token"),
    org="example-org",
    repo="example-repo",
    tag="v1.0.0",
    prefix="artifacts",
    release_name="Example release",
    message="Artifacts published by our workflow.",
)

print(adapter.root_uri)

uri = adapter.upload("artifact.txt", BytesIO(b"important payload"))
downloaded_payload = adapter.download("artifact.txt").read()
assets = list(adapter.iter_prefix(""))

print(uri)
print(downloaded_payload)
print(assets)
```
<!-- readme-standards:end example.usage -->

The code above demonstrates:

- `SecretStr` support for securely passing tokens.
- Automatic release creation when the `v1.0.0` tag does not exist.
- Prefix-aware uploads that produce the URI
  `ghrel://example-org/example-repo/v1.0.0/artifacts/artifacts/artifact.txt`
  (the asset key itself contains the prefix, so it appears in the base URI and
  the returned asset key).
- Round-tripping an asset and enumerating stored keys via `iter_prefix`.

### Configuration

Configure `swarmauri_storage_github_release` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_storage_github_release/swarmauri_storage_github_release/gh_release_storage_adapter.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_storage_github_release/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_storage_github_release` source raises `FileNotFoundError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_storage_github_release` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `GithubReleaseStorageAdapter`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_storage_github_release` is located in `standards` and owns gitHub Release storage adapter for Peagen. Source-declared APIs include `GithubReleaseStorageAdapter`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_storage_github_release/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_storage_github_release`.

Source-declared exports or types: `GithubReleaseStorageAdapter`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_storage_github_release/swarmauri_storage_github_release/gh_release_storage_adapter.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `peagen.plugins.storage_adapters` → `gh_release` → `swarmauri_storage_github_release.gh_release_storage_adapter:GithubReleaseStorageAdapter`
- `swarmauri.storage_adapters` → `GithubReleaseStorageAdapter` → `swarmauri_storage_github_release.gh_release_storage_adapter:GithubReleaseStorageAdapter`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_storage_github_release` are `pygithub`, `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_storage_github_release/swarmauri_storage_github_release/gh_release_storage_adapter.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_storage_github_release` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_storage_github_release`, use the source-declared public interfaces (`GithubReleaseStorageAdapter`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_storage_github_release` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_storage_github_release/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_storage_github_release`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_storage_github_release/swarmauri_storage_github_release/gh_release_storage_adapter.py). The `swarmauri_storage_github_release` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_storage_github_release` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_storage_github_release` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/i9n/test_i9n__init__.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_storage_github_release/tests/i9n/test_i9n__init__.py)
- [tests/unit/test_github_release_storage_adapter.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_storage_github_release/tests/unit/test_github_release_storage_adapter.py)
- [tests/unit/test_readme_example.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_storage_github_release/tests/unit/test_readme_example.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_storage_github_release` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_storage_github_release/swarmauri_storage_github_release/gh_release_storage_adapter.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_storage_github_release` provides gitHub Release storage adapter for Peagen; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_storage_github_release`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_storage_github_release/swarmauri_storage_github_release/gh_release_storage_adapter.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_storage_github_release` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_storage_github_release/swarmauri_storage_github_release/gh_release_storage_adapter.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_storage_github_release/pyproject.toml) provide the supporting context for `swarmauri_storage_github_release`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.
- [swarmauri_standard](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/30-standard-kernel/swarmauri_standard/README.md): First-party Swarmauri standard components for agents, tools, parsers, vectors, model adapters, and composable intelligence workflows.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_storage_github_release](https://pypi.org/project/swarmauri_storage_github_release/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.

### Development Setup

Work from the `pkgs/40-standards/swarmauri_storage_github_release` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

**Working with directories**

Use the bulk helper methods to synchronise entire directory trees:

```python
adapter.upload_dir("dist", prefix="binaries")
adapter.download_dir("binaries", "./downloads")
```

Both helpers respect the adapter-level prefix and will mirror nested folders.

**Using ghrel:// URIs and configuration**

The `from_uri` class method creates adapters from an address such as:

```python
adapter = GithubReleaseStorageAdapter.from_uri(
    "ghrel://example-org/example-repo/v1.0.0/artifacts",
)
```

When invoked this way the adapter builds an unauthenticated client
(`token=""`).

Any prefix encoded in the URI is respected, and the resulting instance exposes
the same API shown above. For private repositories or higher rate limits,
instantiate the adapter directly and provide a token.

**Controlling release metadata**

The constructor accepts additional keyword arguments to fine tune release
creation, including `release_name`, `message`, `draft`, and `prerelease`. These
parameters map directly to GitHub's release settings, allowing you to reuse the
adapter for production, staging, or nightly build workflows.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_storage_github_release` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_storage_github_release/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_storage_github_release` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_storage_github_release` source version is `0.11.0.dev3`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_storage_github_release/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_storage_github_release/NOTICE) for attribution.
<!-- readme-standards:end notices -->
