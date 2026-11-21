# swarmauri_llm_perplexity

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_llm_perplexity</strong></p>
<p align="center">Provider-specific Swarmauri import package for Perplexity chat, streaming, async, batch, and citation-aware LLM workflows.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_llm_perplexity/"><img alt="pypi: swarmauri_llm_perplexity" src="https://img.shields.io/pypi/v/swarmauri_llm_perplexity"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_perplexity/pyproject.toml"><img alt="Source version: 0.11.0.dev3" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev3&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_perplexity/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_perplexity/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_perplexity/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_perplexity/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_perplexity/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_llm_perplexity/"><img alt="Monthly PyPI downloads: swarmauri_llm_perplexity" src="https://img.shields.io/pypi/dm/swarmauri_llm_perplexity"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_perplexity/README.md"><img alt="README hits: swarmauri_llm_perplexity" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/community/swarmauri_llm_perplexity/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_perplexity/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_perplexity/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_llm_perplexity` provides the provider-specific Swarmauri import package for `PerplexityModel`. It wraps Perplexity's chat completion API so Swarmauri applications can use the tracked `sonar` and `r1-1776` model families through the standard `Conversation` workflow.

The runtime targets `https://api.perplexity.ai/chat/completions`, supports sync, async, streaming, and batch generation, and exposes controls such as `return_citations`, `top_p`, `top_k`, `presence_penalty`, and `frequency_penalty`.

### Why This Package

- Keep Perplexity-specific imports explicit in Swarmauri applications.
- Use Swarmauri `Conversation` objects against Perplexity's hosted chat completion API.
- Stream Perplexity responses while preserving the same component model used across other provider packages.
- Access Perplexity's current repo-tracked `sonar` and reasoning model families from a dedicated package boundary.

### When to Use

Choose `swarmauri_llm_perplexity` when your integration needs provider-specific Swarmauri import package for Perplexity chat, streaming, async, batch, and citation-aware LLM workflows. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- `PerplexityModel` import package for hosted Perplexity chat completion workflows.
- Sync, async, streaming, and batch generation support.
- Optional citation-return behavior for supported Perplexity responses.
- Usage metadata capture through Swarmauri `UsageData` when enabled.
- Compatibility with Python 3.10, 3.11, 3.12, 3.13, and 3.14.

### Non-Goals

`swarmauri_llm_perplexity` owns provider-specific Swarmauri import package for Perplexity chat, streaming, async, batch, and citation-aware LLM workflows. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_perplexity/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. Read the example’s inputs and service requirements before execution.

### Installation

```bash
uv add swarmauri_llm_perplexity
```

```bash
pip install swarmauri_llm_perplexity
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_llm_perplexity
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_llm_perplexity
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_llm_perplexity
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_perplexity/docs/readme/quick_start.py).

```python
import os

from swarmauri_llm_perplexity import PerplexityModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(
    HumanMessage(content="Summarize Swarmauri in two sentences.")
)

model = PerplexityModel(
    api_key=os.environ["PPLX_API_KEY"],
    name="sonar",
)
result = model.predict(conversation=conversation, max_tokens=200)

print(result.get_last().content)
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_llm_perplexity` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_perplexity/docs/readme/usage.py).

```python
import os

from swarmauri_llm_perplexity import PerplexityModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(
    HumanMessage(content="Summarize Swarmauri in two sentences.")
)

model = PerplexityModel(
    api_key=os.environ["PPLX_API_KEY"],
    name="sonar",
)
result = model.predict(conversation=conversation, max_tokens=200)

print(result.get_last().content)
```
<!-- readme-standards:end example.usage -->

Set `PPLX_API_KEY` in your environment before creating the model.

**Chat Completion**


**Streaming**

```python
import os

from swarmauri_llm_perplexity import PerplexityModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(HumanMessage(content="List three differences between hosted and local inference."))

model = PerplexityModel(
    api_key=os.environ["PPLX_API_KEY"],
    name="sonar-reasoning",
)

for token in model.stream(conversation=conversation, return_citations=True):
    print(token, end="", flush=True)
```

**Async**

```python
import asyncio
import os

from swarmauri_llm_perplexity import PerplexityModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage


async def main() -> None:
    conversation = Conversation()
    conversation.add_message(HumanMessage(content="Explain retrieval-augmented generation briefly."))

    model = PerplexityModel(
        api_key=os.environ["PPLX_API_KEY"],
        name="sonar-pro",
    )
    result = await model.apredict(conversation=conversation, return_citations=True)
    print(result.get_last().content)


