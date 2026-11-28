# swarmauri_llm_leptonai

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_llm_leptonai</strong></p>
<p align="center">Provider-specific Swarmauri import package for Lepton AI hosted chat models, streaming workflows, and SDXL image generation.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_llm_leptonai/"><img alt="pypi: swarmauri_llm_leptonai" src="https://img.shields.io/pypi/v/swarmauri_llm_leptonai?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_leptonai/pyproject.toml"><img alt="Source version: 0.11.0" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_leptonai/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_leptonai/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_leptonai/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_leptonai/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_leptonai/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_llm_leptonai/"><img alt="Monthly PyPI downloads: swarmauri_llm_leptonai" src="https://img.shields.io/pypi/dm/swarmauri_llm_leptonai?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_leptonai/README.md"><img alt="README hits: swarmauri_llm_leptonai" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/50-community/swarmauri_llm_leptonai/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_leptonai/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_leptonai/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_llm_leptonai` provides provider-specific Swarmauri imports for Lepton AI hosted chat models and SDXL image generation. The package exposes `LeptonAIModel` for synchronous, asynchronous, streaming, and batch text generation workflows, plus `LeptonAIImgGenModel` for prompt-to-image generation against Lepton-hosted image endpoints.

The runtime uses model-specific Lepton endpoints in the form `https://<model>.lepton.run/api/v1/` for chat and `https://sdxl.lepton.run/run` for image generation. That keeps Lepton-specific configuration isolated in one provider package while preserving the shared Swarmauri `Conversation` and component model.

### Why This Package

- Keep Lepton AI imports explicit in Swarmauri applications instead of importing provider implementations from broader runtime packages.
- Run hosted chat models with sync, async, streaming, and batch interfaces that align with Swarmauri LLM conventions.
- Generate images with a Swarmauri image generation component instead of managing raw HTTP calls directly.
- Reuse shared Swarmauri message, conversation, and serialization behavior while keeping provider credentials and model names local to the Lepton package.

### When to Use

Choose `swarmauri_llm_leptonai` when your integration needs provider-specific Swarmauri import package for Lepton AI hosted chat models, streaming workflows, and SDXL image generation. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- `LeptonAIModel` for provider-hosted chat generation with sync, async, streaming, and batch execution.
- Usage metadata capture on text responses through Swarmauri `UsageData`.
- `LeptonAIImgGenModel` for prompt-to-image generation against Lepton-hosted SDXL endpoints.
- Endpoint selection derived from the configured model name for text generation workflows.
- Compatibility with Python 3.10, 3.11, 3.12, 3.13, and 3.14.

### Non-Goals

`swarmauri_llm_leptonai` owns provider-specific Swarmauri import package for Lepton AI hosted chat models, streaming workflows, and SDXL image generation. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_leptonai/pyproject.toml) declares runtime dependencies including `openai`, `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. Read the example’s inputs and service requirements before execution.

### Installation

```bash
uv add swarmauri_llm_leptonai
```

```bash
pip install swarmauri_llm_leptonai
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_llm_leptonai
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_llm_leptonai
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_llm_leptonai
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_leptonai/docs/readme/quick_start.py).

```python
import os

from swarmauri_llm_leptonai import LeptonAIModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(
    HumanMessage(content="Summarize Swarmauri in two sentences.")
)

model = LeptonAIModel(
    api_key=os.environ["LEPTON_API_KEY"],
    name="llama3-8b",
)
result = model.predict(conversation=conversation)

print(result.get_last().content)
print(result.get_last().usage.total_tokens)
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_llm_leptonai` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_leptonai/docs/readme/usage.py).

```python
import os

from swarmauri_llm_leptonai import LeptonAIModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(
    HumanMessage(content="Summarize Swarmauri in two sentences.")
)

model = LeptonAIModel(
    api_key=os.environ["LEPTON_API_KEY"],
    name="llama3-8b",
)
result = model.predict(conversation=conversation)

print(result.get_last().content)
print(result.get_last().usage.total_tokens)
```
<!-- readme-standards:end example.usage -->

Set `LEPTON_API_KEY` in your environment before creating either component.

**Chat Completion**


**Async and Streaming**

```python
import asyncio
import os

from swarmauri_llm_leptonai import LeptonAIModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage


async def ask_async(prompt: str) -> None:
    conversation = Conversation()
    conversation.add_message(HumanMessage(content=prompt))

    model = LeptonAIModel(
        api_key=os.environ["LEPTON_API_KEY"],
        name="mixtral-8x7b",
    )
    result = await model.apredict(conversation=conversation)
    print(result.get_last().content)


def stream_text(prompt: str) -> None:
    conversation = Conversation()
    conversation.add_message(HumanMessage(content=prompt))

    model = LeptonAIModel(api_key=os.environ["LEPTON_API_KEY"])
    for token in model.stream(conversation=conversation):
        print(token, end="", flush=True)


# asyncio.run(ask_async("Draft a short release note."))
# stream_text("Write a haiku about composable AI systems.")
```

**Image Generation**

```python
import os
from pathlib import Path

from swarmauri_llm_leptonai import LeptonAIImgGenModel

image_model = LeptonAIImgGenModel(
    api_key=os.environ["LEPTON_API_KEY"],
    model_name="sdxl",
)

image_bytes = image_model.generate_image(
    prompt="A cyberpunk skyline at blue hour in watercolor style",
    width=768,
    height=512,
)

output = Path("leptonai_cyberpunk.png")
image_model.save_image(image_bytes, output.as_posix())
```

