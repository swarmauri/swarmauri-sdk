# swarmauri_llm_falai

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_llm_falai</strong></p>
<p align="center">Provider-specific Swarmauri import package for fal.ai queue-backed vision-language inference, OCR, image captioning, and visual question answering.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_llm_falai/"><img alt="pypi: swarmauri_llm_falai" src="https://img.shields.io/pypi/v/swarmauri_llm_falai"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_falai/pyproject.toml"><img alt="Source version: 0.11.0.dev3" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev3&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_falai/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_falai/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_falai/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_falai/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_falai/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_llm_falai/"><img alt="Monthly PyPI downloads: swarmauri_llm_falai" src="https://img.shields.io/pypi/dm/swarmauri_llm_falai"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_falai/README.md"><img alt="README hits: swarmauri_llm_falai" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/50-community/swarmauri_llm_falai/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_falai/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_falai/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_llm_falai` provides the provider-specific `FalAIVisionModel`
import for Swarmauri projects that call fal.ai vision and image-understanding
models. The adapter accepts an image URL plus a prompt, submits the request to
fal's queue-backed inference API, polls for completion, and returns the model
output string.

This package preserves the legacy LLM-package import path for fal.ai vision
workloads while keeping implementation parity with
`swarmauri_standard.llms.FalAIVisionModel`. New VLM-oriented code should also
review the newer Swarmauri VLM imports mentioned by the runtime deprecation
warning.

fal.ai's public documentation describes queue-backed inference under
`https://queue.fal.run/{model_id}`, including request submission, status polling,
and response retrieval. That maps directly to this adapter's `predict` and
`apredict` workflows.

### Why This Package

- Keep fal.ai-specific vision model dependencies isolated from the rest of a
  Swarmauri application.
- Ask questions about remote images with Swarmauri-style model components.
- Use fal's queue-backed inference lifecycle without writing queue polling logic
  in application code.
- Preserve compatibility for projects that still import `FalAIVisionModel` from
  the LLM provider package.

### When to Use

Choose `swarmauri_llm_falai` when your integration needs provider-specific Swarmauri import package for fal.ai queue-backed vision-language inference, OCR, image captioning, and visual question answering. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Provider-specific `FalAIVisionModel` import for Swarmauri projects.
- Vision-language prediction with `image_url` and `prompt` inputs.
- Queue-backed request submission and status polling through fal.ai.
- Synchronous prediction through `predict`.
- Asynchronous prediction through `apredict`.
- Configurable queue polling with `max_retries` and `retry_delay`.
- Built-in model allow list covering OCR, LLaVA, Florence, Moondream, MiniCPM,
  SA2VA, and related fal.ai vision endpoints.
- Compatibility with Python 3.10, 3.11, 3.12, 3.13, and 3.14.

### Non-Goals

`swarmauri_llm_falai` owns provider-specific Swarmauri import package for fal.ai queue-backed vision-language inference, OCR, image captioning, and visual question answering. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Create a fal.ai API key and provide it as `FalAIVisionModel(api_key=...)` or set
`FAL_KEY` in the runtime environment.

### Installation

```bash
uv add swarmauri_llm_falai
```

```bash
pip install swarmauri_llm_falai
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_llm_falai
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_llm_falai
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_llm_falai
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_falai/docs/readme/quick_start.py).

```python
from swarmauri_llm_falai import FalAIVisionModel

model = FalAIVisionModel(api_key="FAL_KEY")

answer = model.predict(
    image_url="https://llava-vl.github.io/static/images/monalisa.jpg",
    prompt="Who painted this artwork?",
)

print(answer)
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_llm_falai` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_falai/docs/readme/usage.py).

```python
from swarmauri_llm_falai import FalAIVisionModel

model = FalAIVisionModel(api_key="FAL_KEY")

answer = model.predict(
    image_url="https://llava-vl.github.io/static/images/monalisa.jpg",
    prompt="Who painted this artwork?",
)

print(answer)
```
<!-- readme-standards:end example.usage -->

**Async Vision Question Answering**

```python
import asyncio

from swarmauri_llm_falai import FalAIVisionModel


async def main() -> None:
    model = FalAIVisionModel(api_key="FAL_KEY")
    answer = await model.apredict(
        image_url="https://llava-vl.github.io/static/images/monalisa.jpg",
        prompt="Describe the subject of the painting.",
    )
    print(answer)


