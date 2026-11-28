# swarmauri_llm_ai21

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_llm_ai21</strong></p>
<p align="center">Provider-specific Swarmauri import package for AI21 Studio Jamba chat completions with sync, async, streaming, batch, and usage workflows.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_llm_ai21/"><img alt="pypi: swarmauri_llm_ai21" src="https://img.shields.io/pypi/v/swarmauri_llm_ai21?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_ai21/pyproject.toml"><img alt="Source version: 0.11.0" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_ai21/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_ai21/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_ai21/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_ai21/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_ai21/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_llm_ai21/"><img alt="Monthly PyPI downloads: swarmauri_llm_ai21" src="https://img.shields.io/pypi/dm/swarmauri_llm_ai21?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_ai21/README.md"><img alt="README hits: swarmauri_llm_ai21" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/50-community/swarmauri_llm_ai21/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_ai21/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_ai21/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_llm_ai21` provides the `AI21StudioModel` import path for Swarmauri applications that use AI21 Studio Jamba chat models. The package re-exports the maintained implementation from `swarmauri_standard`, giving projects a provider-specific dependency while preserving Swarmauri conversation, message, usage, streaming, and batch workflows.

### Why This Package

Use this package when you want to install only the AI21-facing LLM provider surface for a Swarmauri application. `AI21StudioModel` formats Swarmauri conversations for AI21 Studio chat completions, sends bearer-token authenticated HTTP requests, supports sync and async calls, streams token deltas, records usage data when available, and keeps model selection inside the Swarmauri `LLMBase` interface.

### When to Use

Choose `swarmauri_llm_ai21` when your integration needs provider-specific Swarmauri import package for AI21 Studio Jamba chat completions with sync, async, streaming, batch, and usage workflows. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Provider-specific import: `from swarmauri_llm_ai21 import AI21StudioModel`.
- Swarmauri `Conversation`, `HumanMessage`, `SystemMessage`, and `AgentMessage` integration.
- Sync `predict()` and async `apredict()` chat completion calls.
- Sync `stream()` and async `astream()` token streaming.
- Sync `batch()` and async `abatch()` helpers for multiple conversations.
- Usage metadata mapping to Swarmauri `UsageData` when provider usage data is returned.
- Retry handling for rate-limit and overloaded-provider status codes.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

### Non-Goals

`swarmauri_llm_ai21` owns provider-specific Swarmauri import package for AI21 Studio Jamba chat completions with sync, async, streaming, batch, and usage workflows. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

- An AI21 Studio account and API key.
- Network access to `api.ai21.com`.
- Swarmauri conversations built from Swarmauri message classes.

### Installation

Install with `uv`:

```bash
uv add swarmauri_llm_ai21
```

Install with `pip`:

```bash
pip install swarmauri_llm_ai21
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_llm_ai21
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_llm_ai21
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_llm_ai21
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_ai21/docs/readme/quick_start.py).

```python
import os

from swarmauri_llm_ai21 import AI21StudioModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage
from swarmauri_standard.messages.SystemMessage import SystemMessage

conversation = Conversation()
conversation.add_message(
    SystemMessage(content="Answer with concise technical prose.")
)
conversation.add_message(
    HumanMessage(content="What is a Swarmauri component?")
)

model = AI21StudioModel(
    api_key=os.environ["AI21STUDIO_API_KEY"],
    name="jamba-mini",
)
result = model.predict(
    conversation=conversation, temperature=0.3, max_tokens=256
)

print(result.get_last().content)
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_llm_ai21` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_ai21/docs/readme/usage.py).

```python
import os

from swarmauri_llm_ai21 import AI21StudioModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage
from swarmauri_standard.messages.SystemMessage import SystemMessage

conversation = Conversation()
conversation.add_message(
    SystemMessage(content="Answer with concise technical prose.")
)
conversation.add_message(
    HumanMessage(content="What is a Swarmauri component?")
)

model = AI21StudioModel(
    api_key=os.environ["AI21STUDIO_API_KEY"],
    name="jamba-mini",
)
result = model.predict(
    conversation=conversation, temperature=0.3, max_tokens=256
)

print(result.get_last().content)
```
<!-- readme-standards:end example.usage -->

Run a single chat completion:


Stream a response:

```python
import os

from swarmauri_llm_ai21 import AI21StudioModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(HumanMessage(content="Write a short release note."))

model = AI21StudioModel(api_key=os.environ["AI21STUDIO_API_KEY"])

for token in model.stream(conversation=conversation, max_tokens=160):
    print(token, end="")
```

Use the async API:

```python
import os
import asyncio

from swarmauri_llm_ai21 import AI21StudioModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage


async def main() -> None:
    conversation = Conversation()
    conversation.add_message(HumanMessage(content="Summarize AI21 Jamba in one line."))

    model = AI21StudioModel(api_key=os.environ["AI21STUDIO_API_KEY"])
    result = await model.apredict(conversation=conversation)

    print(result.get_last().content)


asyncio.run(main())
```

### Configuration

Configure `swarmauri_llm_ai21` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_ai21/swarmauri_llm_ai21/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_ai21/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_llm_ai21` source does not establish a package-wide exception hierarchy. Preserve errors from its declared dependencies and validate inputs using the specific public contract in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_ai21/swarmauri_llm_ai21/__init__.py).

### Best Practices

- Read the API key from environment variables or a secret manager.
- Set `name` explicitly so deployments do not change behavior when defaults change.
- Use async methods for high-concurrency applications.
- Keep prompts and system messages in Swarmauri `Conversation` objects for provider portability.
- Capture `UsageData` for cost and latency monitoring where provider responses include token usage.

---

## Package Boundary

### What It Owns

`swarmauri_llm_ai21` is located in `community` and owns provider-specific Swarmauri import package for AI21 Studio Jamba chat completions with sync, async, streaming, batch, and usage workflows. Source-declared APIs include `AI21StudioModel`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_ai21/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_llm_ai21`.

Source-declared exports or types: `AI21StudioModel`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_ai21/swarmauri_llm_ai21/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.llms` → `AI21StudioModel` → `swarmauri_llm_ai21.AI21StudioModel:AI21StudioModel`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_llm_ai21` are `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_ai21/swarmauri_llm_ai21/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_llm_ai21` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_llm_ai21`, use the source-declared public interfaces (`AI21StudioModel`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_llm_ai21` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_ai21/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_llm_ai21`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_ai21/swarmauri_llm_ai21/__init__.py). The `swarmauri_llm_ai21` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_llm_ai21` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_llm_ai21` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/i9n/test_AI21StudioModel_i9n.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_ai21/tests/i9n/test_AI21StudioModel_i9n.py)
- [tests/unit/test_AI21StudioModel_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_ai21/tests/unit/test_AI21StudioModel_unit.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_llm_ai21` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_ai21/swarmauri_llm_ai21/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Q: Which AI21 API does this adapter call?**

A: The adapter posts to `https://api.ai21.com/studio/v1/chat/completions`, AI21 Studio's chat completions endpoint used by Jamba chat models.

**Q: Which model names are configured?**

A: The current allowed model list is `jamba-large`, `jamba-mini`, `jamba-large-1.7`, and `jamba-mini-1.7`. The default model name is `jamba-large`.

**Q: Does this package contain a separate AI21 implementation?**

A: No. It re-exports `AI21StudioModel` from `swarmauri_standard.llms.AI21StudioModel` so applications can depend on the provider package while using the shared implementation.

**Q: What credential is required?**

A: Pass an AI21 Studio API key with `AI21StudioModel(api_key="...")`. The repository tests look for `AI21STUDIO_API_KEY` when running live provider checks.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_llm_ai21`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_ai21/swarmauri_llm_ai21/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_llm_ai21` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_ai21/swarmauri_llm_ai21/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_ai21/pyproject.toml) provide the supporting context for `swarmauri_llm_ai21`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

LLM provider packages:

- [swarmauri_llm_anthropic](https://pypi.org/project/swarmauri_llm_anthropic/)
- [swarmauri_llm_cerebras](https://pypi.org/project/swarmauri_llm_cerebras/)
- [swarmauri_llm_cohere](https://pypi.org/project/swarmauri_llm_cohere/)
- [swarmauri_llm_gemini](https://pypi.org/project/swarmauri_llm_gemini/)
- [swarmauri_llm_groq](https://pypi.org/project/swarmauri_llm_groq/)
- [swarmauri_llm_mistral](https://pypi.org/project/swarmauri_llm_mistral/)
- [swarmauri_llm_openai](https://pypi.org/project/swarmauri_llm_openai/)

Foundational packages:

- [swarmauri_core](https://pypi.org/project/swarmauri_core/) defines core interfaces.
- [swarmauri_base](https://pypi.org/project/swarmauri_base/) provides base component classes.
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/) contains the shared `AI21StudioModel` implementation.
- [swarmauri](https://pypi.org/project/swarmauri/) provides namespace imports and plugin discovery.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_llm_ai21](https://pypi.org/project/swarmauri_llm_ai21/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_llm_ai21`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/50-community/swarmauri_llm_ai21` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_llm_ai21` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_llm_ai21` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_ai21/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_llm_ai21` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_llm_ai21` source version is `0.11.0`.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_ai21/LICENSE).
<!-- readme-standards:end license -->

Apache-2.0

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_ai21/NOTICE) for attribution.
<!-- readme-standards:end notices -->
