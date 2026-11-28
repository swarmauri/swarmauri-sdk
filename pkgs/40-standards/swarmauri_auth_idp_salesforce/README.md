# swarmauri_auth_idp_salesforce

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_auth_idp_salesforce</strong></p>
<p align="center">Salesforce OAuth 2.0 / OAuth 2.1 / OIDC 1.0 identity provider implementations for Swarmauri</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_auth_idp_salesforce/"><img alt="pypi: swarmauri_auth_idp_salesforce" src="https://img.shields.io/pypi/v/swarmauri_auth_idp_salesforce?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_salesforce/pyproject.toml"><img alt="Source version: 0.11.0" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_salesforce/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_salesforce/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_salesforce/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_salesforce/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_salesforce/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_auth_idp_salesforce/"><img alt="Monthly PyPI downloads: swarmauri_auth_idp_salesforce" src="https://img.shields.io/pypi/dm/swarmauri_auth_idp_salesforce?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_salesforce/README.md"><img alt="README hits: swarmauri_auth_idp_salesforce" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/40-standards/swarmauri_auth_idp_salesforce/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_salesforce/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_salesforce/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

Salesforce OAuth 2.0 / OAuth 2.1 / OIDC 1.0 identity providers packaged for Swarmauri deployments.

### Why This Package

`swarmauri_auth_idp_salesforce` isolates this responsibility: Salesforce OAuth 2.0 / OAuth 2.1 / OIDC 1.0 identity provider implementations for Swarmauri. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_salesforce/swarmauri_auth_idp_salesforce/__init__.py) exposes `SalesforceOAuth20AppClient`, `SalesforceOAuth20Login`, `SalesforceOAuth21AppClient`, `SalesforceOAuth21Login`, `SalesforceOIDC10AppClient`, `SalesforceOIDC10Login`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_auth_idp_salesforce` when your integration needs salesforce OAuth 2.0 / OAuth 2.1 / OIDC 1.0 identity provider implementations for Swarmauri. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- PKCE-enabled Authorization Code flows that integrate with Salesforce authorization servers.
- JWT bearer app clients for Salesforce OAuth 2.0, OAuth 2.1, and OIDC 1.0 machine identities.
- Discovery-driven OAuth 2.1/OIDC login that verifies ID tokens against Salesforce JWKS.
- UserInfo and Identity URL fallbacks for normalized profile payloads.
- Retry-aware HTTP integration tuned for Salesforce REST endpoints.
- ComponentBase-compatible models registered under `swarmauri.auth_idp` entry points.

### Non-Goals

`swarmauri_auth_idp_salesforce` owns salesforce OAuth 2.0 / OAuth 2.1 / OIDC 1.0 identity provider implementations for Swarmauri. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_salesforce/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `httpx`, `pyjwt`. Read the example’s inputs and service requirements before execution.

### Installation

**uv (project)**

```bash
uv add swarmauri_auth_idp_salesforce
```

**uv (environment)**

```bash
uv pip install swarmauri_auth_idp_salesforce
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_auth_idp_salesforce
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_auth_idp_salesforce
```
<!-- readme-standards:end installation.pip -->

```bash
pip install swarmauri_auth_idp_salesforce
```

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_auth_idp_salesforce
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_salesforce/docs/readme/quick_start.py).

```python
import asyncio
from pydantic import SecretBytes, SecretStr
from swarmauri_auth_idp_salesforce import SalesforceOAuth20Login

login = SalesforceOAuth20Login(
    base_url="https://login.salesforce.com",
    client_id="salesforce-client-id",
    client_secret=SecretStr("salesforce-client-secret"),
    redirect_uri="https://app.example.com/callback",
    state_secret=SecretBytes(b"replace-with-random-bytes"),
)

# Optional discovery cache when running without network access.
login.discovery_cache = {
    "authorization_endpoint": "https://login.salesforce.com/services/oauth2/authorize",
    "token_endpoint": "https://login.salesforce.com/services/oauth2/token",
    "userinfo_endpoint": "https://login.salesforce.com/services/oauth2/userinfo",
}