asyncio.run(main())
```

**Choose A fal.ai Vision Model**

```python
from swarmauri_llm_falai import FalAIVisionModel

model = FalAIVisionModel(api_key="FAL_KEY", name="fal-ai/florence-2-large/ocr")

text = model.predict(
    image_url="https://example.com/document-scan.png",
    prompt="Extract the visible text.",
)

print(text)
```

### Configuration

Configure `swarmauri_llm_falai` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_falai/swarmauri_llm_falai/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_falai/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_llm_falai` source raises `RuntimeError`, `TimeoutError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

- Store fal.ai credentials in environment variables or a secrets manager.
- Use image URLs that are reachable by the fal.ai runtime.
- Tune `max_retries` and `retry_delay` for long-running queue-backed models.
- Prefer newer Swarmauri VLM imports for new projects when available.

---

## Package Boundary

### What It Owns

`swarmauri_llm_falai` is located in `community` and owns provider-specific Swarmauri import package for fal.ai queue-backed vision-language inference, OCR, image captioning, and visual question answering. Source-declared APIs include `FalAIVisionModel`, `FalVLM`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_falai/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_llm_falai`.

Source-declared exports or types: `FalAIVisionModel`, `FalVLM`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_falai/swarmauri_llm_falai/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.llms` → `FalAIVisionModel` → `swarmauri_llm_falai.FalAIVisionModel:FalAIVisionModel`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_llm_falai` are `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_falai/swarmauri_llm_falai/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_llm_falai` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_llm_falai`, use the source-declared public interfaces (`FalAIVisionModel`, `FalVLM`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_llm_falai` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_falai/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_llm_falai`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_falai/swarmauri_llm_falai/__init__.py). The `swarmauri_llm_falai` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_llm_falai` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_llm_falai` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/unit/test_FalAIVisionModel_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_falai/tests/unit/test_FalAIVisionModel_unit.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_llm_falai` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_falai/swarmauri_llm_falai/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**What does swarmauri_llm_falai install?**

It installs a provider package that exports `FalAIVisionModel` from
`swarmauri_standard.llms.FalAIVisionModel` and registers it under the Swarmauri
LLM entry point group.

**Is this a text-only LLM package?**

No. The model accepts `image_url` and `prompt` arguments and is intended for
vision-language tasks such as OCR, image captioning, visual question answering,
and image moderation workflows supported by fal.ai models.

**Which fal.ai endpoint does it use?**

The adapter posts to `https://queue.fal.run/{model_id}`. When fal returns a
`request_id`, the adapter polls the corresponding request status endpoint until
the request is completed, then fetches the response URL.

**Which environment variable can supply credentials?**

The model default reads `FAL_KEY` when `api_key` is not passed explicitly. The
package tests also support live checks when a fal.ai key is available.

**Does this adapter support streaming?**

No. `stream` and `astream` intentionally raise `NotImplementedError` for
`FalAIVisionModel`.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_llm_falai`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_falai/swarmauri_llm_falai/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_llm_falai` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_falai/swarmauri_llm_falai/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_falai/pyproject.toml) provide the supporting context for `swarmauri_llm_falai`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_llm_deepinfra](https://pypi.org/project/swarmauri_llm_deepinfra/)
- [swarmauri_llm_gemini](https://pypi.org/project/swarmauri_llm_gemini/)
- [swarmauri_llm_openai](https://pypi.org/project/swarmauri_llm_openai/)
- [swarmauri_llm_pytesseractimg2text](https://pypi.org/project/swarmauri_llm_pytesseractimg2text/)
- [swarmauri_llm_whisper](https://pypi.org/project/swarmauri_llm_whisper/)

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_llm_falai](https://pypi.org/project/swarmauri_llm_falai/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_llm_falai`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/50-community/swarmauri_llm_falai` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

**Foundational Swarmauri Packages**

- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)
- [swarmauri](https://pypi.org/project/swarmauri/)

**Provider Documentation**

- [fal.ai asynchronous inference](https://fal.ai/docs/documentation/model-apis/inference/queue)
- [fal.ai synchronous inference](https://fal.ai/docs/documentation/model-apis/inference/synchronous)
- [fal.ai vision models](https://fal.ai/models?categories=vision)

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_llm_falai` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_falai/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_llm_falai` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_llm_falai` source version is `0.11.0.dev3`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_falai/LICENSE).
<!-- readme-standards:end license -->

Apache-2.0

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_falai/NOTICE) for attribution.
<!-- readme-standards:end notices -->
