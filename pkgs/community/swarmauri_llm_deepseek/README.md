# swarmauri_llm_deepseek

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_llm_deepseek</strong></p>
<p align="center">Provider-specific Swarmauri import package for DeepSeek OpenAI-compatible chat completions, reasoning models, streaming, async, and batch LLM workflows.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_llm_deepseek/"><img alt="pypi: swarmauri_llm_deepseek" src="https://img.shields.io/pypi/v/swarmauri_llm_deepseek"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_deepseek/pyproject.toml"><img alt="Source version: 0.11.0.dev3" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev3&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_deepseek/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_deepseek/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_deepseek/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_deepseek/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_deepseek/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_llm_deepseek/"><img alt="Monthly PyPI downloads: swarmauri_llm_deepseek" src="https://img.shields.io/pypi/dm/swarmauri_llm_deepseek"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_deepseek/README.md"><img alt="README hits: swarmauri_llm_deepseek" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/community/swarmauri_llm_deepseek/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_deepseek/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_deepseek/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_llm_deepseek` provides the provider-specific `DeepSeekModel`
import for Swarmauri applications that call DeepSeek's OpenAI-compatible chat
completion API. Install this package when a project should depend on the
DeepSeek adapter directly while keeping the runtime implementation aligned with
`swarmauri_standard`.

The adapter formats Swarmauri `Conversation` history as chat messages, sends
requests to DeepSeek chat completions, and appends the provider response as an
`AgentMessage`. It supports synchronous calls, asynchronous calls, streaming,
and simple batch workflows for assistants, coding agents, reasoning workflows,
and model-provider experiments.

DeepSeek's current API documentation describes an OpenAI-compatible chat API and
lists `deepseek-v4-flash` and `deepseek-v4-pro` as current model IDs. This
package currently defaults to the compatibility aliases `deepseek-chat` and
`deepseek-reasoner`, which DeepSeek documents as mapped compatibility model
names.

### Why This Package

- Keep DeepSeek-specific imports explicit in application dependencies.
- Use Swarmauri conversation and message primitives instead of hand-rolled
  request dictionaries throughout the application.
- Swap DeepSeek with other Swarmauri LLM provider packages while preserving the
  same high-level `predict`, `stream`, `apredict`, and `astream` workflows.
- Use DeepSeek reasoning and chat models through one Swarmauri adapter surface.

### When to Use

Choose `swarmauri_llm_deepseek` when your integration needs provider-specific Swarmauri import package for DeepSeek OpenAI-compatible chat completions, reasoning models, streaming, async, and batch LLM workflows. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Provider-specific `DeepSeekModel` import for Swarmauri applications.
- Synchronous chat completion through `predict`.
- Asynchronous chat completion through `apredict`.
- Token streaming through `stream` and `astream`.
- Batch helpers through `batch` and `abatch`.
- Configurable chat generation parameters including `temperature`,
  `max_tokens`, `top_p`, `stop`, `frequency_penalty`, and `presence_penalty`.
- Compatibility with Python 3.10, 3.11, 3.12, 3.13, and 3.14.

### Non-Goals

`swarmauri_llm_deepseek` owns provider-specific Swarmauri import package for DeepSeek OpenAI-compatible chat completions, reasoning models, streaming, async, and batch LLM workflows. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Create a DeepSeek API key in the DeepSeek platform and pass it to
`DeepSeekModel(api_key=...)`. The tests in this package look for
`DEEPSEEK_API_KEY` when running live provider checks.

### Installation

```bash
uv add swarmauri_llm_deepseek
```

```bash
pip install swarmauri_llm_deepseek
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_llm_deepseek
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_llm_deepseek
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_llm_deepseek
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_deepseek/docs/readme/quick_start.py).

```python
from swarmauri_llm_deepseek import DeepSeekModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(
    HumanMessage(content="Summarize why OpenAI-compatible APIs are useful.")
)

model = DeepSeekModel(api_key="DEEPSEEK_API_KEY")
result = model.predict(conversation=conversation, max_tokens=200)

print(result.get_last().content)
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_llm_deepseek` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_deepseek/docs/readme/usage.py).

```python
from swarmauri_llm_deepseek import DeepSeekModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(
    HumanMessage(content="Summarize why OpenAI-compatible APIs are useful.")
)

model = DeepSeekModel(api_key="DEEPSEEK_API_KEY")
result = model.predict(conversation=conversation, max_tokens=200)

print(result.get_last().content)
```
<!-- readme-standards:end example.usage -->

**Streaming**

```python
from swarmauri_llm_deepseek import DeepSeekModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(HumanMessage(content="Write a three-line release note."))

model = DeepSeekModel(api_key="DEEPSEEK_API_KEY")

for token in model.stream(conversation=conversation):
    print(token, end="")
```

**Async Prediction**

```python
import asyncio

from swarmauri_llm_deepseek import DeepSeekModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage


