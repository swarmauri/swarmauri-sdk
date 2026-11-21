# swarmauri_certs_x509

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_certs_x509</strong></p>
<p align="center">X.509 certificate service for Swarmauri</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_certs_x509/"><img alt="pypi: swarmauri_certs_x509" src="https://img.shields.io/pypi/v/swarmauri_certs_x509"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_x509/pyproject.toml"><img alt="Source version: 0.11.0.dev4" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev4&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_x509/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_x509/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_x509/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_x509/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_x509/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_certs_x509/"><img alt="Monthly PyPI downloads: swarmauri_certs_x509" src="https://img.shields.io/pypi/dm/swarmauri_certs_x509"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_x509/README.md"><img alt="README hits: swarmauri_certs_x509" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/standards/swarmauri_certs_x509/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_x509/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_x509/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

X.509 certificate service plugin for Swarmauri using the `cryptography` library.

### Why This Package

`swarmauri_certs_x509` isolates this responsibility: X.509 certificate service for Swarmauri. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_x509/swarmauri_certs_x509/__init__.py) exposes `X509CertService`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_certs_x509` when your integration needs x.509 certificate service for Swarmauri. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Create standards-compliant CSRs
- Issue self-signed leaf or CA certificates
- Sign CSRs with an external CA key
- Verify certificate chains with optional intermediates
- Parse certificates to extract subject, issuer, validity, and extension metadata

### Non-Goals

`swarmauri_certs_x509` owns x.509 certificate service for Swarmauri. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_x509/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `swarmauri-keyprovider-local`, `swarmauri-keyprovider-inmemory`, `cryptography`. Read the example’s inputs and service requirements before execution.

### Installation

The package bundles both the local and in-memory key providers, so no
additional extras are required for the example below. Optional PKCS#11
support can be enabled when you need to integrate with hardware modules.

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_certs_x509
```
<!-- readme-standards:end installation.uv -->

```bash
uv pip install swarmauri_certs_x509
# or add to pyproject.toml and install dependencies
uv add swarmauri_certs_x509
uv sync
# enable PKCS#11
uv pip install 'swarmauri_certs_x509[pkcs11]'
```

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_certs_x509
```
<!-- readme-standards:end installation.pip -->

```bash
pip install swarmauri_certs_x509
# with PKCS#11 support
pip install 'swarmauri_certs_x509[pkcs11]'
```

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_certs_x509
```
<!-- readme-standards:end installation.poetry -->

```bash
poetry add swarmauri_certs_x509
# enable PKCS#11
poetry add swarmauri_certs_x509 --extras pkcs11
```

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_x509/docs/readme/quick_start.py).

```python
import asyncio
from swarmauri_certs_x509 import X509CertService
from swarmauri_keyprovider_local import LocalKeyProvider
from swarmauri_core.key_providers.types import KeySpec, KeyAlg, KeyClass
from swarmauri_core.crypto.types import KeyUse, ExportPolicy

svc = X509CertService()
kp = LocalKeyProvider()

spec = KeySpec(
    klass=KeyClass.asymmetric,
    alg=KeyAlg.ED25519,
    uses=(KeyUse.SIGN,),
    export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
)

ca_key = asyncio.run(kp.create_key(spec))
ca_cert = asyncio.run(svc.create_self_signed(ca_key, {"CN": "Example CA"}))

leaf_key = asyncio.run(kp.create_key(spec))
csr = asyncio.run(svc.create_csr(leaf_key, {"CN": "example.org"}))
leaf_cert = asyncio.run(svc.sign_cert(csr, ca_key, ca_cert=ca_cert))
result = asyncio.run(svc.verify_cert(leaf_cert, trust_roots=[ca_cert]))
assert result["valid"]
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_certs_x509` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_x509/docs/readme/usage.py).

```python
import asyncio
from swarmauri_certs_x509 import X509CertService
from swarmauri_keyprovider_local import LocalKeyProvider
from swarmauri_core.key_providers.types import KeySpec, KeyAlg, KeyClass
from swarmauri_core.crypto.types import KeyUse, ExportPolicy

svc = X509CertService()
kp = LocalKeyProvider()

spec = KeySpec(
    klass=KeyClass.asymmetric,
    alg=KeyAlg.ED25519,
    uses=(KeyUse.SIGN,),
    export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
)

ca_key = asyncio.run(kp.create_key(spec))
ca_cert = asyncio.run(svc.create_self_signed(ca_key, {"CN": "Example CA"}))

leaf_key = asyncio.run(kp.create_key(spec))
csr = asyncio.run(svc.create_csr(leaf_key, {"CN": "example.org"}))
leaf_cert = asyncio.run(svc.sign_cert(csr, ca_key, ca_cert=ca_cert))
result = asyncio.run(svc.verify_cert(leaf_cert, trust_roots=[ca_cert]))
assert result["valid"]
```
<!-- readme-standards:end example.usage -->

The example below uses ``LocalKeyProvider`` to create a certificate
authority (CA), issue a leaf certificate, and verify the chain.


**CMS/S/MIME certificate profile**

