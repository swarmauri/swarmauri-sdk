# swarmauri_tests_pylicense

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_tests_pylicense</strong></p>
<p align="center">Pytest plugin reporting dependency licenses</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_tests_pylicense/"><img alt="pypi: swarmauri_tests_pylicense" src="https://img.shields.io/pypi/v/swarmauri_tests_pylicense"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_tests_pylicense/pyproject.toml"><img alt="Source version: 0.11.0.dev3" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev3&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_tests_pylicense/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_tests_pylicense/pyproject.toml"><img alt="Layer: experimental" src="https://img.shields.io/static/v1?label=Layer&amp;message=experimental&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_tests_pylicense/README.md#lifecycle-and-migration"><img alt="Lifecycle: experimental" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=experimental&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_tests_pylicense/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_tests_pylicense/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_tests_pylicense/"><img alt="Monthly PyPI downloads: swarmauri_tests_pylicense" src="https://img.shields.io/pypi/dm/swarmauri_tests_pylicense"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_tests_pylicense/README.md"><img alt="README hits: swarmauri_tests_pylicense" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/experimental/swarmauri_tests_pylicense/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_tests_pylicense/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_tests_pylicense/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_tests_pylicense` is a [pytest](https://docs.pytest.org/) plugin that
scans a package's full dependency tree and ensures each dependency declares a
license. The plugin resolves dependencies recursively, checking every
transitive requirement. It inspects both the `License` metadata field and
any `Classifier` entries that declare a license.

By default, the plugin runs in *parameterized* mode which creates one test per
dependency. An *aggregate* mode is also available that reports all missing
licenses in a single test.

### Why This Package

`swarmauri_tests_pylicense` isolates this responsibility: Pytest plugin reporting dependency licenses. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_tests_pylicense/swarmauri_tests_pylicense/__init__.py) exposes `DependencyPath`, `PackageLicense`, `_collect_dependency_paths`, `_collect_licenses`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_tests_pylicense` when your integration needs pytest plugin reporting dependency licenses. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- `PackageLicense`: declared in swarmauri_tests_pylicense/__init__.py
- `DependencyPath`: declared in swarmauri_tests_pylicense/__init__.py
- `LicenseItem`: declared in swarmauri_tests_pylicense/__init__.py
- `LicenseAggregateItem`: declared in swarmauri_tests_pylicense/__init__.py

### Non-Goals

`swarmauri_tests_pylicense` owns pytest plugin reporting dependency licenses. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_tests_pylicense/pyproject.toml) declares no direct runtime dependencies. Read the example’s inputs and service requirements before execution.

### Installation

```bash
pip install swarmauri_tests_pylicense
```

`pytest` automatically discovers the plugin once it is installed.

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_tests_pylicense
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_tests_pylicense
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_tests_pylicense
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.sh](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_tests_pylicense/docs/readme/quick_start.sh).

```bash
pytest --pylicense-package=<your-package>
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_tests_pylicense` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.sh](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_tests_pylicense/docs/readme/usage.sh).

```bash
pytest --pylicense-package=<your-package>
```
<!-- readme-standards:end example.usage -->

**Parameterized (default)**

Run `pytest` with the package name to scan its dependency licenses:


Each generated test encodes the full dependency path, the resolved version,
and the detected license of the terminal package. For example:

```
swarmauri_tests_pylicense:license::pkg::depA::depB==1.2.3 [Apache-2.0]
```

**Aggregate**

Use the `--pylicense-mode=aggregate` flag to consolidate checks into one test:

```bash
pytest --pylicense-package=<your-package> --pylicense-mode=aggregate
```

**Allow and Disallow Lists**

To restrict acceptable licenses, provide a comma-separated allow list or
disallow list. These can be passed via command-line options or environment
variables.

Command-line:

```bash
pytest --pylicense-package=<your-package> --pylicense-allow-list=MIT,Apache-2.0
pytest --pylicense-package=<your-package> --pylicense-disallow-list=GPL
```

Environment variables:

```bash
export PYLICENSE_ALLOW_LIST="MIT,Apache-2.0"
export PYLICENSE_DISALLOW_LIST="GPL"
pytest --pylicense-package=<your-package>
```

If both are provided, any license not in the allow list or explicitly present
in the disallow list will cause a test failure. By default, all licenses are
allowed and none are disallowed.

**Accepting Specific Dependencies**

Some transitive dependencies may ship with unusual or proprietary licenses that
are acceptable for your project. Use `--pylicense-accept-deps` (or the
`PYLICENSE_ACCEPT_DEPS` environment variable) with a comma-separated list to
explicitly bypass those packages. For example:

```bash
pytest --pylicense-package=<your-package> --pylicense-accept-deps=cffi
```

This tells the plugin to treat `cffi` as pre-approved. Any license issues for
`cffi`?including unknown or non-standard licenses?are ignored while other
dependencies continue to be validated normally.

### Configuration

Configure `swarmauri_tests_pylicense` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_tests_pylicense/swarmauri_tests_pylicense/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_tests_pylicense/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_tests_pylicense` source raises `pytest.UsageError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_tests_pylicense` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `DependencyPath`, `PackageLicense`, `_collect_dependency_paths`, `_collect_licenses`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_tests_pylicense` is located in `experimental` and owns pytest plugin reporting dependency licenses. Source-declared APIs include `DependencyPath`, `PackageLicense`, `_collect_dependency_paths`, `_collect_licenses`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_tests_pylicense/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_tests_pylicense`.

Source-declared exports or types: `DependencyPath`, `PackageLicense`, `_collect_dependency_paths`, `_collect_licenses`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_tests_pylicense/swarmauri_tests_pylicense/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `pytest11` → `swarmauri_tests_pylicense` → `swarmauri_tests_pylicense`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_tests_pylicense` are empty in the manifest. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_tests_pylicense/swarmauri_tests_pylicense/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_tests_pylicense` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_tests_pylicense`, use the source-declared public interfaces (`DependencyPath`, `PackageLicense`, `_collect_dependency_paths`, `_collect_licenses`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_tests_pylicense` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_tests_pylicense/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_tests_pylicense`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_tests_pylicense/swarmauri_tests_pylicense/__init__.py). The `swarmauri_tests_pylicense` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_tests_pylicense` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_tests_pylicense` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_plugin.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_tests_pylicense/tests/test_plugin.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_tests_pylicense` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_tests_pylicense/swarmauri_tests_pylicense/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_tests_pylicense` provides pytest plugin reporting dependency licenses; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_tests_pylicense`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_tests_pylicense/swarmauri_tests_pylicense/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_tests_pylicense` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_tests_pylicense/swarmauri_tests_pylicense/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_tests_pylicense/pyproject.toml) provide the supporting context for `swarmauri_tests_pylicense`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

No direct local dependency was identified for `swarmauri_tests_pylicense` in this checkout. External dependency names are listed under Prerequisites; packages in the same directory layer are not automatically dependencies.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_tests_pylicense](https://pypi.org/project/swarmauri_tests_pylicense/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_tests_pylicense`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/experimental/swarmauri_tests_pylicense` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_tests_pylicense` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_tests_pylicense` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_tests_pylicense/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_tests_pylicense` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_tests_pylicense` source version is `0.11.0.dev3`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_tests_pylicense/LICENSE).
<!-- readme-standards:end license -->

Licensed under the [Apache 2.0 License](LICENSE).

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/experimental/swarmauri_tests_pylicense/NOTICE) for attribution.
<!-- readme-standards:end notices -->
