# swarmauri_core

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_core</strong></p>
<p align="center">Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_core/"><img alt="pypi: swarmauri_core" src="https://img.shields.io/pypi/v/swarmauri_core"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/core/pyproject.toml"><img alt="Source version: 0.11.0.dev8" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev8&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/core/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/core/pyproject.toml"><img alt="Layer: core" src="https://img.shields.io/static/v1?label=Layer&amp;message=core&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/core/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/core/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/core/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_core/"><img alt="Monthly PyPI downloads: swarmauri_core" src="https://img.shields.io/pypi/dm/swarmauri_core"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/core/README.md"><img alt="README hits: swarmauri_core" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/core/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/core/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/core/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_core`: Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.

### Why This Package

`swarmauri_core` keeps component contracts separate from implementations. Package authors can depend on stable interfaces without pulling in every base class, provider adapter, model package, or runtime integration.

### When to Use

Use `swarmauri_core` when you are designing or implementing a Swarmauri-compatible component and need the interface contract. Use `swarmauri_base` when you also need reusable base-class behavior, serialization helpers, and component registration. Use `swarmauri_standard` when you want ready-to-use implementations.

### Features

The package is intentionally implementation-light. It defines contracts, protocol shapes, enums, and shared types so implementation packages can interoperate without depending on each other directly.

Major interface families include:

- Agents and agent APIs: `IAgent`, conversation, parser, retrieval, toolkit, and vector-store agent mixins.
- LLM and multimodal prediction: text LLMs, tool LLMs, OCR, STT, TTS, and VLM interfaces.
- Documents and parsing: document contracts, parser contracts, chunkers, conversations, prompts, and prompt templates.
- Retrieval and vectors: vector, matrix, tensor, metric, similarity, vector-store comparator, deprecated distance compatibility contracts, vector store, and document store contracts.
- Security and trust: crypto, MRE crypto, cipher suites, signing, proof-of-possession, token services, key providers, certificates, and XMP embedding.
- Runtime infrastructure: middleware, transports, storage adapters, publishers, rate limits, tracing, state, service registries, and pipelines.
- Business systems: billing provider interfaces for customers, payments, invoices, subscriptions, refunds, payouts, risk, reporting, webhooks, and marketplace flows.

- Stable abstract interfaces for Swarmauri component packages.
- Shared types for crypto, signing, key management, transports, billing, and proof-of-possession workflows.
- Zero runtime dependencies.
- Interface-first design for packages that later inherit reusable behavior from `swarmauri_base`.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

### Non-Goals

`swarmauri_core` owns core interface contracts and shared types for Swarmauri composable intelligence infrastructure components. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/core/pyproject.toml) declares no direct runtime dependencies. Read the example’s inputs and service requirements before execution.

### Installation

Install with `uv`:

```bash
uv add swarmauri_core
```

Install with `pip`:

```bash
pip install swarmauri_core
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_core
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_core
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_core
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/core/docs/readme/quick_start.py).

```python
import asyncio
from typing import Any, Optional

from swarmauri_core.agents.IAgent import IAgent
from swarmauri_core.messages.IMessage import IMessage


class MinimalAgent(IAgent):
    def exec(
        self,
        input_data: Optional[Any] = None,
        llm_kwargs: Optional[dict] = None,
    ) -> Any:
        return {"input": input_data, "kwargs": llm_kwargs or {}}

    async def aexec(
        self,
        input_str: Optional[str | IMessage] = "",
        llm_kwargs: Optional[dict] = None,
    ) -> Any:
        return self.exec(input_str, llm_kwargs)

    def batch(
        self,
        inputs: list[str | IMessage],
        llm_kwargs: Optional[dict] = None,
    ) -> list[Any]:
        return [self.exec(item, llm_kwargs) for item in inputs]

    async def abatch(
        self,
        inputs: list[str | IMessage],
        llm_kwargs: Optional[dict] = None,
    ) -> list[Any]:
        return await asyncio.gather(
            *(self.aexec(item, llm_kwargs) for item in inputs)
        )
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_core` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/core/docs/readme/usage.py).

```python
import asyncio
from typing import Any, Optional