async def run_flow() -> None:
    auth = await login.auth_url()
    print(auth["url"])
    # Send the browser to the authorization URL and capture code and state.
    # In the callback, pass code and state to exchange_and_identity.


asyncio.run(run_flow())
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_auth_idp_salesforce` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_salesforce/docs/readme/usage.py).

```python
import asyncio
from pydantic import SecretBytes, SecretStr
from swarmauri_auth_idp_salesforce import SalesforceOAuth20Login

login = SalesforceOAuth20Login(
    base_url="https://login.salesforce.com",
    client_id="salesforce-client-id",
    client_secret=SecretStr("salesforce-client-secret"),
    redirect_uri="https://app.example.com/callback",
    state_secret=SecretBytes(b"replace-with-random-bytes"),
)

# Optional discovery cache when running without network access.
login.discovery_cache = {
    "authorization_endpoint": "https://login.salesforce.com/services/oauth2/authorize",
    "token_endpoint": "https://login.salesforce.com/services/oauth2/token",
    "userinfo_endpoint": "https://login.salesforce.com/services/oauth2/userinfo",
}


async def run_flow() -> None:
    auth = await login.auth_url()
    print(auth["url"])
    # Send the browser to the authorization URL and capture code and state.
    # In the callback, pass code and state to exchange_and_identity.


asyncio.run(run_flow())
```
<!-- readme-standards:end example.usage -->

**Authorization Code logins**


1. Call `auth_url()` and redirect the browser to the returned URL.
2. Persist the `state` and verify it during the callback handler.
3. Exchange the authorization code through `exchange_and_identity()` to obtain tokens and profile metadata.

**Server-to-server JWT bearer tokens**

```python
import asyncio
from pydantic import SecretStr
from swarmauri_auth_idp_salesforce import SalesforceOAuth20AppClient

client = SalesforceOAuth20AppClient(
    token_endpoint="https://login.salesforce.com/services/oauth2/token",
    client_id="connected-app-id",
    user="integration.user@example.com",
    private_key_pem=SecretStr("-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"),
)

async def fetch_token() -> None:
    access_token = await client.access_token()
    print(access_token)

asyncio.run(fetch_token())
```

Use `SalesforceOAuth21AppClient` when your integration manages keys as JWKs, or
`SalesforceOIDC10AppClient` to discover tenant-specific endpoints before
requesting JWT bearer tokens.

### Configuration

Configure `swarmauri_auth_idp_salesforce` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_salesforce/swarmauri_auth_idp_salesforce/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_salesforce/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_auth_idp_salesforce` source raises `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_auth_idp_salesforce` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `SalesforceOAuth20AppClient`, `SalesforceOAuth20Login`, `SalesforceOAuth21AppClient`, `SalesforceOAuth21Login`, `SalesforceOIDC10AppClient`, `SalesforceOIDC10Login`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_auth_idp_salesforce` is located in `standards` and owns salesforce OAuth 2.0 / OAuth 2.1 / OIDC 1.0 identity provider implementations for Swarmauri. Source-declared APIs include `SalesforceOAuth20AppClient`, `SalesforceOAuth20Login`, `SalesforceOAuth21AppClient`, `SalesforceOAuth21Login`, `SalesforceOIDC10AppClient`, `SalesforceOIDC10Login`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_salesforce/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_auth_idp_salesforce`.

