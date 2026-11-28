# swarmauri_transport_https_unicast

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_transport_https_unicast</strong></p>
<p align="center">Policy-bound HTTPS unicast transport for Swarmauri.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_transport_https_unicast/"><img alt="pypi: swarmauri_transport_https_unicast" src="https://img.shields.io/pypi/v/swarmauri_transport_https_unicast?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_https_unicast/pyproject.toml"><img alt="Source version: 0.11.0" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_https_unicast/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_https_unicast/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_https_unicast/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_https_unicast/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_https_unicast/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_transport_https_unicast/"><img alt="Monthly PyPI downloads: swarmauri_transport_https_unicast" src="https://img.shields.io/pypi/dm/swarmauri_transport_https_unicast?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_https_unicast/README.md"><img alt="README hits: swarmauri_transport_https_unicast" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/40-standards/swarmauri_transport_https_unicast/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_https_unicast/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_https_unicast/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_transport_https_unicast` provides a policy-bound HTTPS client
transport that composes HTTPX with Swarmauri TLS 1.3 cipher policy, X.509
certificate verification, HTTP signature headers, bearer-token forwarding, and
JWS body signing or verification.

### Why This Package

`swarmauri_transport_https_unicast` isolates this responsibility: Policy-bound HTTPS unicast transport for Swarmauri. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_https_unicast/swarmauri_transport_https_unicast/__init__.py) exposes `HttpsSecurityPolicy`, `HttpsTransportEvidence`, `HttpsUnicastTransport`, `http_signature`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_transport_https_unicast` when your integration needs policy-bound HTTPS unicast transport for Swarmauri. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Advertises HTTPS-over-TLS unicast transport capabilities through
  `TransportBase`.
- Uses HTTPX for concrete HTTPS request dispatch.
- Applies bearer tokens, `HttpSigMiddleware`-compatible HMAC headers, and JWS
  request-body signatures.
- Verifies response-body JWS payloads before returning transport results.
- Exposes X.509 preflight verification through `X509VerifyService`.
- Publishes TLS 1.3 cipher-suite policy metadata through `Tls13CipherSuite`.

### Non-Goals

`swarmauri_transport_https_unicast` owns policy-bound HTTPS unicast transport for Swarmauri. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_https_unicast/pyproject.toml) declares runtime dependencies including `httpx`, `swarmauri-core`, `swarmauri-base`, `swarmauri-certs-x509verify`, `swarmauri-cipher-suite-tls13`, `swarmauri-middleware-httpsig`, `swarmauri-signing-jws`. Read the example’s inputs and service requirements before execution.

### Installation

With `uv`:

```bash
uv add swarmauri_transport_https_unicast
```

With `pip`:

```bash
pip install swarmauri_transport_https_unicast
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_transport_https_unicast
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_transport_https_unicast
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_transport_https_unicast
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_https_unicast/docs/readme/quick_start.py).

```python
import asyncio

from swarmauri_transport_https_unicast import (
    HttpsSecurityPolicy,
    HttpsUnicastTransport,
)


async def main() -> None:
    body = b'{"order_id":"ord_1001"}'
    jws_key = {
        "kind": "raw",
        "key": b"transport-demo-secret-32-bytes!!",
        "kid": "body.1",
    }
    policy = HttpsSecurityPolicy(
        bearer_token="jwt-or-other-bearer-token",
        http_signature_secret="shared-secret",
        request_jws_key=jws_key,
        request_jws_kid="body.1",
        response_jws_key=jws_key,
    )
    transport = HttpsUnicastTransport(
        base_url="https://127.0.0.1:8443",
        verify="/path/to/trust-anchor.pem",
        security_policy=policy,
        require_response_jws=True,
    )

    async with transport.client():
        status, headers, response_body = await transport.request(
            "POST", "/secure/orders", body=body
        )

    print(status, headers["content-type"], response_body)
    print(transport.last_evidence)


asyncio.run(main())
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_transport_https_unicast` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_https_unicast/docs/readme/usage.py).

```python
import asyncio

from swarmauri_transport_https_unicast import (
    HttpsSecurityPolicy,
    HttpsUnicastTransport,
)


async def main() -> None:
    body = b'{"order_id":"ord_1001"}'
    jws_key = {
        "kind": "raw",
        "key": b"transport-demo-secret-32-bytes!!",
        "kid": "body.1",
    }
    policy = HttpsSecurityPolicy(
        bearer_token="jwt-or-other-bearer-token",
        http_signature_secret="shared-secret",
        request_jws_key=jws_key,
        request_jws_kid="body.1",
        response_jws_key=jws_key,
    )
    transport = HttpsUnicastTransport(
        base_url="https://127.0.0.1:8443",
        verify="/path/to/trust-anchor.pem",
        security_policy=policy,
        require_response_jws=True,
    )

    async with transport.client():
        status, headers, response_body = await transport.request(
            "POST", "/secure/orders", body=body
        )

    print(status, headers["content-type"], response_body)
    print(transport.last_evidence)


asyncio.run(main())
```
<!-- readme-standards:end example.usage -->

