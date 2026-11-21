# swarmauri_llm_groq

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_llm_groq</strong></p>
<p align="center">Provider-specific Swarmauri import package for Groq OpenAI-compatible chat, tool use, vision-language, streaming, and audio transcription workflows.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_llm_groq/"><img alt="pypi: swarmauri_llm_groq" src="https://img.shields.io/pypi/v/swarmauri_llm_groq"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_groq/pyproject.toml"><img alt="Source version: 0.11.0.dev3" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev3&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_groq/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_groq/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_groq/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_groq/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_groq/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_llm_groq/"><img alt="Monthly PyPI downloads: swarmauri_llm_groq" src="https://img.shields.io/pypi/dm/swarmauri_llm_groq"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_groq/README.md"><img alt="README hits: swarmauri_llm_groq" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/community/swarmauri_llm_groq/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_groq/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_groq/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_llm_groq` provides provider-specific Groq imports for Swarmauri
applications that need fast OpenAI-compatible inference. The package exports
chat, tool-calling, vision, and audio adapters while keeping their runtime
implementations aligned with `swarmauri_standard`.

Groq's public API documentation describes an OpenAI-compatible base URL at
`https://api.groq.com/openai/v1`, with endpoints for chat completions, audio
transcriptions, and audio translations. This package maps those API surfaces
into Swarmauri components:

- `GroqModel` for chat completions, streaming, JSON responses, and batch helper
  workflows.
- `GroqToolModel` for function/tool calling through Swarmauri `Toolkit`
  instances.
- `GroqVisionModel` for vision-language chat completion payloads.
- `GroqAIAudio` for transcription and translation with Groq-hosted Whisper
  models.

### Why This Package

- Keep Groq-specific model dependencies explicit while preserving common
  Swarmauri conversation and toolkit patterns.
- Use Groq's low-latency OpenAI-compatible chat completions without rewriting
  application code around raw HTTP payloads.
- Add tool calling, vision-language prompts, or speech-to-text workflows from
  one provider package.
- Swap between Groq and other Swarmauri LLM provider packages while retaining
  familiar `predict`, `stream`, `apredict`, `astream`, `batch`, and `abatch`
  workflows.

### When to Use

Choose `swarmauri_llm_groq` when your integration needs provider-specific Swarmauri import package for Groq OpenAI-compatible chat, tool use, vision-language, streaming, and audio transcription workflows. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- `GroqModel` for synchronous, asynchronous, streaming, JSON, and batch chat
  completion workflows.
- `GroqToolModel` for Groq tool use with Swarmauri `Toolkit` schemas.
- `GroqVisionModel` for OpenAI-compatible vision-language chat payloads.
- `GroqAIAudio` for Whisper transcription and translation tasks.
- Usage metadata support where Groq chat responses include usage data.
- Model discovery through Groq's OpenAI-compatible models endpoint for chat.
- Compatibility with Python 3.10, 3.11, 3.12, 3.13, and 3.14.

### Non-Goals

`swarmauri_llm_groq` owns provider-specific Swarmauri import package for Groq OpenAI-compatible chat, tool use, vision-language, streaming, and audio transcription workflows. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Create a Groq API key in the Groq console and pass it to the model constructor
as `api_key=...`. Package live tests are skipped unless provider credentials are
available in the environment.

### Installation

```bash
uv add swarmauri_llm_groq
```

```bash
pip install swarmauri_llm_groq
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_llm_groq
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_llm_groq
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_llm_groq
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_groq/docs/readme/quick_start.py).

```python
from swarmauri_llm_groq import GroqModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(
    HumanMessage(content="Write a one-sentence release note.")
)

model = GroqModel(api_key="GROQ_API_KEY")
result = model.predict(conversation=conversation, max_tokens=120)

print(result.get_last().content)
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_llm_groq` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_groq/docs/readme/usage.py).

```python
from swarmauri_llm_groq import GroqModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(
    HumanMessage(content="Write a one-sentence release note.")
)

model = GroqModel(api_key="GROQ_API_KEY")
result = model.predict(conversation=conversation, max_tokens=120)

print(result.get_last().content)
```
<!-- readme-standards:end example.usage -->

**Streaming Chat Completion**

```python
from swarmauri_llm_groq import GroqModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(HumanMessage(content="List three build pipeline risks."))

model = GroqModel(api_key="GROQ_API_KEY")

for token in model.stream(conversation=conversation):
    print(token, end="")
```

**Tool Calling**

```python
from swarmauri_llm_groq import GroqToolModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage
from swarmauri_standard.toolkits.Toolkit import Toolkit

conversation = Conversation()
conversation.add_message(HumanMessage(content="Use a tool if one is relevant."))

toolkit = Toolkit()
model = GroqToolModel(api_key="GROQ_API_KEY")
result = model.predict(conversation=conversation, toolkit=toolkit)

print(result.get_last().content)
```

**Audio Transcription**

```python
from swarmauri_llm_groq import GroqAIAudio

audio = GroqAIAudio(api_key="GROQ_API_KEY")
text = audio.predict("meeting.wav", task="transcription")

print(text)
```

**Vision-Language Prompt**

```python
from swarmauri_llm_groq import GroqVisionModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(
    HumanMessage(
        content=[
            {"type": "text", "text": "Describe the image."},
            {"type": "image_url", "image_url": {"url": "https://example.com/image.png"}},
        ]
    )
)

model = GroqVisionModel(api_key="GROQ_API_KEY")
result = model.predict(conversation=conversation)

print(result.get_last().content)
```

### Configuration

Configure `swarmauri_llm_groq` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_groq/swarmauri_llm_groq/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_groq/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_llm_groq` source does not establish a package-wide exception hierarchy. Preserve errors from its declared dependencies and validate inputs using the specific public contract in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_groq/swarmauri_llm_groq/__init__.py).

