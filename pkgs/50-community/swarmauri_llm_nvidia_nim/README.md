# swarmauri_llm_nvidia_nim

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_llm_nvidia_nim</strong></p>
<p align="center">Swarmauri chat and tool-calling adapters for NVIDIA NIM OpenAI-compatible deployments.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_llm_nvidia_nim/"><img alt="pypi: swarmauri_llm_nvidia_nim" src="https://img.shields.io/pypi/v/swarmauri_llm_nvidia_nim?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_nvidia_nim/pyproject.toml"><img alt="Source version: 0.11.0.dev3" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev3&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_nvidia_nim/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_nvidia_nim/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_nvidia_nim/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_nvidia_nim/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_nvidia_nim/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_llm_nvidia_nim/"><img alt="Monthly PyPI downloads: swarmauri_llm_nvidia_nim" src="https://img.shields.io/pypi/dm/swarmauri_llm_nvidia_nim?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_nvidia_nim/README.md"><img alt="README hits: swarmauri_llm_nvidia_nim" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/50-community/swarmauri_llm_nvidia_nim/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_nvidia_nim/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_nvidia_nim/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_llm_nvidia_nim` connects Swarmauri conversations and toolkits to an NVIDIA NIM for LLMs deployment.

### Why This Package

`swarmauri_llm_nvidia_nim` isolates this responsibility: Swarmauri chat and tool-calling adapters for NVIDIA NIM OpenAI-compatible deployments. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_nvidia_nim/swarmauri_llm_nvidia_nim/_client.py) exposes `NvidiaNIMChatRetryPolicy`, `NvidiaNIMModel`, `NvidiaNIMToolModel`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_llm_nvidia_nim` when your integration needs swarmauri chat and tool-calling adapters for NVIDIA NIM OpenAI-compatible deployments. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- OpenAI-compatible chat completions through `NvidiaNIMModel`.
- Tool calling through `NvidiaNIMToolModel`.
- Synchronous, asynchronous, incremental streaming, and batch workflows inherited from Swarmauri's shared transports.
- Optional discovery from the deployment's `/v1/models` endpoint.
- Configurable deployment base URL for local, private, and managed NIM endpoints.
- Persistent, injectable Swarmauri HTTP clients with conservative rate-limit retries.

### Non-Goals

`swarmauri_llm_nvidia_nim` owns swarmauri chat and tool-calling adapters for NVIDIA NIM OpenAI-compatible deployments. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_nvidia_nim/pyproject.toml) declares runtime dependencies including `swarmauri-base`, `swarmauri-core`, `swarmauri-standard`, `swarmauri-transport-httpx`, `swarmauri-transport-retry`. Read the example’s inputs and service requirements before execution.

### Installation

```bash
uv add swarmauri_llm_nvidia_nim
```

```bash
pip install swarmauri_llm_nvidia_nim
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_llm_nvidia_nim
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_llm_nvidia_nim
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_llm_nvidia_nim
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_nvidia_nim/docs/readme/quick_start.py).

```python
from swarmauri_llm_nvidia_nim import NvidiaNIMModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation(
    messages=[HumanMessage(content="What is accelerated computing?")]
)
model = NvidiaNIMModel(
    base_url="http://localhost:8000",
    name="meta/llama-3.1-8b-instruct",
)
model.predict(conversation)
print(conversation.get_last().content)
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_llm_nvidia_nim` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_nvidia_nim/docs/readme/usage.py).

```python
from swarmauri_llm_nvidia_nim import NvidiaNIMModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation(
    messages=[HumanMessage(content="What is accelerated computing?")]
)
model = NvidiaNIMModel(
    base_url="http://localhost:8000",
    name="meta/llama-3.1-8b-instruct",
)
model.predict(conversation)
print(conversation.get_last().content)
```
<!-- readme-standards:end example.usage -->

Pass `api_key` when the deployment requires bearer authentication. Set `discover_models=True` to populate `allowed_models` from the running deployment. For tool workflows, instantiate `NvidiaNIMToolModel` and pass a Swarmauri `Toolkit` to `predict`, `apredict`, `stream`, or `astream`.

