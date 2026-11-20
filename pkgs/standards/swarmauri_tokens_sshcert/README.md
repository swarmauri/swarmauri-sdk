# swarmauri_tokens_sshcert

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_tokens_sshcert</strong></p>
<p align="center">OpenSSH certificate token service for Swarmauri</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_tokens_sshcert/"><img alt="pypi: swarmauri_tokens_sshcert" src="https://img.shields.io/pypi/v/swarmauri_tokens_sshcert"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tokens_sshcert/pyproject.toml"><img alt="Source version: 0.11.0.dev3" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev3&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tokens_sshcert/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tokens_sshcert/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tokens_sshcert/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tokens_sshcert/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tokens_sshcert/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_tokens_sshcert/"><img alt="Monthly PyPI downloads: swarmauri_tokens_sshcert" src="https://img.shields.io/pypi/dm/swarmauri_tokens_sshcert"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tokens_sshcert/README.md"><img alt="README hits: swarmauri_tokens_sshcert" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/standards/swarmauri_tokens_sshcert/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tokens_sshcert/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tokens_sshcert/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

An OpenSSH certificate token service for the Swarmauri framework. This service
mints and verifies OpenSSH user and host certificates and exposes no JWKS
endpoints.

### Why This Package

`swarmauri_tokens_sshcert` isolates this responsibility: OpenSSH certificate token service for Swarmauri. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tokens_sshcert/swarmauri_tokens_sshcert/__init__.py) exposes `SshCertTokenService`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_tokens_sshcert` when your integration needs openSSH certificate token service for Swarmauri. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- `SshCertTokenService`: declared in swarmauri_tokens_sshcert/SshCertTokenService.py

### Non-Goals

`swarmauri_tokens_sshcert` owns openSSH certificate token service for Swarmauri. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tokens_sshcert/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`. Read the example’s inputs and service requirements before execution.

### Installation

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_tokens_sshcert
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_tokens_sshcert
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_tokens_sshcert
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tokens_sshcert/docs/readme/quick_start.py).

```python
import asyncio
import os
import subprocess
import tempfile
from typing import Iterable, Mapping

from swarmauri_tokens_sshcert import SshCertTokenService
from swarmauri_core.crypto.types import ExportPolicy, KeyRef, KeyType, KeyUse
from swarmauri_core.key_providers import IKeyProvider


def _generate_keypair() -> tuple[str, str]:
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "id")
        subprocess.run(
            ["ssh-keygen", "-t", "ed25519", "-N", "", "-f", path],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        priv = open(path, "r", encoding="utf-8").read()
        pub = open(path + ".pub", "r", encoding="utf-8").read()
    return priv, pub


class DummyKeyProvider(IKeyProvider):
    def __init__(self) -> None:
        self.priv, self.pub = _generate_keypair()
        self.kid = "ca"
        self.version = 1

    async def get_key(
        self,
        kid: str,
        version: int | None = None,
        *,
        include_secret: bool = False,
    ) -> KeyRef:
        material = self.priv if include_secret else None
        return KeyRef(
            kid=self.kid,
            version=self.version,
            type=KeyType.ED25519,
            uses=(KeyUse.SIGN, KeyUse.VERIFY),
            export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
            material=material,
            public=self.pub,
        )

    async def jwks(self, *, prefix_kids: str | None = None) -> dict:
        return {"keys": []}

    def supports(self) -> Mapping[str, Iterable[str]]:
        return {}


async def main() -> None:
    svc = SshCertTokenService(DummyKeyProvider(), ca_kid="ca")
    _, subj_pub = _generate_keypair()
    cert = await svc.mint(
        {"subject_pub": subj_pub, "principals": ["alice"], "key_id": "demo"},
        alg="ssh-ed25519",
    )
    info = await svc.verify(cert, audience="alice")
    print(info["key_id"])


if __name__ == "__main__":
    asyncio.run(main())
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_tokens_sshcert` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tokens_sshcert/docs/readme/usage.py).

