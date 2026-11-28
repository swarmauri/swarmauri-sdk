# swarmauri_gitfilter_s3fs

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_gitfilter_s3fs</strong></p>
<p align="center">S3 git filter for Peagen using s3fs</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_gitfilter_s3fs/"><img alt="pypi: swarmauri_gitfilter_s3fs" src="https://img.shields.io/pypi/v/swarmauri_gitfilter_s3fs?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_gitfilter_s3fs/pyproject.toml"><img alt="Source version: 0.11.0" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_gitfilter_s3fs/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_gitfilter_s3fs/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_gitfilter_s3fs/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_gitfilter_s3fs/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_gitfilter_s3fs/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_gitfilter_s3fs/"><img alt="Monthly PyPI downloads: swarmauri_gitfilter_s3fs" src="https://img.shields.io/pypi/dm/swarmauri_gitfilter_s3fs?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_gitfilter_s3fs/README.md"><img alt="README hits: swarmauri_gitfilter_s3fs" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/40-standards/swarmauri_gitfilter_s3fs/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_gitfilter_s3fs/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_gitfilter_s3fs/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

Git filter implementation for Peagen that streams artifacts to Amazon S3 (or
S3-compatible services) through ``s3fs``.  The filter registers as a
``StorageAdapter`` named ``S3FSFilter`` and supports the full git clean/smudge
cycle by delegating reads and writes to the configured S3 bucket.

### Why This Package

`swarmauri_gitfilter_s3fs` isolates this responsibility: S3 git filter for Peagen using s3fs. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_gitfilter_s3fs/swarmauri_gitfilter_s3fs/__init__.py) exposes `S3FSFilter`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_gitfilter_s3fs` when your integration needs s3 git filter for Peagen using s3fs. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Implements :class:`~swarmauri_base.storage.StorageAdapterBase` and
  :class:`~swarmauri_base.git_filters.GitFilterBase` to provide streaming
  ``upload`` and ``download`` operations.
- Recursively uploads local directories via ``upload_dir`` and reconstructs
  prefixes back onto disk with ``download_prefix``.
- Lists existing objects under a prefix with ``iter_prefix`` to back git
  history reconstruction.
- Reads configuration from ``peagen.toml`` (``[storage.filters.s3fs]``) or the
  ``AWS_*`` environment variables when instantiated through
  :meth:`S3FSFilter.from_uri`.

### Non-Goals

`swarmauri_gitfilter_s3fs` owns s3 git filter for Peagen using s3fs. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_gitfilter_s3fs/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`, `s3fs`. Read the example’s inputs and service requirements before execution.

### Installation

Install the package with your preferred Python packaging tool:

```bash
pip install swarmauri_gitfilter_s3fs
```

```bash
poetry add swarmauri_gitfilter_s3fs
```

```bash
uv pip install swarmauri_gitfilter_s3fs
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_gitfilter_s3fs
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_gitfilter_s3fs
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_gitfilter_s3fs
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_gitfilter_s3fs/docs/readme/quick_start.py).

```python
from contextlib import nullcontext
from io import BytesIO
from unittest.mock import MagicMock, patch

from swarmauri_gitfilter_s3fs import S3FSFilter

with patch("swarmauri_gitfilter_s3fs.s3fs_filter.s3fs.S3FileSystem") as fs_cls:
    fake_fs = MagicMock()
    buffer = BytesIO()
    fake_fs.open.return_value = nullcontext(buffer)
    fs_cls.return_value = fake_fs

    filt = S3FSFilter.from_uri("s3://demo-bucket/models")
    location = filt.upload("artifacts/model.bin", BytesIO(b"model-weights"))

    assert location == "s3://demo-bucket/models/artifacts/model.bin"
    fake_fs.open.assert_called_with(
        "demo-bucket/models/artifacts/model.bin",
        "wb",
    )
    assert buffer.getvalue() == b"model-weights"
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_gitfilter_s3fs` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_gitfilter_s3fs/docs/readme/usage.py).

```python
from contextlib import nullcontext
from io import BytesIO
from unittest.mock import MagicMock, patch

from swarmauri_gitfilter_s3fs import S3FSFilter

with patch("swarmauri_gitfilter_s3fs.s3fs_filter.s3fs.S3FileSystem") as fs_cls:
    fake_fs = MagicMock()
    buffer = BytesIO()
    fake_fs.open.return_value = nullcontext(buffer)
    fs_cls.return_value = fake_fs

    filt = S3FSFilter.from_uri("s3://demo-bucket/models")
    location = filt.upload("artifacts/model.bin", BytesIO(b"model-weights"))

    assert location == "s3://demo-bucket/models/artifacts/model.bin"
    fake_fs.open.assert_called_with(
        "demo-bucket/models/artifacts/model.bin",
        "wb",
    )
    assert buffer.getvalue() == b"model-weights"