# asyncio.run(main())
```

- Use `sonar` for general-purpose hosted Perplexity chat workflows.
- Use `sonar-reasoning` or `sonar-reasoning-pro` when you want the reasoning-oriented family explicitly.
- Use `return_citations=True` when the downstream experience should expose provider citations alongside the generated response.

### Configuration

Configure `swarmauri_llm_perplexity` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_perplexity/swarmauri_llm_perplexity/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_perplexity/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_llm_perplexity` source does not establish a package-wide exception hierarchy. Preserve errors from its declared dependencies and validate inputs using the specific public contract in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_perplexity/swarmauri_llm_perplexity/__init__.py).

### Best Practices

- Keep `PPLX_API_KEY` in environment variables or a secret manager.
- Choose the Perplexity model family intentionally, especially when switching between search-style and reasoning-oriented variants.
- Do not set both `top_p` and `top_k` in the same request.
- Use citation-return mode only when the consuming application is prepared to surface or process citation metadata.

---

## Package Boundary

### What It Owns

`swarmauri_llm_perplexity` is located in `community` and owns provider-specific Swarmauri import package for Perplexity chat, streaming, async, batch, and citation-aware LLM workflows. Source-declared APIs include `PerplexityModel`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_perplexity/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_llm_perplexity`.

Source-declared exports or types: `PerplexityModel`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_perplexity/swarmauri_llm_perplexity/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.llms` → `PerplexityModel` → `swarmauri_llm_perplexity.PerplexityModel:PerplexityModel`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_llm_perplexity` are `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_perplexity/swarmauri_llm_perplexity/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_llm_perplexity` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_llm_perplexity`, use the source-declared public interfaces (`PerplexityModel`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_llm_perplexity` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_perplexity/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_llm_perplexity`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_perplexity/swarmauri_llm_perplexity/__init__.py). The `swarmauri_llm_perplexity` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_llm_perplexity` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_llm_perplexity` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/unit/test_PerplexityModel_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_perplexity/tests/unit/test_PerplexityModel_unit.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_llm_perplexity` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_perplexity/swarmauri_llm_perplexity/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**What does swarmauri_llm_perplexity install?**

It installs `PerplexityModel` under `swarmauri.llms`.

**Which Perplexity model families are tracked?**

The current runtime allowlist includes `sonar-deep-research`, `sonar-reasoning-pro`, `sonar-reasoning`, `sonar-pro`, `sonar`, and `r1-1776`.

**Does the package support streaming?**

Yes. `PerplexityModel` supports `predict`, `apredict`, `stream`, `astream`, `batch`, and `abatch`.

**Can it request citations?**

Yes. The runtime exposes a `return_citations` option so the provider can include citation data when supported by the selected model.

**Can I set both top_p and top_k?**

No. The runtime rejects that combination and raises a `ValueError`.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_llm_perplexity`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_perplexity/swarmauri_llm_perplexity/__init__.py) for the exact types and signatures involved.

### When

**Where should I verify current model and pricing details?**

Use the Perplexity section in [docs/LLM_PROVIDER_MODEL_PRICING_LINKS.md](../../../docs/LLM_PROVIDER_MODEL_PRICING_LINKS.md), which links to the current model cards and pricing documentation.

---

## Documentation and Related Packages

### More Documentation

- [LLM provider model and pricing links](../../../docs/LLM_PROVIDER_MODEL_PRICING_LINKS.md)
- [Perplexity model cards](https://docs.perplexity.ai/guides/model-cards)
- [Perplexity pricing](https://docs.perplexity.ai/docs/getting-started/pricing)

### Related Packages

- [swarmauri_llm_openai](https://pypi.org/project/swarmauri_llm_openai/)
- [swarmauri_llm_mistral](https://pypi.org/project/swarmauri_llm_mistral/)
- [swarmauri_llm_groq](https://pypi.org/project/swarmauri_llm_groq/)
- [swarmauri_llm_hyperbolic](https://pypi.org/project/swarmauri_llm_hyperbolic/)
- [swarmauri_llm_deepinfra](https://pypi.org/project/swarmauri_llm_deepinfra/)
- [OpenAI TTS (Play.ht replacement)](../../standards/swarmauri_tts_openai/README.md)

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_llm_perplexity](https://pypi.org/project/swarmauri_llm_perplexity/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_llm_perplexity`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/community/swarmauri_llm_perplexity` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

**Foundational Swarmauri Packages**

- [swarmauri](https://pypi.org/project/swarmauri/)
- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_llm_perplexity` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_perplexity/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_llm_perplexity` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_llm_perplexity` source version is `0.11.0.dev3`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_perplexity/LICENSE).
<!-- readme-standards:end license -->

Apache-2.0

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_llm_perplexity/NOTICE) for attribution.
<!-- readme-standards:end notices -->