Source-declared exports or types: `SalesforceOAuth20AppClient`, `SalesforceOAuth20Login`, `SalesforceOAuth21AppClient`, `SalesforceOAuth21Login`, `SalesforceOIDC10AppClient`, `SalesforceOIDC10Login`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_salesforce/swarmauri_auth_idp_salesforce/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.auth_idp` → `SalesforceOAuth20AppClient` → `swarmauri_auth_idp_salesforce:SalesforceOAuth20AppClient`
- `swarmauri.auth_idp` → `SalesforceOAuth20Login` → `swarmauri_auth_idp_salesforce:SalesforceOAuth20Login`
- `swarmauri.auth_idp` → `SalesforceOAuth21AppClient` → `swarmauri_auth_idp_salesforce:SalesforceOAuth21AppClient`
- `swarmauri.auth_idp` → `SalesforceOAuth21Login` → `swarmauri_auth_idp_salesforce:SalesforceOAuth21Login`
- `swarmauri.auth_idp` → `SalesforceOIDC10AppClient` → `swarmauri_auth_idp_salesforce:SalesforceOIDC10AppClient`
- `swarmauri.auth_idp` → `SalesforceOIDC10Login` → `swarmauri_auth_idp_salesforce:SalesforceOIDC10Login`
<!-- readme-standards:end entry-points -->

- `swarmauri.auth_idp:SalesforceOAuth20AppClient`
- `swarmauri.auth_idp:SalesforceOAuth20Login`
- `swarmauri.auth_idp:SalesforceOAuth21AppClient`
- `swarmauri.auth_idp:SalesforceOAuth21Login`
- `swarmauri.auth_idp:SalesforceOIDC10AppClient`
- `swarmauri.auth_idp:SalesforceOIDC10Login`

### Injected Dependencies

The direct installation dependencies of `swarmauri_auth_idp_salesforce` are `swarmauri-core`, `swarmauri-base`, `httpx`, `pyjwt`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_salesforce/swarmauri_auth_idp_salesforce/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_auth_idp_salesforce` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_auth_idp_salesforce`, use the source-declared public interfaces (`SalesforceOAuth20AppClient`, `SalesforceOAuth20Login`, `SalesforceOAuth21AppClient`, `SalesforceOAuth21Login`, `SalesforceOIDC10AppClient`, `SalesforceOIDC10Login`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_auth_idp_salesforce` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_salesforce/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_auth_idp_salesforce`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_salesforce/swarmauri_auth_idp_salesforce/__init__.py). The `swarmauri_auth_idp_salesforce` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_auth_idp_salesforce` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run the full package suite offline from the repository's `pkgs/` directory with `uv run --package swarmauri_auth_idp_salesforce --directory standards/swarmauri_auth_idp_salesforce pytest`. The tests use fake HTTP clients and throwaway signing keys, with no network access, credentials, or live Salesforce account: they verify the request/response contract only and do not prove interoperability with Salesforce's production service. Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_auth_idp_salesforce` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/unit/test_salesforce_oauth20_app_client_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_salesforce/tests/unit/test_salesforce_oauth20_app_client_unit.py)
- [tests/unit/test_salesforce_oauth20_login_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_salesforce/tests/unit/test_salesforce_oauth20_login_unit.py)
- [tests/unit/test_salesforce_oauth21_app_client_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_salesforce/tests/unit/test_salesforce_oauth21_app_client_unit.py)
- [tests/unit/test_salesforce_oauth21_login_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_salesforce/tests/unit/test_salesforce_oauth21_login_unit.py)
- [tests/unit/test_salesforce_oidc10_app_client_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_salesforce/tests/unit/test_salesforce_oidc10_app_client_unit.py)
- [tests/unit/test_salesforce_oidc10_login_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_salesforce/tests/unit/test_salesforce_oidc10_login_unit.py)
- [tests/unit/test_salesforce_login_contract_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_salesforce/tests/unit/test_salesforce_login_contract_unit.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_auth_idp_salesforce` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_salesforce/swarmauri_auth_idp_salesforce/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_auth_idp_salesforce` provides salesforce OAuth 2.0 / OAuth 2.1 / OIDC 1.0 identity provider implementations for Swarmauri; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_auth_idp_salesforce`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_salesforce/swarmauri_auth_idp_salesforce/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_auth_idp_salesforce` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_salesforce/swarmauri_auth_idp_salesforce/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_salesforce/pyproject.toml) provide the supporting context for `swarmauri_auth_idp_salesforce`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_auth_idp_salesforce](https://pypi.org/project/swarmauri_auth_idp_salesforce/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

To contribute to swarmauri-sdk, review the
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
which cover development workflow, testing, and coding standards.

### Development Setup

Work from the `pkgs/40-standards/swarmauri_auth_idp_salesforce` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_auth_idp_salesforce` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_auth_idp_salesforce` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_salesforce/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_auth_idp_salesforce` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_auth_idp_salesforce` source version is `0.11.0`.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_salesforce/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_salesforce/NOTICE) for attribution.
<!-- readme-standards:end notices -->
