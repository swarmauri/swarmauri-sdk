# swarmauri_llm_whisper

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_llm_whisper</strong></p>
<p align="center">Provider-specific Swarmauri import package for Whisper transcription, translation, async, and batch speech-to-text workflows.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_llm_whisper/"><img alt="pypi: swarmauri_llm_whisper" src="https://img.shields.io/pypi/v/swarmauri_llm_whisper"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_whisper/pyproject.toml"><img alt="Source version: 0.11.0.dev3" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev3&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_whisper/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_whisper/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_whisper/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_whisper/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_whisper/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_llm_whisper/"><img alt="Monthly PyPI downloads: swarmauri_llm_whisper" src="https://img.shields.io/pypi/dm/swarmauri_llm_whisper"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_whisper/README.md"><img alt="README hits: swarmauri_llm_whisper" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/community/swarmauri_llm_whisper/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_whisper/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_whisper/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_llm_whisper` provides the provider-specific Swarmauri import package for `WhisperLargeModel`. Despite the older `llm` package name, the runtime is a speech-to-text adapter that calls Hugging Face Inference for `openai/whisper-large-v3` and supports both transcription and translation workflows.

The adapter targets Hugging Face Inference at `https://api-inference.huggingface.co/models/openai/whisper-large-v3`, accepts local audio file paths, and returns text output for single-file, async, and batch processing workflows.

### Why This Package

- Keep Whisper-specific imports explicit in Swarmauri applications.
- Transcribe or translate audio through a Swarmauri component instead of hand-writing Hugging Face Inference requests.
- Reuse one adapter for synchronous, asynchronous, and batch audio processing.
- Bridge older `llms` import patterns while newer `stt`-oriented package paths continue to evolve.

### When to Use

Choose `swarmauri_llm_whisper` when your integration needs provider-specific Swarmauri import package for Whisper transcription, translation, async, and batch speech-to-text workflows. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- `WhisperLargeModel` for transcription and translation against Hugging Face Inference.
- Sync and async single-file processing.
- Batch and async batch audio workflows.
- Explicit task selection between transcription and translation.
- Compatibility with Python 3.10, 3.11, 3.12, 3.13, and 3.14.

### Non-Goals

`swarmauri_llm_whisper` owns provider-specific Swarmauri import package for Whisper transcription, translation, async, and batch speech-to-text workflows. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_whisper/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. Read the example’s inputs and service requirements before execution.

### Installation

```bash
uv add swarmauri_llm_whisper
```

```bash
pip install swarmauri_llm_whisper
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_llm_whisper
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_llm_whisper
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_llm_whisper
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_whisper/docs/readme/quick_start.py).

```python
import os

from swarmauri_llm_whisper import WhisperLargeModel

model = WhisperLargeModel(api_key=os.environ["HF_API_KEY"])
text = model.predict("tests/static/test.mp3", task="transcription")

print(text)
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_llm_whisper` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_whisper/docs/readme/usage.py).

```python
import os

from swarmauri_llm_whisper import WhisperLargeModel

model = WhisperLargeModel(api_key=os.environ["HF_API_KEY"])
text = model.predict("tests/static/test.mp3", task="transcription")

print(text)
```
<!-- readme-standards:end example.usage -->

Set `HF_API_KEY` in your environment before creating the model.

**Transcription**


**Translation**

```python
import os

from swarmauri_llm_whisper import WhisperLargeModel

model = WhisperLargeModel(api_key=os.environ["HF_API_KEY"])
text = model.predict("tests/static/test_fr.mp3", task="translation")

print(text)
```

**Async Batch Processing**

```python
import asyncio
import os

from swarmauri_llm_whisper import WhisperLargeModel


async def main() -> None:
    model = WhisperLargeModel(api_key=os.environ["HF_API_KEY"])
    results = await model.abatch(
        {
            "tests/static/test.mp3": "transcription",
            "tests/static/test_fr.mp3": "translation",
        }
    )
    print(results)