Expected output for a service that returns `application/json` and body
`b'{"ok":true}'`:

```text
200 application/json b'{"ok":true}'
HttpsTransportEvidence(status_code=200, response_jws_verified=True, certificate_valid=None, certificate_subject=None, cipher_suite='tls13', cipher_alg='TLS_AES_256_GCM_SHA384')
```

Use `verify_certificate()` when a service has a PEM certificate or chain that
should be validated against explicit trust roots before making transport calls.
Use `allowed_tls_cipher()` on server instrumentation to confirm the negotiated
TLS cipher is within the Swarmauri TLS 1.3 policy.

### Configuration

Configure `swarmauri_transport_https_unicast` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_https_unicast/swarmauri_transport_https_unicast/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_https_unicast/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_transport_https_unicast` source raises `NotImplementedError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_transport_https_unicast` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `HttpsSecurityPolicy`, `HttpsTransportEvidence`, `HttpsUnicastTransport`, `http_signature`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_transport_https_unicast` is located in `standards` and owns policy-bound HTTPS unicast transport for Swarmauri. Source-declared APIs include `HttpsSecurityPolicy`, `HttpsTransportEvidence`, `HttpsUnicastTransport`, `http_signature`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_https_unicast/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_transport_https_unicast`.

Source-declared exports or types: `HttpsSecurityPolicy`, `HttpsTransportEvidence`, `HttpsUnicastTransport`, `http_signature`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_https_unicast/swarmauri_transport_https_unicast/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.transports` → `HttpsUnicastTransport` → `swarmauri_transport_https_unicast:HttpsUnicastTransport`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_transport_https_unicast` are `httpx`, `swarmauri-core`, `swarmauri-base`, `swarmauri-certs-x509verify`, `swarmauri-cipher-suite-tls13`, `swarmauri-middleware-httpsig`, `swarmauri-signing-jws`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_https_unicast/swarmauri_transport_https_unicast/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_transport_https_unicast` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_transport_https_unicast`, use the source-declared public interfaces (`HttpsSecurityPolicy`, `HttpsTransportEvidence`, `HttpsUnicastTransport`, `http_signature`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_transport_https_unicast` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_https_unicast/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_transport_https_unicast`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_https_unicast/swarmauri_transport_https_unicast/__init__.py). The `swarmauri_transport_https_unicast` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_transport_https_unicast` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_transport_https_unicast` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/example/test_readme_import.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_https_unicast/tests/example/test_readme_import.py)
- [tests/unit/test_https_unicast_transport.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_https_unicast/tests/unit/test_https_unicast_transport.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_transport_https_unicast` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_https_unicast/swarmauri_transport_https_unicast/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_transport_https_unicast` provides policy-bound HTTPS unicast transport for Swarmauri; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_transport_https_unicast`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_https_unicast/swarmauri_transport_https_unicast/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_transport_https_unicast` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_https_unicast/swarmauri_transport_https_unicast/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_https_unicast/pyproject.toml) provide the supporting context for `swarmauri_transport_https_unicast`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.
- [swarmauri_certs_x509verify](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_certs_x509verify/README.md): X.509 certificate verification service for Swarmauri
- [swarmauri_cipher_suite_tls13](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_cipher_suite_tls13/README.md): TLS 1.3 cipher suite policy for Swarmauri
- [swarmauri_middleware_httpsig](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_middleware_httpsig/README.md): HTTP signature verification middleware for Swarmauri
- [swarmauri_signing_jws](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_jws/README.md): Composite JWS signer/verifier for Swarmauri

### Project Links

<!-- readme-standards:begin project-links -->
- [Documentation](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/40-standards/swarmauri_transport_https_unicast#readme)
- [Homepage](https://github.com/swarmauri/swarmauri-sdk)
- [Source](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/40-standards/swarmauri_transport_https_unicast)
- [pypi: swarmauri_transport_https_unicast](https://pypi.org/project/swarmauri_transport_https_unicast/)
<!-- readme-standards:end project-links -->

- Source:
  <https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/40-standards/swarmauri_transport_https_unicast>
- Issues: <https://github.com/swarmauri/swarmauri-sdk/issues>

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_transport_https_unicast`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/40-standards/swarmauri_transport_https_unicast` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_transport_https_unicast` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_transport_https_unicast` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_https_unicast/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_transport_https_unicast` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_transport_https_unicast` source version is `0.11.0`.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_https_unicast/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_https_unicast/NOTICE) for attribution.
<!-- readme-standards:end notices -->
