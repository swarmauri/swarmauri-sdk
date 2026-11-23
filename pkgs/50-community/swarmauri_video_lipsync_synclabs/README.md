# swarmauri_video_lipsync_synclabs

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_video_lipsync_synclabs</strong></p>
<p align="center">Standalone Sync Labs queued lip-sync video provider for Swarmauri.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_video_lipsync_synclabs/"><img alt="pypi: swarmauri_video_lipsync_synclabs" src="https://img.shields.io/pypi/v/swarmauri_video_lipsync_synclabs"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_video_lipsync_synclabs/pyproject.toml"><img alt="Source version: 0.1.0.dev5" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.1.0.dev5&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_video_lipsync_synclabs/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_video_lipsync_synclabs/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_video_lipsync_synclabs/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_video_lipsync_synclabs/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_video_lipsync_synclabs/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_video_lipsync_synclabs/"><img alt="Monthly PyPI downloads: swarmauri_video_lipsync_synclabs" src="https://img.shields.io/pypi/dm/swarmauri_video_lipsync_synclabs"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_video_lipsync_synclabs/README.md"><img alt="README hits: swarmauri_video_lipsync_synclabs" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/50-community/swarmauri_video_lipsync_synclabs/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_video_lipsync_synclabs/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_video_lipsync_synclabs/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_video_lipsync_synclabs` is the standalone Sync Labs provider for
Swarmauri lip-sync video generation. `SyncLabsLipSync` implements the common
`LipSyncBase` contract and exposes Sync Labs' queued job lifecycle without
misrepresenting progress events as streamed video.

