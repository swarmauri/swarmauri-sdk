# swarmauri_auth_idp_azure

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_auth_idp_azure</strong></p>
<p align="center">Azure Active Directory OAuth 2.0 / 2.1 / OIDC 1.0 login implementations for Swarmauri deployments</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_auth_idp_azure/"><img alt="pypi: swarmauri_auth_idp_azure" src="https://img.shields.io/pypi/v/swarmauri_auth_idp_azure?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_azure/pyproject.toml"><img alt="Source version: 0.11.0" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_azure/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_azure/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_azure/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_azure/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_azure/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_auth_idp_azure/"><img alt="Monthly PyPI downloads: swarmauri_auth_idp_azure" src="https://img.shields.io/pypi/dm/swarmauri_auth_idp_azure?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_azure/README.md"><img alt="README hits: swarmauri_auth_idp_azure" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/40-standards/swarmauri_auth_idp_azure/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_azure/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_azure/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

Azure Active Directory / Entra ID OAuth 2.0, OAuth 2.1, and OIDC 1.0 login flows packaged for Swarmauri deployments.

### Why This Package

`swarmauri_auth_idp_azure` isolates this responsibility: Azure Active Directory OAuth 2.0 / 2.1 / OIDC 1.0 login implementations for Swarmauri deployments. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_azure/swarmauri_auth_idp_azure/__init__.py) exposes `AzureOAuth20Login`, `AzureOAuth21Login`, `AzureOIDC10Login`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_auth_idp_azure` when your integration needs azure Active Directory OAuth 2.0 / 2.1 / OIDC 1.0 login implementations for Swarmauri deployments. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- PKCE-enabled authorization URL generation with signed state payloads to protect verifiers.
- Token exchange helpers that return normalized identity details from Microsoft Graph.
- Built-in retrying HTTP client for resilient calls against Azure AD and Graph endpoints.
- ComponentBase-compatible models that register under `swarmauri.auth_idp` entry points.
- Support for both interactive browser logins and confidential client OIDC workflows.

### Non-Goals

`swarmauri_auth_idp_azure` owns azure Active Directory OAuth 2.0 / 2.1 / OIDC 1.0 login implementations for Swarmauri deployments. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_azure/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `httpx`, `pyjwt`. Read the example’s inputs and service requirements before execution.

### Installation

**uv (project)**

```bash
uv add swarmauri_auth_idp_azure
```

**uv (environment)**

```bash
uv pip install swarmauri_auth_idp_azure
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_auth_idp_azure
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_auth_idp_azure
```
<!-- readme-standards:end installation.pip -->

```bash
pip install swarmauri_auth_idp_azure
```

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_auth_idp_azure
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_azure/docs/readme/quick_start.py).

```python
from pydantic import SecretStr
from swarmauri_auth_idp_azure import AzureOAuth21Login

login = AzureOAuth21Login(
    tenant="organizations",
    client_id="00000000-0000-0000-0000-000000000000",
    client_secret=SecretStr("client-secret"),
    redirect_uri="https://app.example.com/auth/callback",
    state_secret=b"azure-ad-state-key",
)

print(login.client_id)
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_auth_idp_azure` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_azure/docs/readme/usage.py).

```python
from pydantic import SecretStr
from swarmauri_auth_idp_azure import AzureOAuth21Login

login = AzureOAuth21Login(
    tenant="organizations",
    client_id="00000000-0000-0000-0000-000000000000",
    client_secret=SecretStr("client-secret"),
    redirect_uri="https://app.example.com/auth/callback",
    state_secret=b"azure-ad-state-key",
)