```
<!-- readme-standards:end example.usage -->

The example below patches ``s3fs`` with an in-memory stub so it can run without
network access.  The logic mirrors how ``S3FSFilter`` writes data to S3 and
returns the URI of the uploaded object.


In a production workflow you do not need to patch ``s3fs`` ? instantiate the
filter with your credentials and bucket, then use ``clean``/``smudge`` or
``upload``/``download`` to move artifacts between git and S3.

### Configuration

Create the filter by supplying your bucket name and optional connection
parameters:

- ``bucket`` ? Target bucket name (required).
- ``prefix`` ? Optional key prefix to scope uploads.
- ``key`` / ``secret`` ? Credentials for the S3 endpoint.  ``SecretStr``
  instances are supported.
- ``endpoint_url`` ? Custom S3-compatible endpoint (useful for MinIO or
  LocalStack).
- ``region_name`` ? Region for the endpoint.

When using :meth:`S3FSFilter.from_uri`, the URI sets the ``bucket`` and
``prefix`` while credentials are loaded from ``peagen.toml`` at
``[storage.filters.s3fs]`` (``key``, ``secret``, ``endpoint_url``, and
``region``).  Missing configuration falls back to
``AWS_ACCESS_KEY_ID``, ``AWS_SECRET_ACCESS_KEY``, ``AWS_ENDPOINT_URL``, and
``AWS_REGION`` respectively.

### Error Handling

The inspected `swarmauri_gitfilter_s3fs` source raises `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_gitfilter_s3fs` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `S3FSFilter`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_gitfilter_s3fs` is located in `standards` and owns s3 git filter for Peagen using s3fs. Source-declared APIs include `S3FSFilter`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_gitfilter_s3fs/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_gitfilter_s3fs`.

Source-declared exports or types: `S3FSFilter`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_gitfilter_s3fs/swarmauri_gitfilter_s3fs/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `peagen.plugins.git_filters` → `s3` → `swarmauri_gitfilter_s3fs.s3fs_filter:S3FSFilter`
- `swarmauri.git_filters` → `S3FSFilter` → `swarmauri_gitfilter_s3fs.s3fs_filter:S3FSFilter`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_gitfilter_s3fs` are `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`, `s3fs`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_gitfilter_s3fs/swarmauri_gitfilter_s3fs/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_gitfilter_s3fs` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_gitfilter_s3fs`, use the source-declared public interfaces (`S3FSFilter`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_gitfilter_s3fs` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_gitfilter_s3fs/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_gitfilter_s3fs`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_gitfilter_s3fs/swarmauri_gitfilter_s3fs/__init__.py). The `swarmauri_gitfilter_s3fs` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_gitfilter_s3fs` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_gitfilter_s3fs` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/example/test_readme_example.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_gitfilter_s3fs/tests/example/test_readme_example.py)
- [tests/i9n/test_i9n__init__.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_gitfilter_s3fs/tests/i9n/test_i9n__init__.py)
- [tests/unit/test_s3fs_filter.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_gitfilter_s3fs/tests/unit/test_s3fs_filter.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_gitfilter_s3fs` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_gitfilter_s3fs/swarmauri_gitfilter_s3fs/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_gitfilter_s3fs` provides s3 git filter for Peagen using s3fs; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_gitfilter_s3fs`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_gitfilter_s3fs/swarmauri_gitfilter_s3fs/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_gitfilter_s3fs` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_gitfilter_s3fs/swarmauri_gitfilter_s3fs/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_gitfilter_s3fs/pyproject.toml) provide the supporting context for `swarmauri_gitfilter_s3fs`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.
- [swarmauri_standard](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/30-standard-kernel/swarmauri_standard/README.md): First-party Swarmauri standard components for agents, tools, parsers, vectors, model adapters, and composable intelligence workflows.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_gitfilter_s3fs](https://pypi.org/project/swarmauri_gitfilter_s3fs/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.

### Development Setup

Work from the `pkgs/40-standards/swarmauri_gitfilter_s3fs` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_gitfilter_s3fs` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_gitfilter_s3fs` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_gitfilter_s3fs/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_gitfilter_s3fs` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_gitfilter_s3fs` source version is `0.11.0`.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_gitfilter_s3fs/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_gitfilter_s3fs/NOTICE) for attribution.
<!-- readme-standards:end notices -->
