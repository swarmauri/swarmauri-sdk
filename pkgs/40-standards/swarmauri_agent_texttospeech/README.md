# swarmauri_agent_texttospeech

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_agent_texttospeech</strong></p>
<p align="center">Stateless Swarmauri agent for converting independent text prompts into audio through any TTSBase provider.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_agent_texttospeech/"><img alt="pypi: swarmauri_agent_texttospeech" src="https://img.shields.io/pypi/v/swarmauri_agent_texttospeech?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_agent_texttospeech/pyproject.toml"><img alt="Source version: 0.11.0.dev7" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev7&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_agent_texttospeech/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_agent_texttospeech/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_agent_texttospeech/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_agent_texttospeech/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_agent_texttospeech/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_agent_texttospeech/"><img alt="Monthly PyPI downloads: swarmauri_agent_texttospeech" src="https://img.shields.io/pypi/dm/swarmauri_agent_texttospeech?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_agent_texttospeech/README.md"><img alt="README hits: swarmauri_agent_texttospeech" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/40-standards/swarmauri_agent_texttospeech/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_agent_texttospeech/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_agent_texttospeech/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_agent_texttospeech` provides a stateless agent that converts each
text prompt into an audio file through any Swarmauri `TTSBase` provider.

[![PyPI Downloads](https://static.pepy.tech/badge/swarmauri_agent_texttospeech)](https://pepy.tech/projects/swarmauri_agent_texttospeech)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/40-standards/swarmauri_agent_texttospeech.svg)](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/40-standards/swarmauri_agent_texttospeech/)
[![Python Versions](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue)](https://pypi.org/project/swarmauri_agent_texttospeech/)
[![License](https://img.shields.io/pypi/l/swarmauri_agent_texttospeech)](https://pypi.org/project/swarmauri_agent_texttospeech/)
[![PyPI Version](https://img.shields.io/pypi/v/swarmauri_agent_texttospeech)](https://pypi.org/project/swarmauri_agent_texttospeech/)

### Why This Package

`swarmauri_agent_texttospeech` isolates this responsibility: Stateless Swarmauri agent for converting independent text prompts into audio through any TTSBase provider. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_agent_texttospeech/swarmauri_agent_texttospeech/TextToSpeechAgent.py) exposes `TextToSpeechAgent`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_agent_texttospeech` when your integration needs stateless Swarmauri agent for converting independent text prompts into audio through any TTSBase provider. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Converts one fresh text input into one audio file.
- Uses any provider implementing Swarmauri's `TTSBase` contract.
- Keeps no conversation history, memory, or system context.
- Supports synchronous, asynchronous, and batch agent execution.
- Generates distinct default paths for batch outputs.

### Non-Goals

`swarmauri_agent_texttospeech` owns stateless Swarmauri agent for converting independent text prompts into audio through any TTSBase provider. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_agent_texttospeech/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`. Read the example’s inputs and service requirements before execution.

### Installation

```bash
uv add swarmauri_agent_texttospeech
```

```bash
pip install swarmauri_agent_texttospeech
```

Install a TTS provider package alongside the agent. For the alpha OpenAI provider:

```bash
uv add --prerelease allow swarmauri_tts_openai
```

Or with `pip`:

```bash
pip install --pre swarmauri_tts_openai
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_agent_texttospeech
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_agent_texttospeech
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_agent_texttospeech
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_agent_texttospeech/docs/readme/quick_start.py).

```python
import os

from swarmauri_agent_texttospeech import TextToSpeechAgent
from swarmauri_tts_openai import OpenaiTTS

tts = OpenaiTTS(
    api_key=os.environ["OPENAI_API_KEY"],
    name="gpt-4o-mini-tts",
    voice="alloy",
)
agent = TextToSpeechAgent(tts=tts, output_path="greeting.mp3")

audio_path = agent.exec("Welcome to Swarmauri.")
print(audio_path)
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_agent_texttospeech` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_agent_texttospeech/docs/readme/usage.py).

```python
import os

from swarmauri_agent_texttospeech import TextToSpeechAgent
from swarmauri_tts_openai import OpenaiTTS

tts = OpenaiTTS(
    api_key=os.environ["OPENAI_API_KEY"],
    name="gpt-4o-mini-tts",
    voice="alloy",
)
agent = TextToSpeechAgent(tts=tts, output_path="greeting.mp3")

audio_path = agent.exec("Welcome to Swarmauri.")
print(audio_path)
```
<!-- readme-standards:end example.usage -->

Each call is independent. The agent passes only that call's text to the TTS
provider and never constructs a conversation or system message.

### Configuration

Configure `swarmauri_agent_texttospeech` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_agent_texttospeech/swarmauri_agent_texttospeech/TextToSpeechAgent.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_agent_texttospeech/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_agent_texttospeech` source raises `TypeError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_agent_texttospeech` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `TextToSpeechAgent`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_agent_texttospeech` is located in `standards` and owns stateless Swarmauri agent for converting independent text prompts into audio through any TTSBase provider. Source-declared APIs include `TextToSpeechAgent`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_agent_texttospeech/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_agent_texttospeech`.

Source-declared exports or types: `TextToSpeechAgent`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_agent_texttospeech/swarmauri_agent_texttospeech/TextToSpeechAgent.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.agents` → `TextToSpeechAgent` → `swarmauri_agent_texttospeech:TextToSpeechAgent`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_agent_texttospeech` are `swarmauri-core`, `swarmauri-base`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_agent_texttospeech/swarmauri_agent_texttospeech/TextToSpeechAgent.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_agent_texttospeech` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_agent_texttospeech`, use the source-declared public interfaces (`TextToSpeechAgent`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_agent_texttospeech` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_agent_texttospeech/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_agent_texttospeech`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_agent_texttospeech/swarmauri_agent_texttospeech/TextToSpeechAgent.py). The `swarmauri_agent_texttospeech` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_agent_texttospeech` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_agent_texttospeech` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/unit/test_dialogue_providers.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_agent_texttospeech/tests/unit/test_dialogue_providers.py)
- [tests/unit/test_provider_import_order.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_agent_texttospeech/tests/unit/test_provider_import_order.py)
- [tests/unit/test_text_to_speech_agent.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_agent_texttospeech/tests/unit/test_text_to_speech_agent.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_agent_texttospeech` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_agent_texttospeech/swarmauri_agent_texttospeech/TextToSpeechAgent.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_agent_texttospeech` provides stateless Swarmauri agent for converting independent text prompts into audio through any TTSBase provider; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_agent_texttospeech`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_agent_texttospeech/swarmauri_agent_texttospeech/TextToSpeechAgent.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_agent_texttospeech` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_agent_texttospeech/swarmauri_agent_texttospeech/TextToSpeechAgent.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_agent_texttospeech/pyproject.toml) provide the supporting context for `swarmauri_agent_texttospeech`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_agent_texttospeech](https://pypi.org/project/swarmauri_agent_texttospeech/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

This package is part of the
[Swarmauri SDK](https://github.com/swarmauri/swarmauri-sdk). Contributions
should follow the repository contribution and style guides.

### Development Setup

Work from the `pkgs/40-standards/swarmauri_agent_texttospeech` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

**Structured dialogue and bounded batches**

The agent also forwards a nonempty tuple of typed dialogue turns unchanged:

```python
import os

from swarmauri_agent_texttospeech import TextToSpeechAgent
from swarmauri_tts_gemini_dialogue import (
    GeminiDialogueTTS, GeminiDialogueTurn,
)

provider = GeminiDialogueTTS(
    api_key=os.environ["GEMINI_API_KEY"],
    speaker_voices={"A": "Puck", "B": "Kore"},
)
agent = TextToSpeechAgent(tts=provider, output_path="dialogue.wav")
turns = (
    GeminiDialogueTurn(text="Hello", speaker="A"),
    GeminiDialogueTurn(text="Hello back", speaker="B"),
)
agent.exec(turns)
# await agent.abatch([turns], max_concurrent=2)
```

Speaker and voice validation belongs to the selected provider. A JSON string
is not parsed into turns. Set filenames to match the codec; Gemini/native
DeepInfra WAV defaults require .wav paths. Async batches default to at most
five concurrent calls, with a positive integer max_concurrent override.

The OpenAI Speech example above is temporary compatibility: its models have a
scheduled 2027-01-06 shutdown. All new provider packages remain alpha and live
verification is pending; see the SDK migration and verification guides.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_agent_texttospeech` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_agent_texttospeech/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_agent_texttospeech` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_agent_texttospeech` source version is `0.11.0.dev7`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_agent_texttospeech/LICENSE).
<!-- readme-standards:end license -->

Apache-2.0

Provider instances are validated against TTSBase at call-time construction, so
providers imported after the agent class remain usable. Serialized providers
retain their concrete fields; import that provider before deserialization.

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_agent_texttospeech/NOTICE) for attribution.
<!-- readme-standards:end notices -->
