# swarmauri_provider_openrouter

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_provider_openrouter</strong></p>
<p align="center">OpenRouter provider configuration, routing, catalogs, errors, and tool schemas for Swarmauri.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_provider_openrouter/"><img alt="pypi: swarmauri_provider_openrouter" src="https://img.shields.io/pypi/v/swarmauri_provider_openrouter"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_provider_openrouter/pyproject.toml"><img alt="Source version: 0.1.0.dev2" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.1.0.dev2&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_provider_openrouter/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_provider_openrouter/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_provider_openrouter/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_provider_openrouter/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_provider_openrouter/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_provider_openrouter/"><img alt="Monthly PyPI downloads: swarmauri_provider_openrouter" src="https://img.shields.io/pypi/dm/swarmauri_provider_openrouter"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_provider_openrouter/README.md"><img alt="README hits: swarmauri_provider_openrouter" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/50-community/swarmauri_provider_openrouter/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_provider_openrouter/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_provider_openrouter/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

[![PyPI version](https://img.shields.io/pypi/v/swarmauri_provider_openrouter.svg)](https://pypi.org/project/swarmauri_provider_openrouter/) [![Python versions](https://img.shields.io/pypi/pyversions/swarmauri_provider_openrouter.svg)](https://pypi.org/project/swarmauri_provider_openrouter/) [![Downloads](https://static.pepy.tech/badge/swarmauri_provider_openrouter/month)](https://pepy.tech/project/swarmauri_provider_openrouter) [![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/50-community/swarmauri_provider_openrouter.svg)](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/50-community/swarmauri_provider_openrouter/) [![License](https://img.shields.io/pypi/l/swarmauri_provider_openrouter.svg)](https://pypi.org/project/swarmauri_provider_openrouter/)

`swarmauri_provider_openrouter` describes OpenRouter authentication, endpoints,
model metadata, routing preferences, provider errors, and tool schemas without
owning an HTTP implementation.

### Why This Package

`swarmauri_provider_openrouter` isolates this responsibility: OpenRouter provider configuration, routing, catalogs, errors, and tool schemas for Swarmauri. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_provider_openrouter/swarmauri_provider_openrouter/__init__.py) exposes `OpenRouterAuthConfig`, `OpenRouterEndpoints`, `OpenRouterErrorMapper`, `OpenRouterModelCatalog`, `OpenRouterProvider`, `OpenRouterProviderPreferences`, `OpenRouterToolSchemaConverter`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_provider_openrouter` when your integration needs openRouter provider configuration, routing, catalogs, errors, and tool schemas for Swarmauri. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Bearer authentication with optional application attribution headers.
- Capability-based resolution for chat, catalog, and image-generation APIs.
- Provider routing, fallback, data-collection, and ZDR preferences.
- Mutable provider catalog populated by an injected model client.
- OpenRouter-compatible function-tool schema conversion.
- Serializable connection configurations that exclude credentials.

### Non-Goals

`swarmauri_provider_openrouter` owns openRouter provider configuration, routing, catalogs, errors, and tool schemas for Swarmauri. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_provider_openrouter/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`. Read the example’s inputs and service requirements before execution.

### Installation

```bash
uv add swarmauri_provider_openrouter
```

```bash
pip install swarmauri_provider_openrouter
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_provider_openrouter
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_provider_openrouter
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_provider_openrouter
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_provider_openrouter/docs/readme/quick_start.py).

```python
from swarmauri_provider_openrouter import (
    OpenRouterProvider,
    OpenRouterProviderPreferences,
)

provider = OpenRouterProvider(
    api_key="...",
    site_url="https://example.com",
    app_name="My application",
)
config = provider.connection_config(
    "chat.completions",
    model="openai/gpt-4o-mini",
)
headers = provider.authorize(config)
routing = OpenRouterProviderPreferences(order=["OpenAI"])
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_provider_openrouter` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_provider_openrouter/docs/readme/usage.py).

```python
from swarmauri_provider_openrouter import (
    OpenRouterProvider,
    OpenRouterProviderPreferences,
)

provider = OpenRouterProvider(
    api_key="...",
    site_url="https://example.com",
    app_name="My application",
)
config = provider.connection_config(
    "chat.completions",
    model="openai/gpt-4o-mini",
)
headers = provider.authorize(config)
routing = OpenRouterProviderPreferences(order=["OpenAI"])
```
<!-- readme-standards:end example.usage -->

Pass the provider and routing preferences to a compatible model package. The
provider returns connection configuration; a Swarmauri transport such as
`swarmauri_transport_httpx` performs the request.

### Configuration

Configure `swarmauri_provider_openrouter` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_provider_openrouter/swarmauri_provider_openrouter/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_provider_openrouter/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_provider_openrouter` source raises `TypeError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_provider_openrouter` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `OpenRouterAuthConfig`, `OpenRouterEndpoints`, `OpenRouterErrorMapper`, `OpenRouterModelCatalog`, `OpenRouterProvider`, `OpenRouterProviderPreferences`, `OpenRouterToolSchemaConverter`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_provider_openrouter` is located in `community` and owns openRouter provider configuration, routing, catalogs, errors, and tool schemas for Swarmauri. Source-declared APIs include `OpenRouterAuthConfig`, `OpenRouterEndpoints`, `OpenRouterErrorMapper`, `OpenRouterModelCatalog`, `OpenRouterProvider`, `OpenRouterProviderPreferences`, `OpenRouterToolSchemaConverter`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_provider_openrouter/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_provider_openrouter`.

Source-declared exports or types: `OpenRouterAuthConfig`, `OpenRouterEndpoints`, `OpenRouterErrorMapper`, `OpenRouterModelCatalog`, `OpenRouterProvider`, `OpenRouterProviderPreferences`, `OpenRouterToolSchemaConverter`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_provider_openrouter/swarmauri_provider_openrouter/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.model_providers` → `OpenRouterProvider` → `swarmauri_provider_openrouter:OpenRouterProvider`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_provider_openrouter` are `swarmauri-core`, `swarmauri-base`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_provider_openrouter/swarmauri_provider_openrouter/__init__.py).