print(login.client_id)
```
<!-- readme-standards:end example.usage -->

1. Call `auth_url()` and redirect the browser to the returned Microsoft login URL.
2. Persist the `state` token and compare it when handling the callback.
3. Exchange the authorization code via `exchange_and_identity()` to obtain tokens and Graph profile data.
4. Persist the returned tokens or computed identity details for session and authorization workflows.

### Configuration

Configure `swarmauri_auth_idp_azure` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_azure/swarmauri_auth_idp_azure/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_azure/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_auth_idp_azure` source raises `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_auth_idp_azure` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `AzureOAuth20Login`, `AzureOAuth21Login`, `AzureOIDC10Login`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_auth_idp_azure` is located in `standards` and owns azure Active Directory OAuth 2.0 / 2.1 / OIDC 1.0 login implementations for Swarmauri deployments. Source-declared APIs include `AzureOAuth20Login`, `AzureOAuth21Login`, `AzureOIDC10Login`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_azure/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_auth_idp_azure`.

Source-declared exports or types: `AzureOAuth20Login`, `AzureOAuth21Login`, `AzureOIDC10Login`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_azure/swarmauri_auth_idp_azure/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.auth_idp` → `AzureOAuth20Login` → `swarmauri_auth_idp_azure:AzureOAuth20Login`
- `swarmauri.auth_idp` → `AzureOAuth21Login` → `swarmauri_auth_idp_azure:AzureOAuth21Login`
- `swarmauri.auth_idp` → `AzureOIDC10Login` → `swarmauri_auth_idp_azure:AzureOIDC10Login`
<!-- readme-standards:end entry-points -->

- `swarmauri.auth_idp:AzureOAuth20Login`
- `swarmauri.auth_idp:AzureOAuth21Login`
- `swarmauri.auth_idp:AzureOIDC10Login`

### Injected Dependencies

The direct installation dependencies of `swarmauri_auth_idp_azure` are `swarmauri-core`, `swarmauri-base`, `httpx`, `pyjwt`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_azure/swarmauri_auth_idp_azure/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_auth_idp_azure` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_auth_idp_azure`, use the source-declared public interfaces (`AzureOAuth20Login`, `AzureOAuth21Login`, `AzureOIDC10Login`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_auth_idp_azure` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_azure/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_auth_idp_azure`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_azure/swarmauri_auth_idp_azure/__init__.py). The `swarmauri_auth_idp_azure` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_auth_idp_azure` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_auth_idp_azure` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/unit/test_azure_oauth20_login_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_azure/tests/unit/test_azure_oauth20_login_unit.py)
- [tests/unit/test_azure_oauth21_login_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_azure/tests/unit/test_azure_oauth21_login_unit.py)
- [tests/unit/test_azure_oidc10_login_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_azure/tests/unit/test_azure_oidc10_login_unit.py)
- [tests/unit/test_azure_login_contract_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_azure/tests/unit/test_azure_login_contract_unit.py)

Run the full offline package suite from the `pkgs/` directory with `uv run --package swarmauri_auth_idp_azure --directory standards/swarmauri_auth_idp_azure pytest`. The contract tests in `tests/unit/test_azure_login_contract_unit.py` use fake HTTP clients and locally signed ID tokens; they verify the request/response contract only, not live Azure interoperability.

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_auth_idp_azure` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_azure/swarmauri_auth_idp_azure/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_auth_idp_azure` provides azure Active Directory OAuth 2.0 / 2.1 / OIDC 1.0 login implementations for Swarmauri deployments; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_auth_idp_azure`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_azure/swarmauri_auth_idp_azure/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_auth_idp_azure` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_azure/swarmauri_auth_idp_azure/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_azure/pyproject.toml) provide the supporting context for `swarmauri_auth_idp_azure`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_auth_idp_azure](https://pypi.org/project/swarmauri_auth_idp_azure/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

To contribute to swarmauri-sdk, review the
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
which cover development workflow, testing, and coding standards.

### Development Setup

Work from the `pkgs/40-standards/swarmauri_auth_idp_azure` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_auth_idp_azure` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_auth_idp_azure` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_azure/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_auth_idp_azure` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_auth_idp_azure` source version is `0.11.0`.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_azure/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_azure/NOTICE) for attribution.
<!-- readme-standards:end notices -->
