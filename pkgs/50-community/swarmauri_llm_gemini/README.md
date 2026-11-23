# swarmauri_llm_gemini

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_llm_gemini</strong></p>
<p align="center">Provider-specific Swarmauri import package for Google Gemini generateContent, streaming, function calling, tool use, and async LLM workflows.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_llm_gemini/"><img alt="pypi: swarmauri_llm_gemini" src="https://img.shields.io/pypi/v/swarmauri_llm_gemini"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_gemini/pyproject.toml"><img alt="Source version: 0.11.0.dev3" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev3&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_gemini/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_gemini/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_gemini/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_gemini/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_gemini/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_llm_gemini/"><img alt="Monthly PyPI downloads: swarmauri_llm_gemini" src="https://img.shields.io/pypi/dm/swarmauri_llm_gemini"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_gemini/README.md"><img alt="README hits: swarmauri_llm_gemini" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/50-community/swarmauri_llm_gemini/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_gemini/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_gemini/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_llm_gemini` provides provider-specific imports for Google Gemini
models in Swarmauri applications. It exports `GeminiProModel` for standard
generation and streaming workflows and `GeminiToolModel` for Gemini function
calling through Swarmauri toolkits.

The adapters use Google Gemini's `generateContent` and `streamGenerateContent`
API shape through `generativelanguage.googleapis.com/v1beta`. They translate
Swarmauri conversations into Gemini `contents`, apply safety settings, preserve
system instructions where supported by the implementation, and append generated
responses back to the conversation as `AgentMessage` instances.

### Why This Package

- Keep Google Gemini-specific dependencies explicit in provider-aware Swarmauri
  applications.
- Use the same Swarmauri `Conversation`, message, and toolkit workflows across
  Gemini and other LLM providers.
- Support both direct text generation and Gemini function-calling workflows.
- Stream Gemini responses through the same high-level Swarmauri model interface
  used by other provider packages.

### When to Use

Choose `swarmauri_llm_gemini` when your integration needs provider-specific Swarmauri import package for Google Gemini generateContent, streaming, function calling, tool use, and async LLM workflows. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- `GeminiProModel` for generation, async generation, streaming, and batch
  conversation workflows.
- `GeminiToolModel` for Gemini function calling through Swarmauri toolkits.
- Support for Gemini `systemInstruction` / `system_instruction` payloads in the
  current adapters.
- Safety settings for harassment, hate speech, sexually explicit content, and
  dangerous content thresholds.
- Configurable generation controls such as `temperature` and `max_tokens`.
- Optional usage metadata handling on `GeminiProModel`.
- Compatibility with Python 3.10, 3.11, 3.12, 3.13, and 3.14.

### Non-Goals

`swarmauri_llm_gemini` owns provider-specific Swarmauri import package for Google Gemini generateContent, streaming, function calling, tool use, and async LLM workflows. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Create a Gemini API key in Google AI Studio or Google Cloud and pass it to the
model constructor as `api_key=...`.

### Installation

```bash
uv add swarmauri_llm_gemini
```

```bash
pip install swarmauri_llm_gemini
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_llm_gemini
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_llm_gemini
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_llm_gemini
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_gemini/docs/readme/quick_start.py).

```python
from swarmauri_llm_gemini import GeminiProModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(
    HumanMessage(content="Write a concise project status update.")
)

model = GeminiProModel(api_key="GEMINI_API_KEY")
result = model.predict(conversation=conversation, max_tokens=200)

print(result.get_last().content)
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_llm_gemini` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_gemini/docs/readme/usage.py).

```python
from swarmauri_llm_gemini import GeminiProModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(
    HumanMessage(content="Write a concise project status update.")
)

model = GeminiProModel(api_key="GEMINI_API_KEY")
result = model.predict(conversation=conversation, max_tokens=200)

print(result.get_last().content)
```
<!-- readme-standards:end example.usage -->

**Streaming**

```python
from swarmauri_llm_gemini import GeminiProModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(HumanMessage(content="List three risks for an AI release."))

model = GeminiProModel(api_key="GEMINI_API_KEY")

for token in model.stream(conversation=conversation, max_tokens=200):
    print(token, end="")
```

**Tool Calling**

```python
from swarmauri_llm_gemini import GeminiToolModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage
from swarmauri_standard.toolkits.Toolkit import Toolkit

conversation = Conversation()
conversation.add_message(HumanMessage(content="Use the available tool if needed."))

toolkit = Toolkit()
model = GeminiToolModel(api_key="GEMINI_API_KEY")
result = model.predict(conversation=conversation, toolkit=toolkit)

print(result.get_last().content)
```

### Configuration

Configure `swarmauri_llm_gemini` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_gemini/swarmauri_llm_gemini/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_gemini/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_llm_gemini` source does not establish a package-wide exception hierarchy. Preserve errors from its declared dependencies and validate inputs using the specific public contract in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_gemini/swarmauri_llm_gemini/__init__.py).

### Best Practices

- Store Gemini API keys in environment variables or a secrets manager.
- Confirm model availability against the current Gemini API before pinning model
  names for production.
