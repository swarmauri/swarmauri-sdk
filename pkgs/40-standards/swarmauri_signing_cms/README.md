# swarmauri_signing_cms

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_signing_cms</strong></p>
<p align="center">CMS signer stub registered on the Swarmauri SigningBase registry</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_signing_cms/"><img alt="pypi: swarmauri_signing_cms" src="https://img.shields.io/pypi/v/swarmauri_signing_cms?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_cms/pyproject.toml"><img alt="Source version: 0.11.0.dev3" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev3&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_cms/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_cms/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_cms/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_cms/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_cms/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_signing_cms/"><img alt="Monthly PyPI downloads: swarmauri_signing_cms" src="https://img.shields.io/pypi/dm/swarmauri_signing_cms?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_cms/README.md"><img alt="README hits: swarmauri_signing_cms" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/40-standards/swarmauri_signing_cms/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_cms/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_cms/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`CMSSigner` delivers production-ready
[Cryptographic Message Syntax (CMS)](https://www.rfc-editor.org/rfc/rfc5652)
and [S/MIME](https://www.rfc-editor.org/rfc/rfc8551) signing utilities for the
Swarmauri platform. The signer integrates with the common
`SigningBase` registry and works seamlessly with Swarmauri certificate
providers so that applications can create, distribute, and verify PKCS#7
signatures end-to-end.

### Why This Package

`swarmauri_signing_cms` isolates this responsibility: CMS signer stub registered on the Swarmauri SigningBase registry. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_cms/swarmauri_signing_cms/cms_signer.py) exposes `CMSSigner`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_signing_cms` when your integration needs cMS signer stub registered on the Swarmauri SigningBase registry. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Detached and attached PKCS#7 signatures with DER or PEM serialization
- S/MIME friendly defaults for email payloads
- Streaming, digest, and structured-envelope signing helpers
- Signature verification with certificate chain enforcement
- First-class interoperability with Swarmauri key providers and certificate
  authorities

### Non-Goals

`swarmauri_signing_cms` owns cMS signer stub registered on the Swarmauri SigningBase registry. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_cms/pyproject.toml) declares runtime dependencies including `swarmauri-base`, `swarmauri-core`, `cryptography`. Read the example’s inputs and service requirements before execution.

### Installation

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_signing_cms
```
<!-- readme-standards:end installation.uv -->

Add it to your managed project:

```bash
uv add swarmauri_signing_cms
```

Or install directly into the active environment:

```bash
uv pip install swarmauri_signing_cms
```

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_signing_cms
```
<!-- readme-standards:end installation.pip -->

```bash
pip install swarmauri_signing_cms
```

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_signing_cms
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_cms/docs/readme/quick_start.py).

```python
import asyncio
from swarmauri_core.crypto.types import KeyUse, ExportPolicy
from swarmauri_core.key_providers.types import KeyAlg, KeyClass, KeySpec
from swarmauri_certs_x509 import X509CertService
from swarmauri_keyprovider_local import LocalKeyProvider


async def build_smime_identity():
    key_provider = LocalKeyProvider()
    certs = X509CertService()

    ca_spec = KeySpec(
        klass=KeyClass.asymmetric,
        alg=KeyAlg.ECDSA_P256_SHA256,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        label="Example CMS CA",
    )
    ca_key = await key_provider.create_key(ca_spec)
    ca_cert = await certs.create_self_signed(
        ca_key,
        {"CN": "Example CMS Root", "O": "Example Org"},
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
        label="CMS Signer",
    )
    leaf_key = await key_provider.create_key(leaf_spec)
    csr = await certs.create_csr(
        leaf_key,
        {"CN": "cms-signer.example", "emailAddress": "signer@example.org"},
        san={"email": ["signer@example.org"]},
    )
    leaf_cert = await certs.sign_cert(
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

    cms_key_ref = {
        "kind": "pem",
        "private_key": leaf_key.material,
        "certificate": leaf_cert,
        "extra_certificates": [ca_cert],
    }
    trust_chain = [ca_cert]
    return cms_key_ref, trust_chain


cms_key_ref, trust_chain = asyncio.run(build_smime_identity())
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_signing_cms` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_cms/docs/readme/usage.py).

```python
import asyncio
from swarmauri_core.crypto.types import KeyUse, ExportPolicy
from swarmauri_core.key_providers.types import KeyAlg, KeyClass, KeySpec
from swarmauri_certs_x509 import X509CertService
from swarmauri_keyprovider_local import LocalKeyProvider


async def build_smime_identity():
    key_provider = LocalKeyProvider()
    certs = X509CertService()

    ca_spec = KeySpec(
        klass=KeyClass.asymmetric,
        alg=KeyAlg.ECDSA_P256_SHA256,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        label="Example CMS CA",
    )
    ca_key = await key_provider.create_key(ca_spec)
    ca_cert = await certs.create_self_signed(
        ca_key,
        {"CN": "Example CMS Root", "O": "Example Org"},
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
        label="CMS Signer",
    )
    leaf_key = await key_provider.create_key(leaf_spec)
    csr = await certs.create_csr(
        leaf_key,
        {"CN": "cms-signer.example", "emailAddress": "signer@example.org"},
        san={"email": ["signer@example.org"]},
    )
    leaf_cert = await certs.sign_cert(
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

    cms_key_ref = {
        "kind": "pem",
        "private_key": leaf_key.material,
        "certificate": leaf_cert,
        "extra_certificates": [ca_cert],
    }
    trust_chain = [ca_cert]
    return cms_key_ref, trust_chain


cms_key_ref, trust_chain = asyncio.run(build_smime_identity())
```
<!-- readme-standards:end example.usage -->

The snippets below illustrate how to bootstrap certificates, create CMS and
S/MIME signatures, and verify results with Swarmauri components.

**Bootstrapping CMS credentials**

Use `swarmauri_certs_x509` together with a key provider to issue a
CMS-capable signing certificate with the correct [email protection
Extended Key Usage](https://www.rfc-editor.org/rfc/rfc5280#section-4.2.1.12).


`cms_key_ref` can now be supplied to the `CMSSigner` for both CMS and S/MIME
operations. The returned `trust_chain` is useful when verifying signatures.

**Detached CMS signing & verification**

```python
import asyncio
from swarmauri_signing_cms import CMSSigner


async def sign_and_verify(message: bytes):
    signer = CMSSigner()
    signatures = await signer.sign_bytes(
        cms_key_ref,
        message,
        alg="SHA256",
        opts={"encoding": "der"},
    )

    ok = await signer.verify_bytes(
        message,
        signatures,
        opts={"trusted_certs": trust_chain},
    )
    return signatures[0].artifact, ok


artifact, verified = asyncio.run(sign_and_verify(b"important document"))
print(f"Signature length: {len(artifact)} bytes, verified={verified}")
```

`sign_bytes` produces a detached PKCS#7 signature suitable for archival or
transport alongside the original payload. Verification succeeds when at least
one signature chains back to a trusted certificate.

**S/MIME attached signing**

Attached S/MIME signatures encapsulate the message body and are typically
distributed using the `application/pkcs7-mime` content type.

```python
import asyncio
from email.message import EmailMessage
from email import policy
from swarmauri_signing_cms import CMSSigner


async def create_smime(message: EmailMessage):
    payload = message.as_bytes(policy=policy.SMTP)
    signer = CMSSigner()
    signature = await signer.sign_bytes(
        cms_key_ref,
        payload,
        opts={"attached": True, "encoding": "pem"},
    )
    verified = await signer.verify_bytes(
        payload,
        signature,
        opts={"trusted_certs": trust_chain},
    )
    return signature[0].artifact, verified


msg = EmailMessage()
msg["From"] = "signer@example.org"
msg["To"] = "recipient@example.net"
msg["Subject"] = "Quarterly Statement"
msg.set_content("Please review the attached statement.")

smime_bytes, ok = asyncio.run(create_smime(msg))
if ok:
    with open("statement.p7m", "wb") as fp:
        fp.write(smime_bytes)
```

The resulting `statement.p7m` file contains a fully formed S/MIME envelope that
can be delivered via email or downloaded from an API.

### Configuration

Configure `swarmauri_signing_cms` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_cms/swarmauri_signing_cms/cms_signer.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_cms/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_signing_cms` source raises `RuntimeError`, `TypeError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_signing_cms` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `CMSSigner`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_signing_cms` is located in `standards` and owns cMS signer stub registered on the Swarmauri SigningBase registry. Source-declared APIs include `CMSSigner`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_cms/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_signing_cms`.

Source-declared exports or types: `CMSSigner`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_cms/swarmauri_signing_cms/cms_signer.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
This package declares no command-line, GUI, or plugin entry points in its manifest.
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_signing_cms` are `swarmauri-base`, `swarmauri-core`, `cryptography`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_cms/swarmauri_signing_cms/cms_signer.py).

### Protocol Consumers

Direct consumers in this checkout’s package manifests include `MediaSigner`, `swarmauri_signing_pdf`. These edges describe declared dependencies, not protocol-conformance evidence.

### Extensions

For `swarmauri_signing_cms`, use the source-declared public interfaces (`CMSSigner`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_signing_cms` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_cms/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_signing_cms`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_cms/swarmauri_signing_cms/cms_signer.py). The `swarmauri_signing_cms` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_signing_cms` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_signing_cms` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_cms_signer.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_cms/tests/test_cms_signer.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_signing_cms` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_cms/swarmauri_signing_cms/cms_signer.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_signing_cms` provides cMS signer stub registered on the Swarmauri SigningBase registry; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_signing_cms`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_cms/swarmauri_signing_cms/cms_signer.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_signing_cms` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_cms/swarmauri_signing_cms/cms_signer.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_cms/pyproject.toml) provide the supporting context for `swarmauri_signing_cms`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.

### Project Links

<!-- readme-standards:begin project-links -->
- [Documentation](https://github.com/swarmauri/swarmauri-sdk/tree/main/pkgs/40-standards/swarmauri_signing_cms#readme)
- [Homepage](https://github.com/swarmauri/swarmauri-sdk)
- [Source](https://github.com/swarmauri/swarmauri-sdk/tree/main/pkgs/40-standards/swarmauri_signing_cms)
- [pypi: swarmauri_signing_cms](https://pypi.org/project/swarmauri_signing_cms/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Pull requests and issue reports are welcome! Please review the
[contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
before submitting changes.

### Development Setup

Work from the `pkgs/40-standards/swarmauri_signing_cms` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

**Example workflows**

The package ships ready-to-run demonstrations inside
`swarmauri_signing_cms/examples/cms_and_smime_examples.py`. They generate
ephemeral key material using the `cryptography` library so you can explore CMS
and S/MIME flows without external tooling.

**Prepare signing material**

```python
from swarmauri_signing_cms.examples.cms_and_smime_examples import build_ephemeral_identity

key_ref, trust_anchor = build_ephemeral_identity("demo.swarmauri")
```

`key_ref` is the structure expected by `CMSSigner`. It contains the PEM encoded
private key, end-entity certificate, and (optionally) a chain. The helper also
returns a PEM trust anchor that can be supplied during verification.

**Create a detached CMS signature**

```python
import asyncio
from swarmauri_signing_cms import CMSSigner
from swarmauri_signing_cms.examples.cms_and_smime_examples import (
    build_ephemeral_identity,
    cms_detached_signature,
)


async def main() -> None:
    key_ref, trust_anchor = build_ephemeral_identity("demo.swarmauri")
    signer = CMSSigner()
    signature = await cms_detached_signature(signer, key_ref, [trust_anchor])
    print("Signature mode:", signature.mode)
    print("Hash algorithm:", signature.alg)


if __name__ == "__main__":
    asyncio.run(main())
```

The helper signs raw bytes, verifies the result using the provided trust store,
and returns the resulting `Signature` instance. Detached artifacts are encoded
as DER by default, but you can pass `opts={"attached": False, "encoding": "pem"}`
when you need PEM output for downstream systems.

**Assemble an S/MIME message**

```python
import asyncio
from email import policy
from email.generator import BytesGenerator
from io import BytesIO

from swarmauri_signing_cms import CMSSigner
from swarmauri_signing_cms.examples.cms_and_smime_examples import (
    build_ephemeral_identity,
    smime_attached_message,
)


async def main() -> None:
    key_ref, trust_anchor = build_ephemeral_identity("demo.swarmauri")
    envelope = await smime_attached_message(CMSSigner(), key_ref, [trust_anchor])
    buffer = BytesIO()
    BytesGenerator(buffer, policy=policy.SMTP).flatten(envelope)
    print(buffer.getvalue().decode("utf-8"))


if __name__ == "__main__":
    asyncio.run(main())
```

`smime_attached_message` requests an attached CMS signature in PEM form
(`smime.p7s`) and wraps the payload inside a `multipart/signed` envelope. The
helper verifies the artifact against the provided trust anchor before returning
the message container.

**Inspect the CMS certificate chain**

```python
import asyncio
from swarmauri_signing_cms import CMSSigner
from swarmauri_signing_cms.examples.cms_and_smime_examples import (
    build_ephemeral_identity,
    cms_detached_signature,
    describe_certificate_chain,
)


async def describe() -> None:
    key_ref, trust_anchor = build_ephemeral_identity("demo.swarmauri")
    signature = await cms_detached_signature(CMSSigner(), key_ref, [trust_anchor])
    for subject in describe_certificate_chain(signature):
        print(subject)


asyncio.run(describe())
```

`Signature.cert_chain_der` contains DER-encoded certificates returned by the
signing routine. `describe_certificate_chain` converts those blobs back into
`cryptography.x509.Certificate` instances so you can display or persist the
chain.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_signing_cms` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_cms/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_signing_cms` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_signing_cms` source version is `0.11.0.dev3`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_cms/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_signing_cms/NOTICE) for attribution.
<!-- readme-standards:end notices -->