from swarmauri_core.agents.IAgent import IAgent
from swarmauri_core.messages.IMessage import IMessage


class MinimalAgent(IAgent):
    def exec(
        self,
        input_data: Optional[Any] = None,
        llm_kwargs: Optional[dict] = None,
    ) -> Any:
        return {"input": input_data, "kwargs": llm_kwargs or {}}

    async def aexec(
        self,
        input_str: Optional[str | IMessage] = "",
        llm_kwargs: Optional[dict] = None,
    ) -> Any:
        return self.exec(input_str, llm_kwargs)

    def batch(
        self,
        inputs: list[str | IMessage],
        llm_kwargs: Optional[dict] = None,
    ) -> list[Any]:
        return [self.exec(item, llm_kwargs) for item in inputs]

    async def abatch(
        self,
        inputs: list[str | IMessage],
        llm_kwargs: Optional[dict] = None,
    ) -> list[Any]:
        return await asyncio.gather(
            *(self.aexec(item, llm_kwargs) for item in inputs)
        )
```
<!-- readme-standards:end example.usage -->

Use `swarmauri_core` when defining a new implementation package or validating that a class satisfies a public Swarmauri contract.


Implement a parser contract:

```python
from pathlib import Path

from swarmauri_core.documents.IDocument import IDocument
from swarmauri_core.parsers.IParser import IParser


class PlainTextParser(IParser):
    def parse(self, data: str | bytes | Path) -> list[IDocument]:
        raise NotImplementedError("Return concrete Document instances here.")
```

Implement a storage or retrieval contract in a concrete package, then expose the class through `swarmauri_base` and the public `swarmauri` namespace when appropriate.

### Configuration

Configure `swarmauri_core` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/core/swarmauri_core/billing/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/core/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_core` source raises `AttributeError`, `IntegrityError`, `KeyError`, `NotImplementedError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_core` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `IAgentCommands`, `IAgentRouterCRUD`, `IExportConf`, `IAgent`, `IAgentCompaction`, `IAgentConversation`, `IAgentParser`, `IAgentRetrieve`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_core` is located in `core` and owns core interface contracts and shared types for Swarmauri composable intelligence infrastructure components. Source-declared APIs include `IAgentCommands`, `IAgentRouterCRUD`, `IExportConf`, `IAgent`, `IAgentCompaction`, `IAgentConversation`, `IAgentParser`, `IAgentRetrieve`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/core/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_core`.

Source-declared exports or types: `IAgentCommands`, `IAgentRouterCRUD`, `IExportConf`, `IAgent`, `IAgentCompaction`, `IAgentConversation`, `IAgentParser`, `IAgentRetrieve`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/core/swarmauri_core/billing/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
This package declares no command-line, GUI, or plugin entry points in its manifest.
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_core` are empty in the manifest. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/core/swarmauri_core/billing/__init__.py).

### Protocol Consumers

Direct consumers in this checkout’s package manifests include `swarmauri_base`, `swarmauri_billing_adyen`, `swarmauri_billing_authorize_net`, `swarmauri_billing_braintree`, `swarmauri_billing_paypal`, `swarmauri_billing_paystack`, `swarmauri_billing_razorpay`, `swarmauri_billing_square`, `swarmauri_certs_acme`, `swarmauri_certs_azure`, `swarmauri_certs_cfssl`, `swarmauri_certs_csronly`, `swarmauri_certs_ocspverify`, `swarmauri_certservice_aws_kms`, `swarmauri_certservice_gcpkms`. These edges describe declared dependencies, not protocol-conformance evidence.

### Extensions

For `swarmauri_core`, use the source-declared public interfaces (`IAgentCommands`, `IAgentRouterCRUD`, `IExportConf`, `IAgent`, `IAgentCompaction`, `IAgentConversation`, `IAgentParser`, `IAgentRetrieve`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_core` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/core/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_core`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/core/swarmauri_core/billing/__init__.py). The `swarmauri_core` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_core` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_core` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/unit/test_execution_contracts.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/core/tests/unit/test_execution_contracts.py)
- [tests/unit/test_git_filter.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/core/tests/unit/test_git_filter.py)
- [tests/unit/test_keys_module.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/core/tests/unit/test_keys_module.py)
- [tests/unit/test_storage_adapter_interface.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/core/tests/unit/test_storage_adapter_interface.py)
- [tests/unit/test_text_to_speech_interface.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/core/tests/unit/test_text_to_speech_interface.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_core` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/core/swarmauri_core/billing/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Q: What belongs in swarmauri_core?**

