# swarmauri_delegation_attenuating

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_delegation_attenuating</strong></p>
<p align="center">Delegate task authority with live ancestry checks.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_delegation_attenuating/"><img alt="pypi: swarmauri_delegation_attenuating unpublished" src="https://img.shields.io/static/v1?label=pypi&amp;message=swarmauri_delegation_attenuating%20unpublished&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_delegation_attenuating/pyproject.toml"><img alt="Source version: 0.1.1" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.1.1&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_delegation_attenuating/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_delegation_attenuating/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_delegation_attenuating/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_delegation_attenuating/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_delegation_attenuating/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_delegation_attenuating/"><img alt="pypi downloads: swarmauri_delegation_attenuating: unpublished" src="https://img.shields.io/static/v1?label=pypi%20downloads&amp;message=swarmauri_delegation_attenuating%3A%20unpublished&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_delegation_attenuating/README.md"><img alt="README hits: swarmauri_delegation_attenuating" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/standards/swarmauri_delegation_attenuating/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_delegation_attenuating/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_delegation_attenuating/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

[![Downloads](https://img.shields.io/pypi/dm/swarmauri_delegation_attenuating)](https://pepy.tech/project/swarmauri_delegation_attenuating)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_delegation_attenuating.svg)](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_delegation_attenuating)
[![Python](https://img.shields.io/pypi/pyversions/swarmauri_delegation_attenuating)](https://pypi.org/project/swarmauri_delegation_attenuating)
[![License](https://img.shields.io/pypi/l/swarmauri_delegation_attenuating)](LICENSE)
[![Version](https://img.shields.io/pypi/v/swarmauri_delegation_attenuating?label=swarmauri_delegation_attenuating&color=green)](https://pypi.org/project/swarmauri_delegation_attenuating)

Interchangeable delegations component for the composable execution framework.

### Why This Package

`swarmauri_delegation_attenuating` isolates this responsibility: Delegate task authority with live ancestry checks. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_delegation_attenuating/swarmauri_delegation_attenuating/__init__.py) exposes `AttenuatingDelegationService`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_delegation_attenuating` when your integration needs delegate task authority with live ancestry checks. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Export `AttenuatingDelegationService` with SDK interface/base-class inheritance and entry-point discovery.
- Keep user authority, workload identity, lifecycle and delivery dependencies explicit.
- Reuse existing service registries, transports, checkpoints and token providers.
- Support Python 3.10, 3.11, 3.12, 3.13 and 3.14.

### Non-Goals

`swarmauri_delegation_attenuating` owns delegate task authority with live ancestry checks. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_delegation_attenuating/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`. Read the example’s inputs and service requirements before execution.

### Installation

Install the package with its declared dependencies. The composable APIs require swarmauri_core 0.11.0.dev8 or newer and swarmauri_base 0.11.0.dev13 or newer within the declared version bounds.

```sh
uv pip install ./pkgs/standards/swarmauri_delegation_attenuating
pip install ./pkgs/standards/swarmauri_delegation_attenuating
```

#### uv

<!-- readme-standards:begin installation.uv -->
`swarmauri_delegation_attenuating` is not declared published. From the source checkout:

```bash
uv pip install .
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
`swarmauri_delegation_attenuating` is not declared published. From the source checkout:

```bash
python -m pip install .
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
`swarmauri_delegation_attenuating` is not declared published. From a separate Poetry project, replace the path with your checkout:

```bash
poetry add /path/to/swarmauri_delegation_attenuating
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_delegation_attenuating/docs/readme/quick_start.py).

```python
import importlib

package = importlib.import_module("swarmauri_delegation_attenuating")
assert package.__name__ == "swarmauri_delegation_attenuating"
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

This quick start is explicitly an import smoke check for `swarmauri_delegation_attenuating`. It confirms that the documented namespace loads; it does not demonstrate or certify a complete application workflow. The detailed source and retained usage guidance below describe the integration boundary.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_delegation_attenuating/docs/readme/usage.py).

```python
import importlib

package = importlib.import_module("swarmauri_delegation_attenuating")
assert package.__name__ == "swarmauri_delegation_attenuating"
```
<!-- readme-standards:end example.usage -->

The following is composition code. Injected dependency names are host configuration, not bundled mock providers. Async statements run inside an async function.

```python
from swarmauri_delegation_attenuating import AttenuatingDelegationService

service = AttenuatingDelegationService(
    grants=grant_store, tasks=task_store, policy=permission_policy,
    tokens=token_service, kid=signing_key_id, issuer=issuer,
    edges=frozenset({("agent:A", "agent:B")}),
)
# Trusted broker operations: authenticate callers before passing identities.
root = service.root(task_id, "agent:A", permissions, remaining_depth=1)
child = service.delegate(root.grant_id, "agent:A", "agent:B", permissions)
credential = await service.credential(
    child.grant_id, "agent:A", "agent:B", permissions[0]
)
service.revoke(root.grant_id)
# Later admission rejects the child even if its JWT has not expired.
```

See [the complete architecture and deployment guide](../../../docs/examples/composable-execution/README.md) for concrete local commands, live OIDC integration, HTTP hosting, lifecycle semantics and failure recovery.

### Configuration

Configure `swarmauri_delegation_attenuating` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_delegation_attenuating/swarmauri_delegation_attenuating/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_delegation_attenuating/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_delegation_attenuating` source raises `PermissionError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_delegation_attenuating` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `AttenuatingDelegationService`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_delegation_attenuating` is located in `standards` and owns delegate task authority with live ancestry checks. Source-declared APIs include `AttenuatingDelegationService`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_delegation_attenuating/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_delegation_attenuating`.

Source-declared exports or types: `AttenuatingDelegationService`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_delegation_attenuating/swarmauri_delegation_attenuating/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.delegations` → `AttenuatingDelegationService` → `swarmauri_delegation_attenuating:AttenuatingDelegationService`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_delegation_attenuating` are `swarmauri-core`, `swarmauri-base`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_delegation_attenuating/swarmauri_delegation_attenuating/__init__.py).

### Protocol Consumers

Direct consumers in this checkout’s package manifests include `swarmauri_workflow_documentassistant`. These edges describe declared dependencies, not protocol-conformance evidence.

### Extensions

For `swarmauri_delegation_attenuating`, use the source-declared public interfaces (`AttenuatingDelegationService`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_delegation_attenuating` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_delegation_attenuating/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_delegation_attenuating`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_delegation_attenuating/swarmauri_delegation_attenuating/__init__.py). The `swarmauri_delegation_attenuating` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_delegation_attenuating` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

From `pkgs/`, with the workspace dependencies installed:

```sh
uv run --package swarmauri_delegation_attenuating --directory standards/swarmauri_delegation_attenuating pytest
uv run --package swarmauri_delegation_attenuating --directory standards/swarmauri_delegation_attenuating ruff check .
```

Tests use real signing and stores where applicable; scripted models are explicitly identified fixtures. No live provider interoperability is claimed by offline tests.

### Certification Status

No external certification is asserted for `swarmauri_delegation_attenuating` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_delegation_attenuating/swarmauri_delegation_attenuating/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_delegation_attenuating` provides delegate task authority with live ancestry checks; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_delegation_attenuating`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_delegation_attenuating/swarmauri_delegation_attenuating/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_delegation_attenuating` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_delegation_attenuating/swarmauri_delegation_attenuating/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_delegation_attenuating/pyproject.toml) provide the supporting context for `swarmauri_delegation_attenuating`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.

### Project Links

<!-- readme-standards:begin project-links -->
- [Repository](https://github.com/swarmauri/swarmauri-sdk)
- [pypi: swarmauri_delegation_attenuating](https://pypi.org/project/swarmauri_delegation_attenuating/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the repository [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/AGENTS.md).

### Development Setup

Work from the `pkgs/standards/swarmauri_delegation_attenuating` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_delegation_attenuating` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_delegation_attenuating` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_delegation_attenuating/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_delegation_attenuating` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_delegation_attenuating` source version is `0.1.1`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_delegation_attenuating/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_delegation_attenuating/NOTICE) for attribution.
<!-- readme-standards:end notices -->
