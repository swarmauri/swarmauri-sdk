# swarmauri_llm_hyperbolic

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_llm_hyperbolic</strong></p>
<p align="center">Provider-specific Swarmauri import package for Hyperbolic OpenAI-compatible chat, vision-language inference, streaming, with retired audio imports retained for compatibility.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_llm_hyperbolic/"><img alt="pypi: swarmauri_llm_hyperbolic" src="https://img.shields.io/pypi/v/swarmauri_llm_hyperbolic"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_hyperbolic/pyproject.toml"><img alt="Source version: 0.11.0.dev4" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev4&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_hyperbolic/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_hyperbolic/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_hyperbolic/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_hyperbolic/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_hyperbolic/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_llm_hyperbolic/"><img alt="Monthly PyPI downloads: swarmauri_llm_hyperbolic" src="https://img.shields.io/pypi/dm/swarmauri_llm_hyperbolic"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_hyperbolic/README.md"><img alt="README hits: swarmauri_llm_hyperbolic" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/50-community/swarmauri_llm_hyperbolic/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_hyperbolic/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_hyperbolic/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_llm_hyperbolic` preserves Hyperbolic chat and vision imports and the
retired `HyperbolicAudioTTS` name. The old `.xyz/v1` API was decommissioned.
The current Hyperbolic inference service documents text and vision, with new
endpoints and credentials; it does not document a compatible audio replacement.

`HyperbolicAudioTTS` now warns and raises a local retirement error on construction
or execution. No audio request is sent. Select a standalone TTS adapter from the
[SDK migration guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/docs/migrations/playht.md).

The chat and vision implementations have not been migrated or live-verified in
this TTS update. Their presence here does not establish current availability.
See [Hyperbolic's migration notice](https://www.hyperbolic.ai/docs/inference/overview#moving-from-the-previous-inference-api).

### Why This Package

`swarmauri_llm_hyperbolic` isolates this responsibility: Provider-specific Swarmauri import package for Hyperbolic OpenAI-compatible chat, vision-language inference, streaming, with retired audio imports retained for compatibility. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_hyperbolic/swarmauri_llm_hyperbolic/__init__.py) exposes `HyperbolicAudioTTS`, `HyperbolicModel`, `HyperbolicVLM`, `HyperbolicVisionModel`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_llm_hyperbolic` when your integration needs provider-specific Swarmauri import package for Hyperbolic OpenAI-compatible chat, vision-language inference, streaming, with retired audio imports retained for compatibility. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- `HyperbolicModel` for sync, async, streaming, and batch chat completion
  workflows.
- `HyperbolicVisionModel` for image-plus-text prompts against Hyperbolic VLMs.
- `HyperbolicAudioTTS` as an import-compatible retired type; it does not call
  the decommissioned audio API.
- Model discovery through Hyperbolic's `/models` endpoint.
- Generation controls including `temperature`, `max_tokens`, `top_p`, `top_k`,
  and `stop`.
- Optional usage metadata handling on chat responses when available.
- Compatibility with Python 3.10, 3.11, 3.12, 3.13, and 3.14.

### Non-Goals

`swarmauri_llm_hyperbolic` owns provider-specific Swarmauri import package for Hyperbolic OpenAI-compatible chat, vision-language inference, streaming, with retired audio imports retained for compatibility. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Create a Hyperbolic API key in the Hyperbolic app and pass it to the model
constructor as `api_key=...`.

### Installation

```bash
uv add swarmauri_llm_hyperbolic
```

```bash
pip install swarmauri_llm_hyperbolic
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_llm_hyperbolic
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_llm_hyperbolic
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_llm_hyperbolic
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_hyperbolic/docs/readme/quick_start.py).

```python
from swarmauri_llm_hyperbolic import HyperbolicModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(
    HumanMessage(content="Summarize this deployment risk.")
)

model = HyperbolicModel(api_key="HYPERBOLIC_API_KEY")
result = model.predict(conversation=conversation, max_tokens=200)

print(result.get_last().content)
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_llm_hyperbolic` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_hyperbolic/docs/readme/usage.py).

```python
from swarmauri_llm_hyperbolic import HyperbolicModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(
    HumanMessage(content="Summarize this deployment risk.")
)

model = HyperbolicModel(api_key="HYPERBOLIC_API_KEY")
result = model.predict(conversation=conversation, max_tokens=200)

print(result.get_last().content)
```
<!-- readme-standards:end example.usage -->

**Streaming Chat**

```python
from swarmauri_llm_hyperbolic import HyperbolicModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(HumanMessage(content="List three API gateway checks."))

model = HyperbolicModel(api_key="HYPERBOLIC_API_KEY")

for token in model.stream(conversation=conversation):
    print(token, end="")
```

**Vision-Language Prompt**

```python
from swarmauri_llm_hyperbolic import HyperbolicVisionModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(
    HumanMessage(
        content=[
            {"type": "text", "text": "Describe the image."},
            {"type": "image_url", "image_url": {"url": "https://example.com/image.jpg"}},
        ]
    )
)

model = HyperbolicVisionModel(api_key="HYPERBOLIC_API_KEY")
result = model.predict(conversation=conversation)

print(result.get_last().content)
```

**Text To Speech (retired)**

