# swarmauri_auth_idp_okta

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_auth_idp_okta</strong></p>
<p align="center">Okta OAuth 2.0 / OAuth 2.1 / OIDC 1.0 identity provider implementations for Swarmauri</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_auth_idp_okta/"><img alt="pypi: swarmauri_auth_idp_okta" src="https://img.shields.io/pypi/v/swarmauri_auth_idp_okta"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_okta/pyproject.toml"><img alt="Source version: 0.11.0.dev4" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev4&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_okta/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_okta/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_okta/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_okta/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_okta/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_auth_idp_okta/"><img alt="Monthly PyPI downloads: swarmauri_auth_idp_okta" src="https://img.shields.io/pypi/dm/swarmauri_auth_idp_okta"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_okta/README.md"><img alt="README hits: swarmauri_auth_idp_okta" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/40-standards/swarmauri_auth_idp_okta/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_okta/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_okta/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

Okta OAuth 2.0 / OAuth 2.1 / OIDC 1.0 identity providers packaged for Swarmauri deployments.

### Why This Package

`swarmauri_auth_idp_okta` isolates this responsibility: Okta OAuth 2.0 / OAuth 2.1 / OIDC 1.0 identity provider implementations for Swarmauri. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_okta/swarmauri_auth_idp_okta/__init__.py) exposes `OktaOAuth20AppClient`, `OktaOAuth20Login`, `OktaOAuth21AppClient`, `OktaOAuth21Login`, `OktaOIDC10AppClient`, `OktaOIDC10Login`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_auth_idp_okta` when your integration needs okta OAuth 2.0 / OAuth 2.1 / OIDC 1.0 identity provider implementations for Swarmauri. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- PKCE-enabled Authorization Code flows that integrate with Okta authorization servers.
- Machine-to-machine app clients for Okta OAuth 2.0, OAuth 2.1 (private key JWT), and OIDC 1.0.
- Discovery-driven OAuth 2.1/OIDC login that verifies ID tokens using Okta JWKS.
- UserInfo enrichment for deployments that require full user profile hydration.
- Retry-aware HTTP integration tuned for Okta endpoints.
- ComponentBase-compatible models registered under `swarmauri.auth_idp` entry points.

### Non-Goals

`swarmauri_auth_idp_okta` owns okta OAuth 2.0 / OAuth 2.1 / OIDC 1.0 identity provider implementations for Swarmauri. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_okta/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `httpx`, `pyjwt`. Read the example’s inputs and service requirements before execution.

### Installation

**uv (project)**

```bash
uv add swarmauri_auth_idp_okta
```

**uv (environment)**

```bash
uv pip install swarmauri_auth_idp_okta
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_auth_idp_okta
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_auth_idp_okta
```
<!-- readme-standards:end installation.pip -->

```bash
pip install swarmauri_auth_idp_okta
```

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_auth_idp_okta
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_okta/docs/readme/quick_start.py).

```python
import asyncio
from pydantic import SecretBytes, SecretStr
from swarmauri_auth_idp_okta import OktaOAuth20Login

login = OktaOAuth20Login(
    issuer="https://example.okta.com/oauth2/default",
    client_id="okta-client-id",
    client_secret=SecretStr("okta-client-secret"),
    redirect_uri="https://app.example.com/callback",
    state_secret=SecretBytes(b"replace-with-random-bytes"),
)


async def run_flow() -> None:
    auth = await login.auth_url()
    print(auth["url"])
    # Redirect the browser to `auth["url"]` and capture `code` and `state`.
    # In the callback handler, call `login.exchange_and_identity(code, state)`.


asyncio.run(run_flow())
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_auth_idp_okta` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_okta/docs/readme/usage.py).

```python
import asyncio
from pydantic import SecretBytes, SecretStr
from swarmauri_auth_idp_okta import OktaOAuth20Login

login = OktaOAuth20Login(
    issuer="https://example.okta.com/oauth2/default",
    client_id="okta-client-id",
    client_secret=SecretStr("okta-client-secret"),
    redirect_uri="https://app.example.com/callback",
    state_secret=SecretBytes(b"replace-with-random-bytes"),
)


async def run_flow() -> None:
    auth = await login.auth_url()
    print(auth["url"])
    # Redirect the browser to `auth["url"]` and capture `code` and `state`.
    # In the callback handler, call `login.exchange_and_identity(code, state)`.


asyncio.run(run_flow())
```
<!-- readme-standards:end example.usage -->

1. Call `auth_url()` and redirect the browser to the returned URL.
2. Persist the `state` and verify it during the callback handler.
3. Exchange the authorization code through `exchange_and_identity()` to obtain tokens and profile metadata.

**Server-to-server client credentials**

```python
import asyncio
from pydantic import SecretStr
from swarmauri_auth_idp_okta import OktaOAuth20AppClient

client = OktaOAuth20AppClient(
    issuer="https://example.okta.com/oauth2/default",
    client_id="machine-client-id",
    client_secret=SecretStr("machine-client-secret"),
)

async def fetch_token() -> None:
    token = await client.access_token(scope="customScope")
    print(token)

