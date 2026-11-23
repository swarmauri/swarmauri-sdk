# swarmauri_auth_idp_cognito

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_auth_idp_cognito</strong></p>
<p align="center">AWS Cognito OAuth 2.0 / OAuth 2.1 / OIDC 1.0 identity provider implementations for Swarmauri</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_auth_idp_cognito/"><img alt="pypi: swarmauri_auth_idp_cognito" src="https://img.shields.io/pypi/v/swarmauri_auth_idp_cognito"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_auth_idp_cognito/pyproject.toml"><img alt="Source version: 0.11.0.dev4" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev4&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_auth_idp_cognito/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_auth_idp_cognito/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_auth_idp_cognito/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_auth_idp_cognito/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_auth_idp_cognito/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_auth_idp_cognito/"><img alt="Monthly PyPI downloads: swarmauri_auth_idp_cognito" src="https://img.shields.io/pypi/dm/swarmauri_auth_idp_cognito"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_auth_idp_cognito/README.md"><img alt="README hits: swarmauri_auth_idp_cognito" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/standards/swarmauri_auth_idp_cognito/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_auth_idp_cognito/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_auth_idp_cognito/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

AWS Cognito OAuth 2.0, OAuth 2.1, and OIDC 1.0 login and app-client flows packaged for the Swarmauri ecosystem.

### Why This Package

`swarmauri_auth_idp_cognito` isolates this responsibility: AWS Cognito OAuth 2.0 / OAuth 2.1 / OIDC 1.0 identity provider implementations for Swarmauri. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_auth_idp_cognito/swarmauri_auth_idp_cognito/__init__.py) exposes `CognitoOAuth20AppClient`, `CognitoOAuth20Login`, `CognitoOAuth21AppClient`, `CognitoOAuth21Login`, `CognitoOIDC10AppClient`, `CognitoOIDC10Login`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_auth_idp_cognito` when your integration needs aWS Cognito OAuth 2.0 / OAuth 2.1 / OIDC 1.0 identity provider implementations for Swarmauri. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- PKCE-enabled authorization code logins with signed state payloads to prevent tampering.
- Automatic discovery of Cognito endpoints with resilient HTTP retry semantics.
- ID token verification against Cognito JWKS with graceful fallback to the UserInfo endpoint.
- Machine-to-machine app clients supporting shared secrets or JWT-based client assertions.
- ComponentBase-registered classes for seamless Swarmauri plugin discovery and configuration.

### Non-Goals

`swarmauri_auth_idp_cognito` owns aWS Cognito OAuth 2.0 / OAuth 2.1 / OIDC 1.0 identity provider implementations for Swarmauri. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_auth_idp_cognito/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `httpx`, `pyjwt`. Read the example’s inputs and service requirements before execution.

### Installation

**uv (project)**

```bash
uv add swarmauri_auth_idp_cognito
```

**uv (environment)**

```bash
uv pip install swarmauri_auth_idp_cognito
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_auth_idp_cognito
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_auth_idp_cognito
```
<!-- readme-standards:end installation.pip -->

```bash
pip install swarmauri_auth_idp_cognito
```

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_auth_idp_cognito
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_auth_idp_cognito/docs/readme/quick_start.py).

```python
from pydantic import SecretBytes, SecretStr
from swarmauri_auth_idp_cognito import CognitoOAuth21Login

login = CognitoOAuth21Login(
    issuer="https://example-domain.auth.us-east-1.amazoncognito.com",
    client_id="example-client-id",
    client_secret=SecretStr("example-secret"),
    redirect_uri="https://example.com/callback",
    state_secret=SecretBytes(b"super-secret-state-key"),
)

# Within an async context:
# auth_payload = await login.auth_url()
# identity = await login.exchange_and_identity(code, auth_payload["state"])
print(login.client_id)
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_auth_idp_cognito` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_auth_idp_cognito/docs/readme/usage.py).

```python
from pydantic import SecretBytes, SecretStr
from swarmauri_auth_idp_cognito import CognitoOAuth21Login

login = CognitoOAuth21Login(
    issuer="https://example-domain.auth.us-east-1.amazoncognito.com",
    client_id="example-client-id",
    client_secret=SecretStr("example-secret"),
    redirect_uri="https://example.com/callback",
    state_secret=SecretBytes(b"super-secret-state-key"),
)

# Within an async context:
# auth_payload = await login.auth_url()
# identity = await login.exchange_and_identity(code, auth_payload["state"])
print(login.client_id)
```
<!-- readme-standards:end example.usage -->

Instantiate the login classes with your Cognito issuer, app client credentials, and redirect URI.
Persist the returned state between `auth_url` and `exchange*` calls to prevent replay attacks.


**Expected Workflow**

1. Call `auth_url()` and redirect the user agent to the returned authorization URL.
2. Persist the state value and later validate it when Cognito posts back to your callback.
3. Call `exchange_and_identity()` (or `exchange()` for the OIDC login) to normalize identity claims.
4. Use the normalized payload to provision sessions, issue downstream tokens, or audit login activity.

App client classes expose the same `access_token` coroutine to support background services
and machine-to-machine integrations.

### Configuration

Configure `swarmauri_auth_idp_cognito` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_auth_idp_cognito/swarmauri_auth_idp_cognito/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_auth_idp_cognito/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_auth_idp_cognito` source raises `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_auth_idp_cognito` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `CognitoOAuth20AppClient`, `CognitoOAuth20Login`, `CognitoOAuth21AppClient`, `CognitoOAuth21Login`, `CognitoOIDC10AppClient`, `CognitoOIDC10Login`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_auth_idp_cognito` is located in `standards` and owns aWS Cognito OAuth 2.0 / OAuth 2.1 / OIDC 1.0 identity provider implementations for Swarmauri. Source-declared APIs include `CognitoOAuth20AppClient`, `CognitoOAuth20Login`, `CognitoOAuth21AppClient`, `CognitoOAuth21Login`, `CognitoOIDC10AppClient`, `CognitoOIDC10Login`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_auth_idp_cognito/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_auth_idp_cognito`.

