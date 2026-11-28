# swarmauri_llm_cloudflare

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_llm_cloudflare</strong></p>
<p align="center">Swarmauri chat and tool-calling adapters for Cloudflare Workers AI.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_llm_cloudflare/"><img alt="pypi: swarmauri_llm_cloudflare" src="https://img.shields.io/pypi/v/swarmauri_llm_cloudflare?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_cloudflare/pyproject.toml"><img alt="Source version: 0.11.0" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_cloudflare/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_cloudflare/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_cloudflare/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_cloudflare/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_cloudflare/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_llm_cloudflare/"><img alt="Monthly PyPI downloads: swarmauri_llm_cloudflare" src="https://img.shields.io/pypi/dm/swarmauri_llm_cloudflare?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_cloudflare/README.md"><img alt="README hits: swarmauri_llm_cloudflare" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/50-community/swarmauri_llm_cloudflare/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_cloudflare/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_cloudflare/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_llm_cloudflare` connects Swarmauri conversations and toolkits to Cloudflare Workers AI's account-scoped REST API.

### Why This Package

`swarmauri_llm_cloudflare` isolates this responsibility: Swarmauri chat and tool-calling adapters for Cloudflare Workers AI. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_cloudflare/swarmauri_llm_cloudflare/_client.py) exposes `CloudflareChatRetryPolicy`, `CloudflareWorkersAIModel`, `CloudflareWorkersAIToolModel`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_llm_cloudflare` when your integration needs swarmauri chat and tool-calling adapters for Cloudflare Workers AI. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- OpenAI-compatible chat completions through `CloudflareWorkersAIModel`.
- Tool calling through `CloudflareWorkersAIToolModel` for models that advertise tool support.
- Synchronous, asynchronous, incremental streaming, and batch workflows.
- Optional discovery from Cloudflare's model-search endpoint.
- Explicit account ID and API-token configuration.
- Persistent, injectable Swarmauri HTTP clients with conservative rate-limit retries.

### Non-Goals

`swarmauri_llm_cloudflare` owns swarmauri chat and tool-calling adapters for Cloudflare Workers AI. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_cloudflare/pyproject.toml) declares runtime dependencies including `swarmauri-base`, `swarmauri-core`, `swarmauri-standard`, `swarmauri-transport-httpx`, `swarmauri-transport-retry`. Read the example’s inputs and service requirements before execution.

### Installation

```bash
uv add swarmauri_llm_cloudflare
```

```bash
pip install swarmauri_llm_cloudflare
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_llm_cloudflare
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_llm_cloudflare
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_llm_cloudflare
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_cloudflare/docs/readme/quick_start.py).

```python
import os

from swarmauri_llm_cloudflare import CloudflareWorkersAIModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation(
    messages=[HumanMessage(content="Explain edge inference.")]
)
model = CloudflareWorkersAIModel(
    account_id=os.environ["CLOUDFLARE_ACCOUNT_ID"],
    api_key=os.environ["CLOUDFLARE_API_TOKEN"],
    name="@cf/meta/llama-3.3-70b-instruct-fp8-fast",
)
model.predict(conversation)
print(conversation.get_last().content)
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_llm_cloudflare` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_cloudflare/docs/readme/usage.py).

```python
import os

from swarmauri_llm_cloudflare import CloudflareWorkersAIModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation(
    messages=[HumanMessage(content="Explain edge inference.")]
)
model = CloudflareWorkersAIModel(
    account_id=os.environ["CLOUDFLARE_ACCOUNT_ID"],
    api_key=os.environ["CLOUDFLARE_API_TOKEN"],
    name="@cf/meta/llama-3.3-70b-instruct-fp8-fast",
)
model.predict(conversation)
print(conversation.get_last().content)
```
<!-- readme-standards:end example.usage -->

Set `discover_models=True` to query the current Workers AI model catalog. For tools, instantiate `CloudflareWorkersAIToolModel` with a tool-capable model and pass a Swarmauri `Toolkit`.