A: Interface contracts, protocol shapes, enums, and shared types for Swarmauri component families.

### How

**Q: How does this package relate to swarmauri_base?**

A: `swarmauri_core` defines interfaces. `swarmauri_base` implements reusable base classes and serialization behavior on top of those interfaces.

### When

**Q: Should application developers instantiate classes from this package?**

A: Usually no. Most application code uses concrete implementations from `swarmauri_standard`, community packages, or provider-specific packages. Component authors use `swarmauri_core` to implement the correct contract.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/core/swarmauri_core/billing/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/core/pyproject.toml) provide the supporting context for `swarmauri_core`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

Foundational packages:

- [swarmauri](https://pypi.org/project/swarmauri/) provides the namespace importer and plugin discovery layer.
- [swarmauri_base](https://pypi.org/project/swarmauri_base/) provides reusable base classes built on these interfaces.
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/) provides first-party implementations for common component kinds.

Packages built around specific core component kinds:

- [swarmauri_signing_ed25519](https://pypi.org/project/swarmauri_signing_ed25519/) implements signing interfaces.
- [swarmauri_crypto_composite](https://pypi.org/project/swarmauri_crypto_composite/) composes crypto providers behind the crypto interface.
- [swarmauri_keyprovider_inmemory](https://pypi.org/project/swarmauri_keyprovider_inmemory/) implements key provider contracts.
- [swarmauri_transport_stdio](https://pypi.org/project/swarmauri_transport_stdio/) implements transport contracts.
- [swarmauri_storage_memory](https://pypi.org/project/swarmauri_storage_memory/) implements storage adapter contracts.
- [swarmauri_middleware_jsonrpc](https://pypi.org/project/swarmauri_middleware_jsonrpc/) implements middleware contracts.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_core](https://pypi.org/project/swarmauri_core/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

When adding or changing a core interface, keep the contract narrow, update downstream base classes where needed, add focused tests, and follow the [Swarmauri SDK contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md).

### Development Setup

Work from the `pkgs/core` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

**Composable execution contracts**

The `executions`, `tasks`, `workflows`, `permissions`, `delegation` and
`invocations` namespaces define driver-neutral lifecycle, admitted task
authority and invocation contracts. Existing service registries, task
assignment, transports and token interfaces remain in use.
See the [composition guide](../../docs/examples/composable-execution/README.md).

`swarmauri_core` provides the interface contracts for the Swarmauri SDK. It is the package component authors use when they need stable abstract interfaces for agents, tools, LLMs, parsers, vector stores, cryptography, signing, key providers, transports, middleware, billing, storage, XMP, and other composable intelligence infrastructure components.

**Component Author Workflow**

1. Choose the closest interface from `swarmauri_core`.
2. Implement domain behavior in a package-specific class.
3. Add reusable serialization and registration behavior with `swarmauri_base` when the implementation should become a Swarmauri component.
4. Publish or register the implementation package through the appropriate `swarmauri.<kind>` entry point or namespace mapping.
5. Document installation and usage in the implementation package README.

**Run checkpoints and tool steps**

`swarmauri_core.run_stores` defines `IRunStore`, `RunCheckpoint`, and
`RunConflictError`. Checkpoints have an opaque text payload and a revision
guarded by an atomic save. `swarmauri_core.tool_llms.IToolStepModel` is the
opt-in contract for proposing tool calls and formatting their results.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_core` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/core/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_core` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_core` source version is `0.11.0.dev8`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/core/LICENSE).
<!-- readme-standards:end license -->

Apache-2.0

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/core/NOTICE) for attribution.
<!-- readme-standards:end notices -->
