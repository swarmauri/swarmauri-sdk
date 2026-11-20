# swarmauri_llm_openai

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_llm_openai</strong></p>
<p align="center">Provider-specific Swarmauri import package for OpenAI chat, reasoning, tool-calling, transcription, and text-to-speech workflows.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_llm_openai/"><img alt="pypi: swarmauri_llm_openai" src="https://img.shields.io/pypi/v/swarmauri_llm_openai"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_openai/pyproject.toml"><img alt="Source version: 0.11.0.dev5" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev5&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_openai/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_openai/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_openai/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_openai/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_openai/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_llm_openai/"><img alt="Monthly PyPI downloads: swarmauri_llm_openai" src="https://img.shields.io/pypi/dm/swarmauri_llm_openai"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_openai/README.md"><img alt="README hits: swarmauri_llm_openai" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/community/swarmauri_llm_openai/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_openai/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_openai/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_llm_openai` provides provider-specific Swarmauri imports for OpenAI chat, reasoning, tool-calling, audio transcription, and text-to-speech workflows. The package exposes `OpenAIModel`, `OpenAIReasonModel`, `OpenAIToolModel`, `OpenAIAudio`, and `OpenAIAudioTTS` as direct provider-package imports while preserving the shared runtime implementations in `swarmauri_standard`.

The repo currently tracks OpenAI chat model families including `gpt-5.x`, `gpt-4.1`, `gpt-4o`, `gpt-4-turbo`, `gpt-oss`, reasoning families including `o1`, `o3`, and `o4-mini`, audio transcription models including `whisper-1` and `gpt-4o-*transcribe`, and text-to-speech models including `tts-1`, `tts-1-hd`, and `gpt-4o-mini-tts`.

### Why This Package

- Keep OpenAI-specific imports explicit in Swarmauri applications.
- Use separate adapters for standard chat, reasoning, tool-calling, transcription, and TTS workflows.
- Reuse Swarmauri `Conversation`, toolkit, and component semantics across the OpenAI surface area.
- Track current OpenAI model families through one provider package boundary.

### When to Use

Choose `swarmauri_llm_openai` when your integration needs provider-specific Swarmauri import package for OpenAI chat, reasoning, tool-calling, transcription, and text-to-speech workflows. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- `OpenAIModel` for sync, async, streaming, and batch chat completion workflows.
- `OpenAIReasonModel` for reasoning-model workflows across the repo-tracked `o*` families.
- `OpenAIToolModel` for toolkit-backed tool-calling and agent execution flows.
- `OpenAIAudio` for speech-to-text workflows against the tracked OpenAI transcription models.
- `OpenAIAudioTTS` for text-to-speech workflows against the tracked OpenAI TTS models.
- Compatibility with Python 3.10, 3.11, 3.12, 3.13, and 3.14.

### Non-Goals

`swarmauri_llm_openai` owns provider-specific Swarmauri import package for OpenAI chat, reasoning, tool-calling, transcription, and text-to-speech workflows. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_openai/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. Read the example’s inputs and service requirements before execution.

### Installation

```bash
uv add swarmauri_llm_openai
```

```bash
pip install swarmauri_llm_openai
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_llm_openai
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_llm_openai
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_llm_openai
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_openai/docs/readme/quick_start.py).

```python
import os

from swarmauri_llm_openai import OpenAIModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(
    HumanMessage(content="Summarize Swarmauri in two sentences.")
)

model = OpenAIModel(
    api_key=os.environ["OPENAI_API_KEY"],
    name="gpt-5.5",
)
result = model.predict(conversation=conversation)

print(result.get_last().content)
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_llm_openai` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_openai/docs/readme/usage.py).

```python
import os

from swarmauri_llm_openai import OpenAIModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(
    HumanMessage(content="Summarize Swarmauri in two sentences.")
)

model = OpenAIModel(
    api_key=os.environ["OPENAI_API_KEY"],
    name="gpt-5.5",
)
result = model.predict(conversation=conversation)

print(result.get_last().content)
```
<!-- readme-standards:end example.usage -->

Set `OPENAI_API_KEY` in your environment before creating any of the OpenAI adapters.

**Chat Completion**


**Reasoning Model**

```python
import os

from swarmauri_llm_openai import OpenAIReasonModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(HumanMessage(content="Reason through a release rollback plan step by step."))

model = OpenAIReasonModel(
    api_key=os.environ["OPENAI_API_KEY"],
    name="o3",
)
result = model.predict(conversation=conversation)

print(result.get_last().content)
```

**Tool Calling**

```python
import os