Do not construct HyperbolicAudioTTS or HyperbolicTTS: the legacy API was
decommissioned. Imports remain, but use emits a warning and raises a local
migration error. See [the SDK guide](../../../docs/migrations/playht.md) and
[Hyperbolic's migration notice](https://www.hyperbolic.ai/docs/inference/overview#moving-from-the-previous-inference-api).

### Configuration

Configure `swarmauri_llm_hyperbolic` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_hyperbolic/swarmauri_llm_hyperbolic/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_hyperbolic/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_llm_hyperbolic` source does not establish a package-wide exception hierarchy. Preserve errors from its declared dependencies and validate inputs using the specific public contract in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_hyperbolic/swarmauri_llm_hyperbolic/__init__.py).

### Best Practices

- Store Hyperbolic API keys in environment variables or a secrets manager.
- Confirm model availability and provider capability flags before production
  deployment.
- Use `HyperbolicVisionModel` only for image-aware prompts; plain chat is simpler
  with `HyperbolicModel`.
- Use explicit output paths for TTS generation so generated audio files are easy
  to manage.
- Prefer newer Swarmauri VLM and TTS imports for new projects when available.

---

## Package Boundary

### What It Owns

`swarmauri_llm_hyperbolic` is located in `community` and owns provider-specific Swarmauri import package for Hyperbolic OpenAI-compatible chat, vision-language inference, streaming, with retired audio imports retained for compatibility. Source-declared APIs include `HyperbolicAudioTTS`, `HyperbolicModel`, `HyperbolicVLM`, `HyperbolicVisionModel`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_hyperbolic/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_llm_hyperbolic`.

Source-declared exports or types: `HyperbolicAudioTTS`, `HyperbolicModel`, `HyperbolicVLM`, `HyperbolicVisionModel`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_hyperbolic/swarmauri_llm_hyperbolic/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.llms` → `HyperbolicAudioTTS` → `swarmauri_llm_hyperbolic.HyperbolicAudioTTS:HyperbolicAudioTTS`
- `swarmauri.llms` → `HyperbolicModel` → `swarmauri_llm_hyperbolic.HyperbolicModel:HyperbolicModel`
- `swarmauri.llms` → `HyperbolicVisionModel` → `swarmauri_llm_hyperbolic.HyperbolicVisionModel:HyperbolicVisionModel`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_llm_hyperbolic` are `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_hyperbolic/swarmauri_llm_hyperbolic/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_llm_hyperbolic` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_llm_hyperbolic`, use the source-declared public interfaces (`HyperbolicAudioTTS`, `HyperbolicModel`, `HyperbolicVLM`, `HyperbolicVisionModel`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_llm_hyperbolic` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_hyperbolic/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_llm_hyperbolic`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_hyperbolic/swarmauri_llm_hyperbolic/__init__.py). The `swarmauri_llm_hyperbolic` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_llm_hyperbolic` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_llm_hyperbolic` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/unit/test_HyperbolicAudioTTS_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_hyperbolic/tests/unit/test_HyperbolicAudioTTS_unit.py)
- [tests/unit/test_HyperbolicModel_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_hyperbolic/tests/unit/test_HyperbolicModel_unit.py)
- [tests/unit/test_HyperbolicVisionModel_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_hyperbolic/tests/unit/test_HyperbolicVisionModel_unit.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_llm_hyperbolic` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_hyperbolic/swarmauri_llm_hyperbolic/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_llm_hyperbolic` provides provider-specific Swarmauri import package for Hyperbolic OpenAI-compatible chat, vision-language inference, streaming, with retired audio imports retained for compatibility; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_llm_hyperbolic`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_hyperbolic/swarmauri_llm_hyperbolic/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_llm_hyperbolic` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_hyperbolic/swarmauri_llm_hyperbolic/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_hyperbolic/pyproject.toml) provide the supporting context for `swarmauri_llm_hyperbolic`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_llm_deepinfra](https://pypi.org/project/swarmauri_llm_deepinfra/)
- [swarmauri_llm_groq](https://pypi.org/project/swarmauri_llm_groq/)
- [swarmauri_llm_mistral](https://pypi.org/project/swarmauri_llm_mistral/)
- [swarmauri_llm_openai](https://pypi.org/project/swarmauri_llm_openai/)
- [swarmauri_llm_perplexity](https://pypi.org/project/swarmauri_llm_perplexity/)
- [OpenAI TTS (Play.ht replacement)](../../40-standards/swarmauri_tts_openai/README.md)

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_llm_hyperbolic](https://pypi.org/project/swarmauri_llm_hyperbolic/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_llm_hyperbolic`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/50-community/swarmauri_llm_hyperbolic` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

**Foundational Swarmauri Packages**

- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)
- [swarmauri](https://pypi.org/project/swarmauri/)

**Provider Documentation**

- [Hyperbolic quick start](https://www.hyperbolic.ai/docs/inference/quickstart)
- [Hyperbolic text generation APIs](https://www.hyperbolic.ai/docs/inference/text-apis)
- [Hyperbolic vision-language APIs](https://www.hyperbolic.ai/docs/inference/vlm-apis)
- [Hyperbolic supported models](https://docs.hyperbolic.xyz/docs/supported-models)

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_llm_hyperbolic` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_hyperbolic/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_llm_hyperbolic` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_llm_hyperbolic` source version is `0.11.0.dev4`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_hyperbolic/LICENSE).
<!-- readme-standards:end license -->

Apache-2.0



The audio retirement does not redirect API keys or rewrite the other LLM/VLM
components. Those legacy integrations need their own provider migration and
verification; this update does not claim their current hosted availability.

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_hyperbolic/NOTICE) for attribution.
<!-- readme-standards:end notices -->