[![PyPI Downloads](https://static.pepy.tech/badge/swarmauri_video_lipsync_synclabs)](https://pepy.tech/projects/swarmauri_video_lipsync_synclabs)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/50-community/swarmauri_video_lipsync_synclabs.svg)](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/50-community/swarmauri_video_lipsync_synclabs/)
[![Python Versions](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue)](https://pypi.org/project/swarmauri_video_lipsync_synclabs/)
[![License](https://img.shields.io/pypi/l/swarmauri_video_lipsync_synclabs)](https://pypi.org/project/swarmauri_video_lipsync_synclabs/)
[![PyPI Version](https://img.shields.io/pypi/v/swarmauri_video_lipsync_synclabs)](https://pypi.org/project/swarmauri_video_lipsync_synclabs/)

### Why This Package

`swarmauri_video_lipsync_synclabs` isolates this responsibility: Standalone Sync Labs queued lip-sync video provider for Swarmauri. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_video_lipsync_synclabs/swarmauri_video_lipsync_synclabs/__init__.py) exposes `SyncLabsLipSync`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_video_lipsync_synclabs` when your integration needs standalone Sync Labs queued lip-sync video provider for Swarmauri. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Common synchronous and asynchronous `predict` workflows.
- Observable queued jobs through `submit`, `get_status`, `iter_events`, and
  `aiter_events`.
- Normalized queued, running, completed, failed, and rejected job events.
- Public URL inputs and local video/audio uploads through Sync Labs assets.
- Preflight cost estimation through Sync Labs' estimate endpoint.
- Retry handling for rate limits and safe transient requests.
- API credentials excluded from serialized component state and external media
  requests.
- Current Sync Labs models: `sync-3`, `lipsync-2`, `lipsync-2-pro`,
  `lipsync-1.9.0-beta`, and `react-1`.

### Non-Goals

`swarmauri_video_lipsync_synclabs` owns standalone Sync Labs queued lip-sync video provider for Swarmauri. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_video_lipsync_synclabs/pyproject.toml) declares runtime dependencies including `httpx`, `pydantic`, `swarmauri-base`, `swarmauri-core`. Read the example’s inputs and service requirements before execution.

### Installation

```bash
uv add swarmauri_video_lipsync_synclabs
```

```bash
pip install swarmauri_video_lipsync_synclabs
```

Set `SYNC_API_KEY` before submitting billable work.

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_video_lipsync_synclabs
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_video_lipsync_synclabs
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_video_lipsync_synclabs
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_video_lipsync_synclabs/docs/readme/quick_start.py).

```python
import os

from swarmauri_video_lipsync_synclabs import SyncLabsLipSync

lip_sync = SyncLabsLipSync(api_key=os.environ["SYNC_API_KEY"])
result = lip_sync.predict(
    "https://example.com/speaker.mp4",
    "https://example.com/dialogue.wav",
    "dubbed.mp4",
    sync_mode="cut_off",
)
print(result)
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_video_lipsync_synclabs` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_video_lipsync_synclabs/docs/readme/usage.py).

```python
import os

from swarmauri_video_lipsync_synclabs import SyncLabsLipSync

lip_sync = SyncLabsLipSync(api_key=os.environ["SYNC_API_KEY"])
result = lip_sync.predict(
    "https://example.com/speaker.mp4",
    "https://example.com/dialogue.wav",
    "dubbed.mp4",
    sync_mode="cut_off",
)
print(result)
```
<!-- readme-standards:end example.usage -->

Generate from public media URLs:


Local paths are uploaded as reusable Sync Labs assets before generation:

```python
result = lip_sync.predict("speaker.mp4", "dialogue.wav", "dubbed.mp4")
```

Observe a queued job without blocking for the final artifact:

```python
job_id = lip_sync.submit(
    "https://example.com/speaker.mp4",
    "https://example.com/dialogue.wav",
)
for event in lip_sync.iter_events(job_id):
    print(event)
```

These iterators report job progress. Sync Labs returns a completed video
artifact rather than incremental video bytes, so this provider intentionally
does not expose `stream` or `astream`.

### Configuration

Configure `swarmauri_video_lipsync_synclabs` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_video_lipsync_synclabs/swarmauri_video_lipsync_synclabs/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_video_lipsync_synclabs/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_video_lipsync_synclabs` source raises `RuntimeError`, `TimeoutError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_video_lipsync_synclabs` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `SyncLabsLipSync`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_video_lipsync_synclabs` is located in `community` and owns standalone Sync Labs queued lip-sync video provider for Swarmauri. Source-declared APIs include `SyncLabsLipSync`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_video_lipsync_synclabs/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_video_lipsync_synclabs`.

Source-declared exports or types: `SyncLabsLipSync`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_video_lipsync_synclabs/swarmauri_video_lipsync_synclabs/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.video_lipsync` → `SyncLabsLipSync` → `swarmauri_video_lipsync_synclabs:SyncLabsLipSync`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_video_lipsync_synclabs` are `httpx`, `pydantic`, `swarmauri-base`, `swarmauri-core`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_video_lipsync_synclabs/swarmauri_video_lipsync_synclabs/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_video_lipsync_synclabs` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_video_lipsync_synclabs`, use the source-declared public interfaces (`SyncLabsLipSync`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_video_lipsync_synclabs` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_video_lipsync_synclabs/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_video_lipsync_synclabs`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_video_lipsync_synclabs/swarmauri_video_lipsync_synclabs/__init__.py). The `swarmauri_video_lipsync_synclabs` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_video_lipsync_synclabs` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_video_lipsync_synclabs` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/unit/test_public_api.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_video_lipsync_synclabs/tests/unit/test_public_api.py)
- [tests/unit/test_synclabs_lipsync.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_video_lipsync_synclabs/tests/unit/test_synclabs_lipsync.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_video_lipsync_synclabs` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_video_lipsync_synclabs/swarmauri_video_lipsync_synclabs/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_video_lipsync_synclabs` provides standalone Sync Labs queued lip-sync video provider for Swarmauri; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_video_lipsync_synclabs`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_video_lipsync_synclabs/swarmauri_video_lipsync_synclabs/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_video_lipsync_synclabs` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_video_lipsync_synclabs/swarmauri_video_lipsync_synclabs/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_video_lipsync_synclabs/pyproject.toml) provide the supporting context for `swarmauri_video_lipsync_synclabs`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_video_lipsync_synclabs](https://pypi.org/project/swarmauri_video_lipsync_synclabs/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

This package is part of the
[Swarmauri SDK](https://github.com/swarmauri/swarmauri-sdk). Contributions
should follow the repository contribution and style guides.

### Development Setup

Work from the `pkgs/50-community/swarmauri_video_lipsync_synclabs` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_video_lipsync_synclabs` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_video_lipsync_synclabs` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_video_lipsync_synclabs/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_video_lipsync_synclabs` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_video_lipsync_synclabs` source version is `0.1.0.dev5`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_video_lipsync_synclabs/LICENSE).
<!-- readme-standards:end license -->

Apache-2.0

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_video_lipsync_synclabs/NOTICE) for attribution.
<!-- readme-standards:end notices -->