Pass an `IHttpClient` as `http_client` to integrate a custom transport or to test without network access. Pass an `IHttpRetryPolicy` as `retry_policy` to replace the default policy, which retries safe reads and rate-limited chat submissions without replaying failed POST requests for generic server errors.

See the [NVIDIA NIM LLM API reference](https://docs.nvidia.com/nim/large-language-models/latest/reference/api-reference.html) for deployment and model-specific capability details.

### Configuration

Configure `swarmauri_llm_nvidia_nim` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_nvidia_nim/swarmauri_llm_nvidia_nim/_client.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_nvidia_nim/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_llm_nvidia_nim` source does not establish a package-wide exception hierarchy. Preserve errors from its declared dependencies and validate inputs using the specific public contract in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_nvidia_nim/swarmauri_llm_nvidia_nim/_client.py).

### Best Practices

Use the explicit `swarmauri_llm_nvidia_nim` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `NvidiaNIMChatRetryPolicy`, `NvidiaNIMModel`, `NvidiaNIMToolModel`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_llm_nvidia_nim` is located in `community` and owns swarmauri chat and tool-calling adapters for NVIDIA NIM OpenAI-compatible deployments. Source-declared APIs include `NvidiaNIMChatRetryPolicy`, `NvidiaNIMModel`, `NvidiaNIMToolModel`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_nvidia_nim/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_llm_nvidia_nim`.

Source-declared exports or types: `NvidiaNIMChatRetryPolicy`, `NvidiaNIMModel`, `NvidiaNIMToolModel`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_nvidia_nim/swarmauri_llm_nvidia_nim/_client.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.llms` → `NvidiaNIMModel` → `swarmauri_llm_nvidia_nim:NvidiaNIMModel`
- `swarmauri.tool_llms` → `NvidiaNIMToolModel` → `swarmauri_llm_nvidia_nim:NvidiaNIMToolModel`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_llm_nvidia_nim` are `swarmauri-base`, `swarmauri-core`, `swarmauri-standard`, `swarmauri-transport-httpx`, `swarmauri-transport-retry`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_nvidia_nim/swarmauri_llm_nvidia_nim/_client.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_llm_nvidia_nim` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_llm_nvidia_nim`, use the source-declared public interfaces (`NvidiaNIMChatRetryPolicy`, `NvidiaNIMModel`, `NvidiaNIMToolModel`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_llm_nvidia_nim` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_nvidia_nim/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_llm_nvidia_nim`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_nvidia_nim/swarmauri_llm_nvidia_nim/_client.py). The `swarmauri_llm_nvidia_nim` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_llm_nvidia_nim` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_llm_nvidia_nim` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/unit/test_nvidia_nim.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_nvidia_nim/tests/unit/test_nvidia_nim.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_llm_nvidia_nim` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_nvidia_nim/swarmauri_llm_nvidia_nim/_client.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_llm_nvidia_nim` provides swarmauri chat and tool-calling adapters for NVIDIA NIM OpenAI-compatible deployments; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_llm_nvidia_nim`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_nvidia_nim/swarmauri_llm_nvidia_nim/_client.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_llm_nvidia_nim` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_nvidia_nim/swarmauri_llm_nvidia_nim/_client.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_nvidia_nim/pyproject.toml) provide the supporting context for `swarmauri_llm_nvidia_nim`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.
- [swarmauri_transport_httpx](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_httpx/README.md): Synchronous, asynchronous, buffered, and streaming HTTPX transport for Swarmauri.
- [swarmauri_transport_retry](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_retry/README.md): Policy-driven synchronous, asynchronous, and streaming HTTP retries for Swarmauri clients.
- [swarmauri_standard](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/30-standard-kernel/swarmauri_standard/README.md): First-party Swarmauri standard components for agents, tools, parsers, vectors, model adapters, and composable intelligence workflows.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_llm_nvidia_nim](https://pypi.org/project/swarmauri_llm_nvidia_nim/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_llm_nvidia_nim`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/50-community/swarmauri_llm_nvidia_nim` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_llm_nvidia_nim` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_llm_nvidia_nim` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_nvidia_nim/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_llm_nvidia_nim` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_llm_nvidia_nim` source version is `0.11.0.dev3`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_nvidia_nim/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_nvidia_nim/NOTICE) for attribution.
<!-- readme-standards:end notices -->