# asyncio.run(main())
```

- Use `transcription` when the output should stay in the original spoken language.
- Use `translation` when the output should be translated into English.
- Use batch methods when one job needs to process multiple audio files together.

### Configuration

Configure `swarmauri_llm_whisper` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_whisper/swarmauri_llm_whisper/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_whisper/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_llm_whisper` source does not establish a package-wide exception hierarchy. Preserve errors from its declared dependencies and validate inputs using the specific public contract in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_whisper/swarmauri_llm_whisper/__init__.py).

### Best Practices

- Keep `HF_API_KEY` in environment variables or a secret manager.
- Choose `translation` only when English output is the intended downstream behavior.
- Use explicit local audio file paths and validate the file exists before dispatching a batch job.
- Prefer newer Swarmauri STT-native imports when available for new projects, since this package preserves an older compatibility surface.

---

## Package Boundary

### What It Owns

`swarmauri_llm_whisper` is located in `community` and owns provider-specific Swarmauri import package for Whisper transcription, translation, async, and batch speech-to-text workflows. Source-declared APIs include `WhisperLargeModel`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_whisper/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_llm_whisper`.

Source-declared exports or types: `WhisperLargeModel`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_whisper/swarmauri_llm_whisper/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.llms` → `WhisperLargeModel` → `swarmauri_llm_whisper.WhisperLargeModel:WhisperLargeModel`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_llm_whisper` are `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_whisper/swarmauri_llm_whisper/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_llm_whisper` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_llm_whisper`, use the source-declared public interfaces (`WhisperLargeModel`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_llm_whisper` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_whisper/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_llm_whisper`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_whisper/swarmauri_llm_whisper/__init__.py). The `swarmauri_llm_whisper` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_llm_whisper` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_llm_whisper` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/unit/test_WhisperLargeModel_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_whisper/tests/unit/test_WhisperLargeModel_unit.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_llm_whisper` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_whisper/swarmauri_llm_whisper/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**What does swarmauri_llm_whisper install?**

It installs `WhisperLargeModel` under `swarmauri.llms`.

**Is this a chat LLM package?**

No. The runtime is a speech-to-text adapter for `openai/whisper-large-v3` on Hugging Face Inference.

**Which tasks are supported?**

The adapter supports `transcription` and `translation`.

**Which model is supported today?**

The current runtime allowlist contains `openai/whisper-large-v3`.

**Does it support streaming?**

No. `stream` and `astream` are explicitly unimplemented for this adapter.

**What credentials are required?**

You need a Hugging Face access token with permission to use the target inference surface.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_llm_whisper`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_whisper/swarmauri_llm_whisper/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_llm_whisper` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

- [LLM provider model and pricing links](../../../docs/LLM_PROVIDER_MODEL_PRICING_LINKS.md)
- [openai/whisper-large-v3 model card](https://huggingface.co/openai/whisper-large-v3)
- [Hugging Face Inference Providers](https://huggingface.co/docs/inference-providers/index)

### Related Packages

- [swarmauri_llm_openai](https://pypi.org/project/swarmauri_llm_openai/)
- [OpenAI TTS (Play.ht replacement)](../../standards/swarmauri_tts_openai/README.md)
- [swarmauri_llm_groq](https://pypi.org/project/swarmauri_llm_groq/)
- [swarmauri_llm_perplexity](https://pypi.org/project/swarmauri_llm_perplexity/)
- [swarmauri_llm_hyperbolic](https://pypi.org/project/swarmauri_llm_hyperbolic/)
- [swarmauri_llm_llamacpp](https://pypi.org/project/swarmauri_llm_llamacpp/)

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_llm_whisper](https://pypi.org/project/swarmauri_llm_whisper/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_llm_whisper`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/community/swarmauri_llm_whisper` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

**Foundational Swarmauri Packages**

- [swarmauri](https://pypi.org/project/swarmauri/)
- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_llm_whisper` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_whisper/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_llm_whisper` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_llm_whisper` source version is `0.11.0.dev3`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_whisper/LICENSE).
<!-- readme-standards:end license -->

Apache-2.0

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_whisper/NOTICE) for attribution.
<!-- readme-standards:end notices -->
