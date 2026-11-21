# swarmauri_transport_tls_unicast

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_transport_tls_unicast</strong></p>
<p align="center">TLS / mTLS unicast transport for Swarmauri.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_transport_tls_unicast/"><img alt="pypi: swarmauri_transport_tls_unicast" src="https://img.shields.io/pypi/v/swarmauri_transport_tls_unicast"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_transport_tls_unicast/pyproject.toml"><img alt="Source version: 0.11.0.dev4" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev4&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_transport_tls_unicast/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_transport_tls_unicast/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_transport_tls_unicast/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_transport_tls_unicast/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_transport_tls_unicast/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_transport_tls_unicast/"><img alt="Monthly PyPI downloads: swarmauri_transport_tls_unicast" src="https://img.shields.io/pypi/dm/swarmauri_transport_tls_unicast"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_transport_tls_unicast/README.md"><img alt="README hits: swarmauri_transport_tls_unicast" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/standards/swarmauri_transport_tls_unicast/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_transport_tls_unicast/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_transport_tls_unicast/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_transport_tls_unicast` implements TLS-secured unicast over asyncio streams through `TlsUnicastTransport`.

### Why This Package

Use one transport interface for TLS client/server lifecycles while explicitly supplying SSL contexts, server names, certificates, and trust roots.

### When to Use

Use it for a single-peer TLS stream connection. Require a trusted server certificate matching the client SNI name. Mutual TLS additionally needs a client certificate and server-side client-certificate validation.

### Features

- `TlsUnicastTransport`: TLS-secured unicast transport built on top of asyncio streams.

### Non-Goals

This package does not issue certificates, manage a CA, discover peers, or multiplex multiple concurrent accepted connections on one transport object. The stream example handles one accepted connection and closes it explicitly.

---

## Getting Started

### Prerequisites

Python and the dependencies declared in the manifest are required. The capability example needs no certificate files and performs no network handshake. The stream example requires `server.pem`, `server.key`, and a signing CA in `ca.pem`; the server certificate must cover `localhost`.

### Installation

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_transport_tls_unicast
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_transport_tls_unicast
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_transport_tls_unicast
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_transport_tls_unicast/docs/readme/quick_start.py).

```python
import ssl
from swarmauri_core.transports import Feature, SecurityMode
from swarmauri_transport_tls_unicast import TlsUnicastTransport

context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
transport = TlsUnicastTransport(context)
capabilities = transport.supports()
assert capabilities.security is SecurityMode.TLS
assert Feature.ENCRYPTED in capabilities.features
assert Feature.MUTUAL_AUTH not in capabilities.features
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The Quick Start assertions inspect the real transport capability object: TLS mode, encrypted streams, and no mutual-auth flag for the supplied context. The Usage example accepts a connection and asserts the exact `b"tls:hello"` response. A capability assertion alone does not verify a TLS handshake.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_transport_tls_unicast/docs/readme/usage.py).

```python
import asyncio
import os
import ssl
from swarmauri_transport_tls_unicast import TlsUnicastTransport


async def main():
    port = int(os.environ.get("TLS_EXAMPLE_PORT", "8443"))
    server_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    server_context.load_cert_chain("server.pem", "server.key")
    client_context = ssl.create_default_context(cafile="ca.pem")
    ready = asyncio.Event()
    transport = TlsUnicastTransport(server_context)

    async def serve():
        async with transport.server(host="127.0.0.1", port=port):
            ready.set()
            async for reader, writer in transport.accept():
                request = await transport.recv(timeout=5)
                await transport.send("peer", b"tls:" + request, timeout=5)
                writer.close()
                await writer.wait_closed()
                break

    async def request():
        await ready.wait()
        client = TlsUnicastTransport(client_context, sni="localhost")
        async with client.client(host="127.0.0.1", port=port):
            await client.send("server", b"hello", timeout=5)
            assert await client.recv(timeout=5) == b"tls:hello"

    await asyncio.gather(serve(), request())


asyncio.run(main())
```
<!-- readme-standards:end example.usage -->

### Configuration

Configure `swarmauri_transport_tls_unicast` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_transport_tls_unicast/swarmauri_transport_tls_unicast/tls_unicast.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_transport_tls_unicast/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_transport_tls_unicast` source raises `RuntimeError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_transport_tls_unicast` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `TlsUnicastTransport`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_transport_tls_unicast` is located in `standards` and owns tLS / mTLS unicast transport for Swarmauri. Source-declared APIs include `TlsUnicastTransport`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_transport_tls_unicast/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_transport_tls_unicast`.

Source-declared exports or types: `TlsUnicastTransport`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_transport_tls_unicast/swarmauri_transport_tls_unicast/tls_unicast.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
This package declares no command-line, GUI, or plugin entry points in its manifest.
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_transport_tls_unicast` are `swarmauri-base`, `swarmauri-core`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_transport_tls_unicast/swarmauri_transport_tls_unicast/tls_unicast.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_transport_tls_unicast` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_transport_tls_unicast`, use the source-declared public interfaces (`TlsUnicastTransport`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_transport_tls_unicast` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_transport_tls_unicast/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_transport_tls_unicast`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Keep certificate verification enabled. Supply trusted CA material and matching SNI; never replace the client context with an unverified context. The example binds loopback and bounds stream operations to five seconds. Client certificate authentication requires both peers to be configured for mTLS.

### Compatibility

This source version of `swarmauri_transport_tls_unicast` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

`tests/unit/test_readme_workflows.py` runs the maintained capability example and a real loopback TLS exchange with an ephemeral CA, trusted server certificate, and hostname verification. Set `TLS_EXAMPLE_PORT` to choose a port; the Usage example defaults to 8443. This test does not claim mutual-TLS coverage.

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_transport_tls_unicast` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_tls_unicast_transport.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_transport_tls_unicast/tests/test_tls_unicast_transport.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_transport_tls_unicast` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_transport_tls_unicast/swarmauri_transport_tls_unicast/tls_unicast.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_transport_tls_unicast` provides tLS / mTLS unicast transport for Swarmauri; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_transport_tls_unicast`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_transport_tls_unicast/swarmauri_transport_tls_unicast/tls_unicast.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_transport_tls_unicast` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_transport_tls_unicast/swarmauri_transport_tls_unicast/tls_unicast.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_transport_tls_unicast/pyproject.toml) provide the supporting context for `swarmauri_transport_tls_unicast`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_transport_tls_unicast](https://pypi.org/project/swarmauri_transport_tls_unicast/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_transport_tls_unicast`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/standards/swarmauri_transport_tls_unicast` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_transport_tls_unicast` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_transport_tls_unicast` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_transport_tls_unicast/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_transport_tls_unicast` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_transport_tls_unicast` source version is `0.11.0.dev4`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_transport_tls_unicast/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_transport_tls_unicast/NOTICE) for attribution.
<!-- readme-standards:end notices -->