- Use `GeminiToolModel` only when the workflow actually needs tool execution.
- Keep tool schemas small and deterministic so Gemini can select and call tools
  reliably.

---

## Package Boundary

### What It Owns

`swarmauri_llm_gemini` is located in `community` and owns provider-specific Swarmauri import package for Google Gemini generateContent, streaming, function calling, tool use, and async LLM workflows. Source-declared APIs include `GeminiProModel`, `GeminiToolModel`, `GeminiVLM`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_gemini/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_llm_gemini`.

Source-declared exports or types: `GeminiProModel`, `GeminiToolModel`, `GeminiVLM`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_gemini/swarmauri_llm_gemini/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.llms` → `GeminiProModel` → `swarmauri_llm_gemini.GeminiProModel:GeminiProModel`
- `swarmauri.tool_llms` → `GeminiToolModel` → `swarmauri_llm_gemini.GeminiToolModel:GeminiToolModel`
- `swarmauri.vlms` → `GeminiVLM` → `swarmauri_llm_gemini.GeminiVLM:GeminiVLM`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_llm_gemini` are `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_gemini/swarmauri_llm_gemini/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_llm_gemini` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_llm_gemini`, use the source-declared public interfaces (`GeminiProModel`, `GeminiToolModel`, `GeminiVLM`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_llm_gemini` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_gemini/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_llm_gemini`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_gemini/swarmauri_llm_gemini/__init__.py). The `swarmauri_llm_gemini` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_llm_gemini` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_llm_gemini` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/r8n/test_GeminiToolModel_r8n.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_gemini/tests/r8n/test_GeminiToolModel_r8n.py)
- [tests/unit/test_GeminiProModel_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_gemini/tests/unit/test_GeminiProModel_unit.py)
- [tests/unit/test_GeminiToolModel_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_gemini/tests/unit/test_GeminiToolModel_unit.py)
- [tests/xfail/test_GeminiProModel_xfail.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_gemini/tests/xfail/test_GeminiProModel_xfail.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_llm_gemini` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_gemini/swarmauri_llm_gemini/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**What does swarmauri_llm_gemini install?**

It installs provider package entry points for `GeminiProModel` and
`GeminiToolModel`, both re-exported from `swarmauri_standard`.

**Which Gemini API methods does it use?**

`GeminiProModel` calls `models.generateContent` for standard prediction and
`models.streamGenerateContent` for streaming. `GeminiToolModel` uses
`generateContent` with Gemini-compatible function declarations converted from a
Swarmauri `Toolkit`.

**Does this package support tools?**

Yes. Use `GeminiToolModel` when a conversation should give Gemini access to
Swarmauri tools. The adapter converts toolkit schemas with
`GeminiSchemaConverter`, executes returned function calls, and can make a
follow-up model call with tool results.

**Which models are listed by default?**

The current implementation includes Gemini 2.0 Flash, Gemini 2.0 Flash Lite,
Gemini 2.0 Pro experimental, Gemini 1.5 Flash, Gemini 1.5 Flash 8B, and Gemini
1.5 Pro in its allowed model list. Confirm current production model availability
in Google's Gemini API documentation before pinning deployment defaults.

**Can it include usage metadata?**

`GeminiProModel` can attach token usage metadata to the returned Swarmauri
`AgentMessage` when `include_usage` is enabled and the provider response
contains usage metadata.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_llm_gemini`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_gemini/swarmauri_llm_gemini/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_llm_gemini` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_gemini/swarmauri_llm_gemini/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_gemini/pyproject.toml) provide the supporting context for `swarmauri_llm_gemini`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_llm_anthropic](https://pypi.org/project/swarmauri_llm_anthropic/)
- [swarmauri_llm_cohere](https://pypi.org/project/swarmauri_llm_cohere/)
- [swarmauri_llm_deepseek](https://pypi.org/project/swarmauri_llm_deepseek/)
- [swarmauri_llm_groq](https://pypi.org/project/swarmauri_llm_groq/)
- [swarmauri_llm_mistral](https://pypi.org/project/swarmauri_llm_mistral/)
- [swarmauri_llm_openai](https://pypi.org/project/swarmauri_llm_openai/)

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_llm_gemini](https://pypi.org/project/swarmauri_llm_gemini/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_llm_gemini`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/50-community/swarmauri_llm_gemini` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

**Foundational Swarmauri Packages**

- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)
- [swarmauri](https://pypi.org/project/swarmauri/)

**Provider Documentation**

- [Gemini API reference](https://ai.google.dev/api)
- [Generate content with Gemini](https://ai.google.dev/api/generate-content)
- [Gemini function calling](https://ai.google.dev/gemini-api/docs/function-calling)

**Resumable tool approvals**

Pass the tool model to `AgentRunner` to pause before application tools run. This requires `swarmauri_standard>=0.11.0.dev9`.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_llm_gemini` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_gemini/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_llm_gemini` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_llm_gemini` source version is `0.11.0.dev3`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_gemini/LICENSE).
<!-- readme-standards:end license -->

Apache-2.0

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_gemini/NOTICE) for attribution.
<!-- readme-standards:end notices -->