### Protocol Consumers

Direct consumers in this checkout’s package manifests include `swarmauri_llm_openrouter`. These edges describe declared dependencies, not protocol-conformance evidence.

### Extensions

For `swarmauri_provider_openrouter`, use the source-declared public interfaces (`OpenRouterAuthConfig`, `OpenRouterEndpoints`, `OpenRouterErrorMapper`, `OpenRouterModelCatalog`, `OpenRouterProvider`, `OpenRouterProviderPreferences`, `OpenRouterToolSchemaConverter`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_provider_openrouter` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_provider_openrouter/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_provider_openrouter`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_provider_openrouter/swarmauri_provider_openrouter/__init__.py). The `swarmauri_provider_openrouter` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_provider_openrouter` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_provider_openrouter` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/unit/test_openrouter_provider.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_provider_openrouter/tests/unit/test_openrouter_provider.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_provider_openrouter` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_provider_openrouter/swarmauri_provider_openrouter/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_provider_openrouter` provides openRouter provider configuration, routing, catalogs, errors, and tool schemas for Swarmauri; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_provider_openrouter`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_provider_openrouter/swarmauri_provider_openrouter/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_provider_openrouter` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_provider_openrouter/swarmauri_provider_openrouter/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_provider_openrouter/pyproject.toml) provide the supporting context for `swarmauri_provider_openrouter`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_provider_openrouter](https://pypi.org/project/swarmauri_provider_openrouter/)
<!-- readme-standards:end project-links -->

- [Swarmauri SDK](https://github.com/swarmauri/swarmauri-sdk)
- [OpenRouter documentation](https://openrouter.ai/docs)

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_provider_openrouter`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/50-community/swarmauri_provider_openrouter` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_provider_openrouter` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_provider_openrouter` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_provider_openrouter/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_provider_openrouter` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_provider_openrouter` source version is `0.1.0.dev2`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_provider_openrouter/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_provider_openrouter/NOTICE) for attribution.
<!-- readme-standards:end notices -->
