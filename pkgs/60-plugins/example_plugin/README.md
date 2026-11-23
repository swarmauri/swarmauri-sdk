# swm_example_plugin

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swm_example_plugin</strong></p>
<p align="center">This repository includes an example of a Swarmauri Plugin.</p>
<p align="center">
<a href="https://pypi.org/project/swm_example_plugin/"><img alt="pypi: swm_example_plugin" src="https://img.shields.io/pypi/v/swm_example_plugin?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/example_plugin/pyproject.toml"><img alt="Source version: 0.11.0.dev4" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev4&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/example_plugin/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/example_plugin/pyproject.toml"><img alt="Layer: plugins" src="https://img.shields.io/static/v1?label=Layer&amp;message=plugins&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/example_plugin/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/example_plugin/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/example_plugin/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swm_example_plugin/"><img alt="Monthly PyPI downloads: swm_example_plugin" src="https://img.shields.io/pypi/dm/swm_example_plugin?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/example_plugin/README.md"><img alt="README hits: swm_example_plugin" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/60-plugins/example_plugin/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/example_plugin/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/example_plugin/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

The Swarmauri Example Plugin is a lightweight reference package that shows how to
ship a plugin ready for the Swarmauri ecosystem. It demonstrates how to declare
entry points, surface metadata, and structure tests so that new plugin projects
start from a fully configured baseline that supports Python 3.10 through 3.12.

### Why This Package

`swm_example_plugin` isolates this responsibility: This repository includes an example of a Swarmauri Plugin. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/example_plugin/swm_example_plugin/__init__.py) exposes `Path`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swm_example_plugin` when your integration needs this repository includes an example of a Swarmauri Plugin. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- **Entry-point wiring** - exposes the `swarmauri.plugins` group so your agent
  classes can be discovered automatically once implemented.
- **Ready-to-publish metadata** - includes keywords, classifiers, and long
  descriptions wired directly into `pyproject.toml`.
- **Version helpers** - surfaces `__version__` and `__long_desc__` constants so
  documentation and tooling can introspect the package after installation.
- **Testing scaffold** - ships with baseline unit tests verifying version
  resolution to encourage a test-first development workflow.

### Non-Goals

`swm_example_plugin` owns this repository includes an example of a Swarmauri Plugin. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/example_plugin/pyproject.toml) declares no direct runtime dependencies. Read the example’s inputs and service requirements before execution.

### Installation

**Using uv**

```bash
uv add swm-example-plugin
```

**Using pip**

```bash
pip install swm-example-plugin
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swm_example_plugin
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swm_example_plugin
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swm_example_plugin
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/example_plugin/docs/readme/quick_start.py).

```python
from swm_example_plugin import __long_desc__, __version__

print(__version__)
print(__long_desc__.splitlines()[0])
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swm_example_plugin` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/example_plugin/docs/readme/usage.py).

```python
from swm_example_plugin import __long_desc__, __version__

print(__version__)
print(__long_desc__.splitlines()[0])
```
<!-- readme-standards:end example.usage -->

**Inspect published metadata**


**Discover the registered entry point**

```python
from importlib.metadata import entry_points

for ep in entry_points(group="swarmauri.plugins"):
    if ep.name == "example_agent":
        print(ep.name, "->", ep.value)
        break
```

This skeleton intentionally leaves the actual agent implementation up to you.
Replace the target specified in the entry point with your concrete class to wire
custom functionality into the Swarmauri plugin registry.

### Configuration

Configure `swm_example_plugin` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/example_plugin/swm_example_plugin/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/example_plugin/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swm_example_plugin` source does not establish a package-wide exception hierarchy. Preserve errors from its declared dependencies and validate inputs using the specific public contract in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/example_plugin/swm_example_plugin/__init__.py).

### Best Practices

Use the explicit `swm_example_plugin` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `Path`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swm_example_plugin` is located in `plugins` and owns this repository includes an example of a Swarmauri Plugin. Source-declared APIs include `Path`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/example_plugin/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swm_example_plugin`.

Source-declared exports or types: `Path`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/example_plugin/swm_example_plugin/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.plugins` → `example_agent` → `swm_example_plugin.agents:ExampleAgent`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swm_example_plugin` are empty in the manifest. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/example_plugin/swm_example_plugin/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swm_example_plugin` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swm_example_plugin`, use the source-declared public interfaces (`Path`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swm_example_plugin` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/example_plugin/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swm_example_plugin`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/example_plugin/swm_example_plugin/__init__.py). The `swm_example_plugin` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swm_example_plugin` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swm_example_plugin` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/unit/test_version.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/example_plugin/tests/unit/test_version.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swm_example_plugin` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/example_plugin/swm_example_plugin/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swm_example_plugin` provides this repository includes an example of a Swarmauri Plugin; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swm_example_plugin`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/example_plugin/swm_example_plugin/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swm_example_plugin` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/example_plugin/swm_example_plugin/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/example_plugin/pyproject.toml) provide the supporting context for `swm_example_plugin`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

No direct local dependency was identified for `swm_example_plugin` in this checkout. External dependency names are listed under Prerequisites; packages in the same directory layer are not automatically dependencies.

### Project Links

<!-- readme-standards:begin project-links -->
- [Changelog](https://github.com/swarmauri/swarmauri-sdk/releases)
- [Discussions](https://github.com/orgs/swarmauri/discussions)
- [Documentation](https://github.com/swarmauri/swarmauri-sdk/tree/main/pkgs/60-plugins/example_plugin#readme)
- [Homepage](https://github.com/swarmauri/swarmauri-sdk)
- [Issues](https://github.com/swarmauri/swarmauri-sdk/issues)
- [Source](https://github.com/swarmauri/swarmauri-sdk/tree/main/pkgs/60-plugins/example_plugin)
- [pypi: swm_example_plugin](https://pypi.org/project/swm_example_plugin/)
<!-- readme-standards:end project-links -->

- Source: <https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/60-plugins/example_plugin>
- Documentation: <https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/60-plugins/example_plugin#readme>
- Issues: <https://github.com/swarmauri/swarmauri-sdk/issues>
- Releases: <https://github.com/swarmauri/swarmauri-sdk/releases>
- Discussions: <https://github.com/orgs/swarmauri/discussions>

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swm_example_plugin`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/60-plugins/example_plugin` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swm_example_plugin` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swm_example_plugin` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/example_plugin/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swm_example_plugin` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swm_example_plugin` source version is `0.11.0.dev4`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/example_plugin/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/example_plugin/NOTICE) for attribution.
<!-- readme-standards:end notices -->