from swarmauri_llm_openai import OpenAIToolModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage
from swarmauri_standard.toolkits.Toolkit import Toolkit
from swarmauri_standard.tools.AdditionTool import AdditionTool

conversation = Conversation()
conversation.add_message(HumanMessage(content="What is 19 + 23? Use the tool."))

toolkit = Toolkit(tools={"add": AdditionTool()})

model = OpenAIToolModel(
    api_key=os.environ["OPENAI_API_KEY"],
    name="gpt-5.5",
)
result = model.predict(
    conversation=conversation,
    toolkit=toolkit,
    tool_choice="auto",
)

print(result.get_last().content)
```

**Audio Transcription**

```python
import os

from swarmauri_llm_openai import OpenAIAudio

audio_model = OpenAIAudio(
    api_key=os.environ["OPENAI_API_KEY"],
    name="whisper-1",
)

text = audio_model.predict("tests/static/test.mp3")
print(text)
```

**Text To Speech**

```python
import os

from swarmauri_llm_openai import OpenAIAudioTTS

tts_model = OpenAIAudioTTS(
    api_key=os.environ["OPENAI_API_KEY"],
    name="tts-1",
)

audio_bytes = tts_model.predict("Swarmauri turns provider APIs into composable components.")
print(len(audio_bytes))
```

- Use `OpenAIModel` for general-purpose chat completion workflows.
- Use `OpenAIReasonModel` when you want the reasoning-model family explicitly.
- Use `OpenAIToolModel` when an agent needs toolkit-backed tool invocation.
- Use `OpenAIAudio` and `OpenAIAudioTTS` when the workflow crosses text, speech, and audio generation boundaries.

### Configuration

Configure `swarmauri_llm_openai` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_openai/swarmauri_llm_openai/OpenAIAudioTTS.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_openai/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_llm_openai` source does not establish a package-wide exception hierarchy. Preserve errors from its declared dependencies and validate inputs using the specific public contract in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_openai/swarmauri_llm_openai/OpenAIAudioTTS.py).

### Best Practices

- Keep `OPENAI_API_KEY` in environment variables or a secret manager.
- Pick the adapter that matches the workflow: chat, reasoning, tool-calling, transcription, or TTS.
- Validate model availability against current OpenAI docs before hard-coding a dated model variant in production.
- Use reasoning models deliberately, since they should be chosen for workflows that actually benefit from deeper multi-step reasoning.

---

## Package Boundary

### What It Owns

`swarmauri_llm_openai` is located in `community` and owns provider-specific Swarmauri import package for OpenAI chat, reasoning, tool-calling, transcription, and text-to-speech workflows. Source-declared APIs include `OpenAIAudio`, `OpenAIAudioTTS`, `OpenAIModel`, `OpenAIReasonModel`, `OpenAIToolModel`, `OpenAIVLM`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_openai/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_llm_openai`.

Source-declared exports or types: `OpenAIAudio`, `OpenAIAudioTTS`, `OpenAIModel`, `OpenAIReasonModel`, `OpenAIToolModel`, `OpenAIVLM`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_openai/swarmauri_llm_openai/OpenAIAudioTTS.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.llms` → `OpenAIAudio` → `swarmauri_llm_openai.OpenAIAudio:OpenAIAudio`
- `swarmauri.llms` → `OpenAIAudioTTS` → `swarmauri_llm_openai.OpenAIAudioTTS:OpenAIAudioTTS`
- `swarmauri.llms` → `OpenAIModel` → `swarmauri_llm_openai.OpenAIModel:OpenAIModel`
- `swarmauri.llms` → `OpenAIReasonModel` → `swarmauri_llm_openai.OpenAIReasonModel:OpenAIReasonModel`
- `swarmauri.tool_llms` → `OpenAIToolModel` → `swarmauri_llm_openai.OpenAIToolModel:OpenAIToolModel`
- `swarmauri.vlms` → `OpenAIVLM` → `swarmauri_llm_openai.OpenAIVLM:OpenAIVLM`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_llm_openai` are `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_openai/swarmauri_llm_openai/OpenAIAudioTTS.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_llm_openai` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_llm_openai`, use the source-declared public interfaces (`OpenAIAudio`, `OpenAIAudioTTS`, `OpenAIModel`, `OpenAIReasonModel`, `OpenAIToolModel`, `OpenAIVLM`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_llm_openai` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_openai/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_llm_openai`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_openai/swarmauri_llm_openai/OpenAIAudioTTS.py). The `swarmauri_llm_openai` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_llm_openai` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_llm_openai` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/unit/test_OpenAIAudioTTS_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_openai/tests/unit/test_OpenAIAudioTTS_unit.py)
- [tests/unit/test_OpenAIAudio_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_openai/tests/unit/test_OpenAIAudio_unit.py)
- [tests/unit/test_OpenAIModel_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_openai/tests/unit/test_OpenAIModel_unit.py)
- [tests/unit/test_OpenAIReasonModel_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_openai/tests/unit/test_OpenAIReasonModel_unit.py)
- [tests/unit/test_OpenAIToolModel_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_openai/tests/unit/test_OpenAIToolModel_unit.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_llm_openai` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_openai/swarmauri_llm_openai/OpenAIAudioTTS.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**What does swarmauri_llm_openai install?**

It installs `OpenAIModel`, `OpenAIReasonModel`, `OpenAIToolModel`, `OpenAIAudio`, and `OpenAIAudioTTS`.

**Which OpenAI capabilities are wrapped today?**

The package covers standard chat completions, reasoning-oriented chat models, tool-calling workflows, audio transcription, and text-to-speech generation.

**What is the difference between OpenAIModel and OpenAIReasonModel?**

`OpenAIModel` targets general chat model families such as `gpt-5.x`, `gpt-4.1`, and `gpt-4o`. `OpenAIReasonModel` targets the reasoning families tracked in the repo, including `o1`, `o3`, and `o4-mini` variants.

**What do OpenAIAudio and OpenAIAudioTTS do?**

`OpenAIAudio` wraps audio transcription workflows. `OpenAIAudioTTS` wraps text-to-speech generation workflows.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_llm_openai`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_openai/swarmauri_llm_openai/OpenAIAudioTTS.py) for the exact types and signatures involved.