```python
import asyncio
import os
import subprocess
import tempfile
from typing import Iterable, Mapping

from swarmauri_tokens_sshcert import SshCertTokenService
from swarmauri_core.crypto.types import ExportPolicy, KeyRef, KeyType, KeyUse
from swarmauri_core.key_providers import IKeyProvider


def _generate_keypair() -> tuple[str, str]:
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "id")
        subprocess.run(
            ["ssh-keygen", "-t", "ed25519", "-N", "", "-f", path],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        priv = open(path, "r", encoding="utf-8").read()
        pub = open(path + ".pub", "r", encoding="utf-8").read()
    return priv, pub


class DummyKeyProvider(IKeyProvider):
    def __init__(self) -> None:
        self.priv, self.pub = _generate_keypair()
        self.kid = "ca"
        self.version = 1

    async def get_key(
        self,
        kid: str,
        version: int | None = None,
        *,
        include_secret: bool = False,
    ) -> KeyRef:
        material = self.priv if include_secret else None
        return KeyRef(
            kid=self.kid,
            version=self.version,
            type=KeyType.ED25519,
            uses=(KeyUse.SIGN, KeyUse.VERIFY),
            export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
            material=material,
            public=self.pub,
        )

    async def jwks(self, *, prefix_kids: str | None = None) -> dict:
        return {"keys": []}

    def supports(self) -> Mapping[str, Iterable[str]]:
        return {}


async def main() -> None:
    svc = SshCertTokenService(DummyKeyProvider(), ca_kid="ca")
    _, subj_pub = _generate_keypair()
    cert = await svc.mint(
        {"subject_pub": subj_pub, "principals": ["alice"], "key_id": "demo"},
        alg="ssh-ed25519",
    )
    info = await svc.verify(cert, audience="alice")
    print(info["key_id"])


if __name__ == "__main__":
    asyncio.run(main())
```
<!-- readme-standards:end example.usage -->

`SshCertTokenService` uses the local `ssh-keygen` utility to mint and verify
OpenSSH certificates. A key provider supplies the certificate authority (CA)
key material used for signing. The typical workflow is:

1. implement or configure an `IKeyProvider` that returns your CA key
2. create the token service
3. mint a certificate for a subject public key
4. verify the certificate before trusting it


The example above mints a certificate for a generated key and verifies it for
the principal `alice`. The service requires the `ssh-keygen` command to be
available on the system path.

### Configuration

Configure `swarmauri_tokens_sshcert` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tokens_sshcert/swarmauri_tokens_sshcert/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tokens_sshcert/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_tokens_sshcert` source raises `RuntimeError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_tokens_sshcert` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `SshCertTokenService`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_tokens_sshcert` is located in `standards` and owns openSSH certificate token service for Swarmauri. Source-declared APIs include `SshCertTokenService`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tokens_sshcert/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_tokens_sshcert`.

Source-declared exports or types: `SshCertTokenService`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tokens_sshcert/swarmauri_tokens_sshcert/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `peagen.plugins.tokens` → `ssh-cert` → `swarmauri_tokens_sshcert:SshCertTokenService`
- `swarmauri.tokens` → `SshCertTokenService` → `swarmauri_tokens_sshcert:SshCertTokenService`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_tokens_sshcert` are `swarmauri-core`, `swarmauri-base`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tokens_sshcert/swarmauri_tokens_sshcert/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_tokens_sshcert` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_tokens_sshcert`, use the source-declared public interfaces (`SshCertTokenService`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_tokens_sshcert` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tokens_sshcert/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_tokens_sshcert`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tokens_sshcert/swarmauri_tokens_sshcert/__init__.py). The `swarmauri_tokens_sshcert` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_tokens_sshcert` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_tokens_sshcert` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/example/test_usage_example.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tokens_sshcert/tests/example/test_usage_example.py)
- [tests/functional/test_sshcerttokenservice_functional.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tokens_sshcert/tests/functional/test_sshcerttokenservice_functional.py)
- [tests/perf/test_sshcerttokenservice_perf.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tokens_sshcert/tests/perf/test_sshcerttokenservice_perf.py)
- [tests/unit/test_rfc4252_userauth.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tokens_sshcert/tests/unit/test_rfc4252_userauth.py)
- [tests/unit/test_rfc8709_ed25519.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tokens_sshcert/tests/unit/test_rfc8709_ed25519.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_tokens_sshcert` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tokens_sshcert/swarmauri_tokens_sshcert/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_tokens_sshcert` provides openSSH certificate token service for Swarmauri; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_tokens_sshcert`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tokens_sshcert/swarmauri_tokens_sshcert/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_tokens_sshcert` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tokens_sshcert/swarmauri_tokens_sshcert/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tokens_sshcert/pyproject.toml) provide the supporting context for `swarmauri_tokens_sshcert`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_tokens_sshcert](https://pypi.org/project/swarmauri_tokens_sshcert/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.

### Development Setup

Work from the `pkgs/standards/swarmauri_tokens_sshcert` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_tokens_sshcert` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_tokens_sshcert` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tokens_sshcert/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_tokens_sshcert` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_tokens_sshcert` source version is `0.11.0.dev3`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tokens_sshcert/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tokens_sshcert/NOTICE) for attribution.
<!-- readme-standards:end notices -->