- Use `LeptonAIModel` for provider-hosted chat inference when you want Swarmauri `Conversation` objects and token usage data.
- Use `LeptonAIImgGenModel` when an agent or application needs image generation without adding a separate provider package.
- Use `stream` or `astream` for latency-sensitive user interfaces that render tokens incrementally.

### Configuration

Configure `swarmauri_llm_leptonai` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_leptonai/swarmauri_llm_leptonai/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_leptonai/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_llm_leptonai` source does not establish a package-wide exception hierarchy. Preserve errors from its declared dependencies and validate inputs using the specific public contract in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_leptonai/swarmauri_llm_leptonai/__init__.py).

### Best Practices

- Keep `LEPTON_API_KEY` in environment variables or a secret manager.
- Validate current provider model availability before deploying a specific allowlisted model to production.
- Tune `width`, `height`, `steps`, and `guidance_scale` carefully for image generation to balance quality, latency, and cost.
- Consume full streaming responses before reading usage metadata from the final conversation message.

---

## Package Boundary

### What It Owns

`swarmauri_llm_leptonai` is located in `community` and owns provider-specific Swarmauri import package for Lepton AI hosted chat models, streaming workflows, and SDXL image generation. Source-declared APIs include `LeptonAIImgGenModel`, `LeptonAIModel`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_leptonai/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_llm_leptonai`.

Source-declared exports or types: `LeptonAIImgGenModel`, `LeptonAIModel`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_leptonai/swarmauri_llm_leptonai/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.image_gens` → `LeptonAIImgGenModel` → `swarmauri_llm_leptonai.LeptonAIImgGenModel:LeptonAIImgGenModel`
- `swarmauri.llms` → `LeptonAIModel` → `swarmauri_llm_leptonai.LeptonAIModel:LeptonAIModel`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_llm_leptonai` are `openai`, `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_leptonai/swarmauri_llm_leptonai/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_llm_leptonai` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_llm_leptonai`, use the source-declared public interfaces (`LeptonAIImgGenModel`, `LeptonAIModel`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_llm_leptonai` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_leptonai/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_llm_leptonai`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_leptonai/swarmauri_llm_leptonai/__init__.py). The `swarmauri_llm_leptonai` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_llm_leptonai` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_llm_leptonai` package directory for the maintained example source checks (Python compilation and non-Python file presence). Behavioral tests may live in the repository’s shared suites; the new README syntax test is not presented as runtime coverage for provider-specific Swarmauri import package for Lepton AI hosted chat models, streaming workflows, and SDXL image generation.

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_llm_leptonai` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_leptonai/swarmauri_llm_leptonai/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**What does swarmauri_llm_leptonai install?**

It installs two provider entry points: `LeptonAIModel` under `swarmauri.llms` and `LeptonAIImgGenModel` under `swarmauri.image_gens`.

**Which Lepton AI capabilities are wrapped today?**

The package currently wraps hosted chat completion style inference for the allowlisted text models in `LeptonAIModel` and SDXL image generation through `LeptonAIImgGenModel`.

**Does LeptonAIModel support streaming and async workflows?**

Yes. `LeptonAIModel` supports `predict`, `apredict`, `stream`, `astream`, `batch`, and `abatch`.

**Does the image generator support batch workflows?**

Yes. `LeptonAIImgGenModel` supports `generate_image`, `agenerate_image`, `batch_generate`, and `abatch_generate`.

### How

**How does model selection work?**

`LeptonAIModel` builds its base URL from the configured `name`, so changing `name="llama3-8b"` to another allowlisted model switches the Lepton endpoint without changing the rest of the application code.

### When

**Where should I verify current provider model availability and pricing?**

Lepton's public model and pricing documentation is limited compared with other providers. Use the provider-facing surfaces in the Lepton dashboard and review [docs/LLM_PROVIDER_MODEL_PRICING_LINKS.md](../../../docs/LLM_PROVIDER_MODEL_PRICING_LINKS.md) for the current project-level documentation links before publishing model or pricing claims.

---

## Documentation and Related Packages

### More Documentation

- [LLM provider model and pricing links](../../../docs/LLM_PROVIDER_MODEL_PRICING_LINKS.md)
- [Lepton AI playground](https://www.lepton.ai/playground)

### Related Packages

- [swarmauri_llm_openai](https://pypi.org/project/swarmauri_llm_openai/)
- [swarmauri_llm_mistral](https://pypi.org/project/swarmauri_llm_mistral/)
- [swarmauri_llm_deepinfra](https://pypi.org/project/swarmauri_llm_deepinfra/)
- [swarmauri_llm_hyperbolic](https://pypi.org/project/swarmauri_llm_hyperbolic/)
- [swarmauri_llm_falai](https://pypi.org/project/swarmauri_llm_falai/)
- [swarmauri_llm_groq](https://pypi.org/project/swarmauri_llm_groq/)

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_llm_leptonai](https://pypi.org/project/swarmauri_llm_leptonai/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_llm_leptonai`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/50-community/swarmauri_llm_leptonai` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

**Foundational Swarmauri Packages**

- [swarmauri](https://pypi.org/project/swarmauri/)
- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_llm_leptonai` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_leptonai/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_llm_leptonai` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_llm_leptonai` source version is `0.11.0`.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_leptonai/LICENSE).
<!-- readme-standards:end license -->

Apache-2.0

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_leptonai/NOTICE) for attribution.
<!-- readme-standards:end notices -->