async def main() -> None:
    conversation = Conversation()
    conversation.add_message(HumanMessage(content="Explain agent memory in one paragraph."))

    model = DeepSeekModel(api_key="DEEPSEEK_API_KEY")
    result = await model.apredict(conversation=conversation)
    print(result.get_last().content)


asyncio.run(main())
```

### Configuration

Configure `swarmauri_llm_deepseek` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_deepseek/swarmauri_llm_deepseek/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_deepseek/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_llm_deepseek` source does not establish a package-wide exception hierarchy. Preserve errors from its declared dependencies and validate inputs using the specific public contract in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_deepseek/swarmauri_llm_deepseek/__init__.py).

### Best Practices

- Keep DeepSeek credentials in environment variables or a secrets manager.
- Confirm current model names and availability in the DeepSeek platform before
  production deployment.
- Use `deepseek-reasoner` only when the workflow benefits from reasoning-model
  behavior; the current adapter records the final answer content.
- Set explicit `max_tokens` and timeout expectations for long-running reasoning
  requests.

---

## Package Boundary

### What It Owns

`swarmauri_llm_deepseek` is located in `community` and owns provider-specific Swarmauri import package for DeepSeek OpenAI-compatible chat completions, reasoning models, streaming, async, and batch LLM workflows. Source-declared APIs include `DeepSeekModel`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_deepseek/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_llm_deepseek`.

Source-declared exports or types: `DeepSeekModel`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_deepseek/swarmauri_llm_deepseek/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.llms` → `DeepSeekModel` → `swarmauri_llm_deepseek.DeepSeekModel:DeepSeekModel`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_llm_deepseek` are `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_deepseek/swarmauri_llm_deepseek/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_llm_deepseek` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_llm_deepseek`, use the source-declared public interfaces (`DeepSeekModel`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_llm_deepseek` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_deepseek/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_llm_deepseek`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_deepseek/swarmauri_llm_deepseek/__init__.py). The `swarmauri_llm_deepseek` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_llm_deepseek` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_llm_deepseek` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/i9n/test_DeepSeekModel_i9n.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_deepseek/tests/i9n/test_DeepSeekModel_i9n.py)
- [tests/unit/test_DeepSeekModel_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_deepseek/tests/unit/test_DeepSeekModel_unit.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_llm_deepseek` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_deepseek/swarmauri_llm_deepseek/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**What does swarmauri_llm_deepseek install?**

It installs a provider package that exports `DeepSeekModel` from
`swarmauri_standard.llms.DeepSeekModel` and registers the same model entry point
for Swarmauri plugin discovery.

**Which DeepSeek endpoint does the adapter call?**

The implementation creates HTTP clients with the configured DeepSeek base URL
and posts to `/chat/completions` using DeepSeek's OpenAI-compatible chat
completion payload shape.

**Which models are available?**

The package default is `deepseek-chat`, with `deepseek-reasoner` also listed in
`allowed_models`. DeepSeek's public documentation now also lists
`deepseek-v4-flash` and `deepseek-v4-pro` as current model IDs, so production
deployments should verify model availability against the DeepSeek platform
before pinning a model name.

**Does the package expose DeepSeek reasoning content?**

The current Swarmauri adapter stores the assistant's final response content on
the conversation. DeepSeek-specific reasoning fields are not exposed as a
separate Swarmauri message property by this package.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_llm_deepseek`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_deepseek/swarmauri_llm_deepseek/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_llm_deepseek` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_deepseek/swarmauri_llm_deepseek/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_deepseek/pyproject.toml) provide the supporting context for `swarmauri_llm_deepseek`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_llm_ai21](https://pypi.org/project/swarmauri_llm_ai21/)
- [swarmauri_llm_anthropic](https://pypi.org/project/swarmauri_llm_anthropic/)
- [swarmauri_llm_cerebras](https://pypi.org/project/swarmauri_llm_cerebras/)
- [swarmauri_llm_deepinfra](https://pypi.org/project/swarmauri_llm_deepinfra/)
- [swarmauri_llm_groq](https://pypi.org/project/swarmauri_llm_groq/)
- [swarmauri_llm_mistral](https://pypi.org/project/swarmauri_llm_mistral/)
- [swarmauri_llm_openai](https://pypi.org/project/swarmauri_llm_openai/)

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_llm_deepseek](https://pypi.org/project/swarmauri_llm_deepseek/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_llm_deepseek`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/community/swarmauri_llm_deepseek` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

**Foundational Swarmauri Packages**

- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)
- [swarmauri](https://pypi.org/project/swarmauri/)

**Provider Documentation**

- [DeepSeek API quick start](https://api-docs.deepseek.com/)
- [DeepSeek chat completion reference](https://api-docs.deepseek.com/api/create-chat-completion)
- [DeepSeek reasoning model guide](https://api-docs.deepseek.com/guides/reasoning_model)

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_llm_deepseek` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_deepseek/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_llm_deepseek` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_llm_deepseek` source version is `0.11.0.dev3`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_deepseek/LICENSE).
<!-- readme-standards:end license -->

Apache-2.0

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_deepseek/NOTICE) for attribution.
<!-- readme-standards:end notices -->