Source-declared exports or types: `CognitoOAuth20AppClient`, `CognitoOAuth20Login`, `CognitoOAuth21AppClient`, `CognitoOAuth21Login`, `CognitoOIDC10AppClient`, `CognitoOIDC10Login`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_auth_idp_cognito/swarmauri_auth_idp_cognito/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.auth_idp` → `CognitoOAuth20AppClient` → `swarmauri_auth_idp_cognito:CognitoOAuth20AppClient`
- `swarmauri.auth_idp` → `CognitoOAuth20Login` → `swarmauri_auth_idp_cognito:CognitoOAuth20Login`
- `swarmauri.auth_idp` → `CognitoOAuth21AppClient` → `swarmauri_auth_idp_cognito:CognitoOAuth21AppClient`
- `swarmauri.auth_idp` → `CognitoOAuth21Login` → `swarmauri_auth_idp_cognito:CognitoOAuth21Login`
- `swarmauri.auth_idp` → `CognitoOIDC10AppClient` → `swarmauri_auth_idp_cognito:CognitoOIDC10AppClient`
- `swarmauri.auth_idp` → `CognitoOIDC10Login` → `swarmauri_auth_idp_cognito:CognitoOIDC10Login`
<!-- readme-standards:end entry-points -->

The distribution registers the following entry points:

- `swarmauri.auth_idp:CognitoOAuth20Login`
- `swarmauri.auth_idp:CognitoOAuth21Login`
- `swarmauri.auth_idp:CognitoOIDC10Login`
- `swarmauri.auth_idp:CognitoOAuth20AppClient`
- `swarmauri.auth_idp:CognitoOAuth21AppClient`
- `swarmauri.auth_idp:CognitoOIDC10AppClient`

### Injected Dependencies

The direct installation dependencies of `swarmauri_auth_idp_cognito` are `swarmauri-core`, `swarmauri-base`, `httpx`, `pyjwt`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_auth_idp_cognito/swarmauri_auth_idp_cognito/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_auth_idp_cognito` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_auth_idp_cognito`, use the source-declared public interfaces (`CognitoOAuth20AppClient`, `CognitoOAuth20Login`, `CognitoOAuth21AppClient`, `CognitoOAuth21Login`, `CognitoOIDC10AppClient`, `CognitoOIDC10Login`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_auth_idp_cognito` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_auth_idp_cognito/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_auth_idp_cognito`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_auth_idp_cognito/swarmauri_auth_idp_cognito/__init__.py). The `swarmauri_auth_idp_cognito` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_auth_idp_cognito` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_auth_idp_cognito` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/unit/test_cognito_oauth20_app_client_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_auth_idp_cognito/tests/unit/test_cognito_oauth20_app_client_unit.py)
- [tests/unit/test_cognito_oauth20_login_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_auth_idp_cognito/tests/unit/test_cognito_oauth20_login_unit.py)
- [tests/unit/test_cognito_oauth21_app_client_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_auth_idp_cognito/tests/unit/test_cognito_oauth21_app_client_unit.py)
- [tests/unit/test_cognito_oauth21_login_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_auth_idp_cognito/tests/unit/test_cognito_oauth21_login_unit.py)
- [tests/unit/test_cognito_oidc10_app_client_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_auth_idp_cognito/tests/unit/test_cognito_oidc10_app_client_unit.py)
- [tests/unit/test_cognito_oidc10_login_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_auth_idp_cognito/tests/unit/test_cognito_oidc10_login_unit.py)
- [tests/unit/test_cognito_login_contract_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_auth_idp_cognito/tests/unit/test_cognito_login_contract_unit.py)

Run the full offline package suite from the `pkgs/` directory with `uv run --package swarmauri_auth_idp_cognito --directory standards/swarmauri_auth_idp_cognito pytest`. The contract tests in `tests/unit/test_cognito_login_contract_unit.py` use fake HTTP clients and locally signed ID tokens; they verify the request/response contract only, not live Cognito interoperability.

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_auth_idp_cognito` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_auth_idp_cognito/swarmauri_auth_idp_cognito/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_auth_idp_cognito` provides aWS Cognito OAuth 2.0 / OAuth 2.1 / OIDC 1.0 identity provider implementations for Swarmauri; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_auth_idp_cognito`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_auth_idp_cognito/swarmauri_auth_idp_cognito/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_auth_idp_cognito` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_auth_idp_cognito/swarmauri_auth_idp_cognito/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_auth_idp_cognito/pyproject.toml) provide the supporting context for `swarmauri_auth_idp_cognito`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_auth_idp_cognito](https://pypi.org/project/swarmauri_auth_idp_cognito/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

To contribute to swarmauri-sdk, review the
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md),
including development workflow, testing, and coding standards.

### Development Setup

Work from the `pkgs/standards/swarmauri_auth_idp_cognito` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_auth_idp_cognito` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_auth_idp_cognito` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_auth_idp_cognito/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_auth_idp_cognito` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_auth_idp_cognito` source version is `0.11.0.dev4`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_auth_idp_cognito/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_auth_idp_cognito/NOTICE) for attribution.
<!-- readme-standards:end notices -->