### When

**When should I use OpenAIToolModel?**

Use it when the application needs OpenAI tool calling through a Swarmauri toolkit. It is the provider-specific surface for tool-backed agent workflows.

**Where should I verify current models and pricing?**

Use the OpenAI section in [docs/LLM_PROVIDER_MODEL_PRICING_LINKS.md](../../../docs/LLM_PROVIDER_MODEL_PRICING_LINKS.md), which points to the current OpenAI models, function-calling, audio, TTS, and pricing documentation.

---

## Documentation and Related Packages

### More Documentation

- [LLM provider model and pricing links](../../../docs/LLM_PROVIDER_MODEL_PRICING_LINKS.md)
- [OpenAI models](https://platform.openai.com/docs/models)
- [OpenAI function calling](https://platform.openai.com/docs/guides/function-calling)
- [OpenAI text to speech](https://platform.openai.com/docs/guides/text-to-speech)

### Related Packages

- [swarmauri_llm_mistral](https://pypi.org/project/swarmauri_llm_mistral/)
- [swarmauri_llm_groq](https://pypi.org/project/swarmauri_llm_groq/)
- [swarmauri_llm_hyperbolic](https://pypi.org/project/swarmauri_llm_hyperbolic/)
- [swarmauri_llm_deepinfra](https://pypi.org/project/swarmauri_llm_deepinfra/)
- [swarmauri_llm_perplexity](https://pypi.org/project/swarmauri_llm_perplexity/)
- [OpenAI TTS (Play.ht replacement)](../../standards/swarmauri_tts_openai/README.md)

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_llm_openai](https://pypi.org/project/swarmauri_llm_openai/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_llm_openai`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/community/swarmauri_llm_openai` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

**Foundational Swarmauri Packages**

- [swarmauri](https://pypi.org/project/swarmauri/)
- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)

**Resumable tool approvals**

Pass the tool model to `AgentRunner` to pause before application tools run. This requires `swarmauri_standard>=0.11.0.dev9`.

**Speech import migration**

`OpenAIAudioTTS` is retained with a deprecation warning. For new speech code,
install `swarmauri_tts_openai` and use `from swarmauri_tts_openai import OpenaiTTS`.
The new provider remains alpha and live API verification is tracked in
[issue #6268](https://github.com/swarmauri/swarmauri-sdk/issues/6268).

OpenAIAudioTTS remains a deprecated compatibility import. The canonical
swarmauri_tts_openai package also warns that OpenAI's Speech models shut down
on 2027-01-06. The Realtime replacement uses a different API; see
[the migration guide](../../../docs/migrations/openai-speech.md).

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_llm_openai` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_openai/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_llm_openai` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_llm_openai` source version is `0.11.0.dev5`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_openai/LICENSE).
<!-- readme-standards:end license -->

Apache-2.0

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_openai/NOTICE) for attribution.
<!-- readme-standards:end notices -->