Pass an `IHttpClient` as `http_client` to integrate a custom transport or to test without network access. Pass an `IHttpRetryPolicy` as `retry_policy` to replace the default policy, which retries safe reads and rate-limited chat submissions without replaying failed POST requests for generic server errors.

See the [Cloudflare Workers AI REST guide](https://developers.cloudflare.com/workers-ai/get-started/rest-api/) and [model-search API](https://developers.cloudflare.com/api/resources/ai/subresources/models/methods/list/) for account setup and current model details.

### Configuration

Configure `swarmauri_llm_cloudflare` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_cloudflare/swarmauri_llm_cloudflare/_client.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_cloudflare/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_llm_cloudflare` source does not establish a package-wide exception hierarchy. Preserve errors from its declared dependencies and validate inputs using the specific public contract in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_cloudflare/swarmauri_llm_cloudflare/_client.py).

### Best Practices

Use the explicit `swarmauri_llm_cloudflare` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `CloudflareChatRetryPolicy`, `CloudflareWorkersAIModel`, `CloudflareWorkersAIToolModel`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_llm_cloudflare` is located in `community` and owns swarmauri chat and tool-calling adapters for Cloudflare Workers AI. Source-declared APIs include `CloudflareChatRetryPolicy`, `CloudflareWorkersAIModel`, `CloudflareWorkersAIToolModel`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_cloudflare/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_llm_cloudflare`.

Source-declared exports or types: `CloudflareChatRetryPolicy`, `CloudflareWorkersAIModel`, `CloudflareWorkersAIToolModel`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_cloudflare/swarmauri_llm_cloudflare/_client.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.llms` → `CloudflareWorkersAIModel` → `swarmauri_llm_cloudflare:CloudflareWorkersAIModel`
- `swarmauri.tool_llms` → `CloudflareWorkersAIToolModel` → `swarmauri_llm_cloudflare:CloudflareWorkersAIToolModel`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_llm_cloudflare` are `swarmauri-base`, `swarmauri-core`, `swarmauri-standard`, `swarmauri-transport-httpx`, `swarmauri-transport-retry`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_cloudflare/swarmauri_llm_cloudflare/_client.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_llm_cloudflare` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_llm_cloudflare`, use the source-declared public interfaces (`CloudflareChatRetryPolicy`, `CloudflareWorkersAIModel`, `CloudflareWorkersAIToolModel`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_llm_cloudflare` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_cloudflare/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_llm_cloudflare`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_cloudflare/swarmauri_llm_cloudflare/_client.py). The `swarmauri_llm_cloudflare` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_llm_cloudflare` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_llm_cloudflare` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/unit/test_cloudflare.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_cloudflare/tests/unit/test_cloudflare.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_llm_cloudflare` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_cloudflare/swarmauri_llm_cloudflare/_client.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_llm_cloudflare` provides swarmauri chat and tool-calling adapters for Cloudflare Workers AI; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_llm_cloudflare`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_cloudflare/swarmauri_llm_cloudflare/_client.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_llm_cloudflare` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_cloudflare/swarmauri_llm_cloudflare/_client.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_cloudflare/pyproject.toml) provide the supporting context for `swarmauri_llm_cloudflare`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.
- [swarmauri_transport_httpx](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_httpx/README.md): Synchronous, asynchronous, buffered, and streaming HTTPX transport for Swarmauri.
- [swarmauri_transport_retry](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_transport_retry/README.md): Policy-driven synchronous, asynchronous, and streaming HTTP retries for Swarmauri clients.
- [swarmauri_standard](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/30-standard-kernel/swarmauri_standard/README.md): First-party Swarmauri standard components for agents, tools, parsers, vectors, model adapters, and composable intelligence workflows.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_llm_cloudflare](https://pypi.org/project/swarmauri_llm_cloudflare/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_llm_cloudflare`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/50-community/swarmauri_llm_cloudflare` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_llm_cloudflare` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_llm_cloudflare` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_cloudflare/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_llm_cloudflare` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_llm_cloudflare` source version is `0.11.0`.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_cloudflare/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_cloudflare/NOTICE) for attribution.
<!-- readme-standards:end notices -->