### Best Practices

- Store Groq API keys in environment variables or a secrets manager.
- Confirm model availability against Groq's current model catalog before
  production deployment.
- Use `GroqToolModel` only when tools are needed; plain chat requests are simpler
  with `GroqModel`.
- Use `GroqAIAudio` for file-based transcription and translation, not streaming
  audio.
- Prefer newer Swarmauri VLM and STT imports for new projects when available.

---

## Package Boundary

### What It Owns

`swarmauri_llm_groq` is located in `community` and owns provider-specific Swarmauri import package for Groq OpenAI-compatible chat, tool use, vision-language, streaming, and audio transcription workflows. Source-declared APIs include `GroqAIAudio`, `GroqModel`, `GroqToolModel`, `GroqVLM`, `GroqVisionModel`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_groq/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_llm_groq`.

Source-declared exports or types: `GroqAIAudio`, `GroqModel`, `GroqToolModel`, `GroqVLM`, `GroqVisionModel`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_groq/swarmauri_llm_groq/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.llms` → `GroqAIAudio` → `swarmauri_llm_groq.GroqAIAudio:GroqAIAudio`
- `swarmauri.llms` → `GroqModel` → `swarmauri_llm_groq.GroqModel:GroqModel`
- `swarmauri.llms` → `GroqVisionModel` → `swarmauri_llm_groq.GroqVisionModel:GroqVisionModel`
- `swarmauri.tool_llms` → `GroqToolModel` → `swarmauri_llm_groq.GroqToolModel:GroqToolModel`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_llm_groq` are `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_groq/swarmauri_llm_groq/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_llm_groq` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_llm_groq`, use the source-declared public interfaces (`GroqAIAudio`, `GroqModel`, `GroqToolModel`, `GroqVLM`, `GroqVisionModel`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_llm_groq` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_groq/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_llm_groq`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_groq/swarmauri_llm_groq/__init__.py). The `swarmauri_llm_groq` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_llm_groq` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_llm_groq` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/i9n/test_GroqModel_i9n.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_groq/tests/i9n/test_GroqModel_i9n.py)
- [tests/r8n/test_GroqToolModel_r8n.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_groq/tests/r8n/test_GroqToolModel_r8n.py)
- [tests/unit/test_GroqAIAudio_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_groq/tests/unit/test_GroqAIAudio_unit.py)
- [tests/unit/test_GroqModel_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_groq/tests/unit/test_GroqModel_unit.py)
- [tests/unit/test_GroqToolModel_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_groq/tests/unit/test_GroqToolModel_unit.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_llm_groq` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_groq/swarmauri_llm_groq/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**What does swarmauri_llm_groq install?**

It installs provider package entry points for `GroqModel`, `GroqToolModel`,
`GroqVisionModel`, and `GroqAIAudio`.

**Which Groq endpoints does it call?**

The chat, tool, and vision adapters post to
`https://api.groq.com/openai/v1/chat/completions`. The audio adapter uses
`https://api.groq.com/openai/v1/audio/transcriptions` and
`https://api.groq.com/openai/v1/audio/translations`.

**Does it support tool calling?**

Yes. `GroqToolModel` converts Swarmauri toolkit schemas to Groq-compatible tool
definitions, sends them with chat completions, executes returned tool calls, and
can perform a follow-up model call with tool results.

**Does it support vision?**

Yes. `GroqVisionModel` accepts Swarmauri message content that can include
structured content lists for OpenAI-compatible vision chat payloads. The runtime
also emits a deprecation warning that new projects should review the newer
Swarmauri VLM imports when available.

**Does audio streaming work?**

No. `GroqAIAudio` supports file-based transcription and translation through
`predict`, `apredict`, `batch`, and `abatch`. Its `stream` and `astream` methods
raise `NotImplementedError`.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_llm_groq`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_groq/swarmauri_llm_groq/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_llm_groq` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_groq/swarmauri_llm_groq/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_groq/pyproject.toml) provide the supporting context for `swarmauri_llm_groq`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_llm_anthropic](https://pypi.org/project/swarmauri_llm_anthropic/)
- [swarmauri_llm_deepinfra](https://pypi.org/project/swarmauri_llm_deepinfra/)
- [swarmauri_llm_deepseek](https://pypi.org/project/swarmauri_llm_deepseek/)
- [swarmauri_llm_gemini](https://pypi.org/project/swarmauri_llm_gemini/)
- [swarmauri_llm_mistral](https://pypi.org/project/swarmauri_llm_mistral/)
- [swarmauri_llm_openai](https://pypi.org/project/swarmauri_llm_openai/)
- [swarmauri_llm_whisper](https://pypi.org/project/swarmauri_llm_whisper/)

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_llm_groq](https://pypi.org/project/swarmauri_llm_groq/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_llm_groq`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/community/swarmauri_llm_groq` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

**Foundational Swarmauri Packages**

- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)
- [swarmauri](https://pypi.org/project/swarmauri/)

**Provider Documentation**

- [Groq API reference](https://console.groq.com/docs/api-reference)
- [Groq OpenAI compatibility](https://console.groq.com/docs/openai)
- [Groq models](https://console.groq.com/docs/models)
- [Groq tool use](https://console.groq.com/docs/tool-use)
- [Groq speech to text](https://console.groq.com/docs/speech-to-text)

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_llm_groq` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_groq/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_llm_groq` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_llm_groq` source version is `0.11.0.dev3`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_groq/LICENSE).
<!-- readme-standards:end license -->

Apache-2.0

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_groq/NOTICE) for attribution.
<!-- readme-standards:end notices -->