When preparing identities for CMS or S/MIME signing, include Email Protection
extended key usage and an email subject alternative name so that relying
parties can validate the certificate purpose.

```python
import asyncio
from swarmauri_core.crypto.types import KeyUse, ExportPolicy
from swarmauri_core.key_providers.types import KeyAlg, KeyClass, KeySpec
from swarmauri_certs_x509 import X509CertService
from swarmauri_keyprovider_local import LocalKeyProvider


async def issue_smime_identity():
    provider = LocalKeyProvider()
    svc = X509CertService()

    ca_spec = KeySpec(
        klass=KeyClass.asymmetric,
        alg=KeyAlg.ECDSA_P256_SHA256,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
    )
    ca_key = await provider.create_key(ca_spec)
    ca_cert = await svc.create_self_signed(
        ca_key,
        {"CN": "Demo CMS Root"},
        extensions={
            "basic_constraints": {"ca": True, "path_len": 0},
            "key_usage": {
                "digital_signature": True,
                "content_commitment": True,
                "key_cert_sign": True,
                "crl_sign": True,
            },
        },
    )

    leaf_spec = KeySpec(
        klass=KeyClass.asymmetric,
        alg=KeyAlg.ECDSA_P256_SHA256,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
    )
    leaf_key = await provider.create_key(leaf_spec)
    csr = await svc.create_csr(
        leaf_key,
        {"CN": "cms-signer.example", "emailAddress": "signer@example.org"},
        san={"email": ["signer@example.org"]},
    )
    leaf_cert = await svc.sign_cert(
        csr,
        ca_key,
        ca_cert=ca_cert,
        extensions={
            "basic_constraints": {"ca": False},
            "key_usage": {
                "digital_signature": True,
                "content_commitment": True,
            },
            "extended_key_usage": {"oids": ["emailProtection"]},
        },
    )

    return {
        "ca_cert": ca_cert,
        "leaf_cert": leaf_cert,
        "leaf_key_pem": leaf_key.material,
    }


bundle = asyncio.run(issue_smime_identity())
```

The `bundle` dictionary pairs neatly with ``swarmauri_signing_cms.CMSSigner`` by
supplying the `leaf_key_pem` together with the `leaf_cert` and `ca_cert`
entries as the PKCS#7 signing material.

### Configuration

Configure `swarmauri_certs_x509` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_x509/swarmauri_certs_x509/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_x509/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_certs_x509` source raises `TypeError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_certs_x509` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `X509CertService`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_certs_x509` is located in `standards` and owns x.509 certificate service for Swarmauri. Source-declared APIs include `X509CertService`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_x509/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_certs_x509`.

Source-declared exports or types: `X509CertService`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_x509/swarmauri_certs_x509/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `peagen.plugins.certs` → `x509` → `swarmauri_certs_x509:X509CertService`
- `swarmauri.certs` → `X509CertService` → `swarmauri_certs_x509:X509CertService`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_certs_x509` are `swarmauri-core`, `swarmauri-base`, `swarmauri-keyprovider-local`, `swarmauri-keyprovider-inmemory`, `cryptography`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_x509/swarmauri_certs_x509/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_certs_x509` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_certs_x509`, use the source-declared public interfaces (`X509CertService`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_certs_x509` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_x509/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_certs_x509`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_x509/swarmauri_certs_x509/__init__.py). The `swarmauri_certs_x509` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_certs_x509` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_certs_x509` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/example/test_usage_example.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_x509/tests/example/test_usage_example.py)
- [tests/functional/test_x509certservice_functional.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_x509/tests/functional/test_x509certservice_functional.py)
- [tests/perf/test_x509certservice_perf.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_x509/tests/perf/test_x509certservice_perf.py)
- [tests/unit/test_rfc2986_pkcs10.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_x509/tests/unit/test_rfc2986_pkcs10.py)
- [tests/unit/test_rfc5280_basic.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_x509/tests/unit/test_rfc5280_basic.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_certs_x509` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_x509/swarmauri_certs_x509/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_certs_x509` provides x.509 certificate service for Swarmauri; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_certs_x509`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_x509/swarmauri_certs_x509/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_certs_x509` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_x509/swarmauri_certs_x509/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_x509/pyproject.toml) provide the supporting context for `swarmauri_certs_x509`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.
- [swarmauri_keyprovider_inmemory](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_keyprovider_inmemory/README.md): In-memory key provider for Swarmauri
- [swarmauri_keyprovider_local](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_keyprovider_local/README.md): In-memory key provider for development and testing

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_certs_x509](https://pypi.org/project/swarmauri_certs_x509/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.

### Development Setup

Work from the `pkgs/standards/swarmauri_certs_x509` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

**RFC References**

- [RFC 2986](https://datatracker.ietf.org/doc/html/rfc2986) ? PKCS #10 Certification Request Syntax
- [RFC 5280](https://datatracker.ietf.org/doc/html/rfc5280) ? Internet X.509 Public Key Infrastructure Certificate and CRL Profile

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_certs_x509` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_x509/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_certs_x509` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_certs_x509` source version is `0.11.0.dev4`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_x509/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_certs_x509/NOTICE) for attribution.
<!-- readme-standards:end notices -->