asyncio.run(fetch_token())
```

Use `OktaOAuth21AppClient` when the integration should authenticate with
`private_key_jwt`, or `OktaOIDC10AppClient` to rely on discovery metadata for
tenant-specific token endpoints.

### Configuration

Configure `swarmauri_auth_idp_okta` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_okta/swarmauri_auth_idp_okta/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_okta/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_auth_idp_okta` source raises `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_auth_idp_okta` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `OktaOAuth20AppClient`, `OktaOAuth20Login`, `OktaOAuth21AppClient`, `OktaOAuth21Login`, `OktaOIDC10AppClient`, `OktaOIDC10Login`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_auth_idp_okta` is located in `standards` and owns okta OAuth 2.0 / OAuth 2.1 / OIDC 1.0 identity provider implementations for Swarmauri. Source-declared APIs include `OktaOAuth20AppClient`, `OktaOAuth20Login`, `OktaOAuth21AppClient`, `OktaOAuth21Login`, `OktaOIDC10AppClient`, `OktaOIDC10Login`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_okta/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_auth_idp_okta`.

Source-declared exports or types: `OktaOAuth20AppClient`, `OktaOAuth20Login`, `OktaOAuth21AppClient`, `OktaOAuth21Login`, `OktaOIDC10AppClient`, `OktaOIDC10Login`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_okta/swarmauri_auth_idp_okta/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.auth_idp` → `OktaOAuth20AppClient` → `swarmauri_auth_idp_okta:OktaOAuth20AppClient`
- `swarmauri.auth_idp` → `OktaOAuth20Login` → `swarmauri_auth_idp_okta:OktaOAuth20Login`
- `swarmauri.auth_idp` → `OktaOAuth21AppClient` → `swarmauri_auth_idp_okta:OktaOAuth21AppClient`
- `swarmauri.auth_idp` → `OktaOAuth21Login` → `swarmauri_auth_idp_okta:OktaOAuth21Login`
- `swarmauri.auth_idp` → `OktaOIDC10AppClient` → `swarmauri_auth_idp_okta:OktaOIDC10AppClient`
- `swarmauri.auth_idp` → `OktaOIDC10Login` → `swarmauri_auth_idp_okta:OktaOIDC10Login`
<!-- readme-standards:end entry-points -->

- `swarmauri.auth_idp:OktaOAuth20AppClient`
- `swarmauri.auth_idp:OktaOAuth20Login`
- `swarmauri.auth_idp:OktaOAuth21AppClient`
- `swarmauri.auth_idp:OktaOAuth21Login`
- `swarmauri.auth_idp:OktaOIDC10AppClient`
- `swarmauri.auth_idp:OktaOIDC10Login`

### Injected Dependencies

The direct installation dependencies of `swarmauri_auth_idp_okta` are `swarmauri-core`, `swarmauri-base`, `httpx`, `pyjwt`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_okta/swarmauri_auth_idp_okta/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_auth_idp_okta` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_auth_idp_okta`, use the source-declared public interfaces (`OktaOAuth20AppClient`, `OktaOAuth20Login`, `OktaOAuth21AppClient`, `OktaOAuth21Login`, `OktaOIDC10AppClient`, `OktaOIDC10Login`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_auth_idp_okta` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_okta/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_auth_idp_okta`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_okta/swarmauri_auth_idp_okta/__init__.py). The `swarmauri_auth_idp_okta` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_auth_idp_okta` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run the full package suite offline from the repository's `pkgs/` directory with `uv run --package swarmauri_auth_idp_okta --directory standards/swarmauri_auth_idp_okta pytest`. The tests use fake HTTP clients and throwaway signing keys, with no network access, credentials, or live Okta account: they verify the request/response contract only and do not prove interoperability with Okta's production service. Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_auth_idp_okta` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/unit/test_okta_oauth20_app_client_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_okta/tests/unit/test_okta_oauth20_app_client_unit.py)
- [tests/unit/test_okta_oauth20_login_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_okta/tests/unit/test_okta_oauth20_login_unit.py)
- [tests/unit/test_okta_oauth21_app_client_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_okta/tests/unit/test_okta_oauth21_app_client_unit.py)
- [tests/unit/test_okta_oauth21_login_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_okta/tests/unit/test_okta_oauth21_login_unit.py)
- [tests/unit/test_okta_oidc10_app_client_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_okta/tests/unit/test_okta_oidc10_app_client_unit.py)
- [tests/unit/test_okta_oidc10_login_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_okta/tests/unit/test_okta_oidc10_login_unit.py)
- [tests/unit/test_okta_oauth_login_contract_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_okta/tests/unit/test_okta_oauth_login_contract_unit.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_auth_idp_okta` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_okta/swarmauri_auth_idp_okta/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_auth_idp_okta` provides okta OAuth 2.0 / OAuth 2.1 / OIDC 1.0 identity provider implementations for Swarmauri; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_auth_idp_okta`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_okta/swarmauri_auth_idp_okta/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_auth_idp_okta` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_okta/swarmauri_auth_idp_okta/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_okta/pyproject.toml) provide the supporting context for `swarmauri_auth_idp_okta`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_auth_idp_okta](https://pypi.org/project/swarmauri_auth_idp_okta/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

To contribute to swarmauri-sdk, review the
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
which cover development workflow, testing, and coding standards.

### Development Setup

Work from the `pkgs/40-standards/swarmauri_auth_idp_okta` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_auth_idp_okta` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_auth_idp_okta` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_okta/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_auth_idp_okta` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_auth_idp_okta` source version is `0.11.0.dev4`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_okta/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_auth_idp_okta/NOTICE) for attribution.
<!-- readme-standards:end notices -->
