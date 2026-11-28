# swarmauri_llm_cerebras

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_llm_cerebras</strong></p>
<p align="center">Provider-specific Swarmauri import package for Cerebras Inference chat completions with sync, async, streaming, batch, and JSON workflows.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_llm_cerebras/"><img alt="pypi: swarmauri_llm_cerebras" src="https://img.shields.io/pypi/v/swarmauri_llm_cerebras?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_cerebras/pyproject.toml"><img alt="Source version: 0.11.0" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_cerebras/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_cerebras/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_cerebras/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_cerebras/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_cerebras/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_llm_cerebras/"><img alt="Monthly PyPI downloads: swarmauri_llm_cerebras" src="https://img.shields.io/pypi/dm/swarmauri_llm_cerebras?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_cerebras/README.md"><img alt="README hits: swarmauri_llm_cerebras" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/50-community/swarmauri_llm_cerebras/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_cerebras/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_cerebras/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_llm_cerebras` provides the `CerebrasModel` import path for Swarmauri applications that use Cerebras Inference chat completions. The package re-exports the maintained implementation from `swarmauri_standard`, giving projects a provider-specific dependency for Cerebras-hosted Llama, Qwen, and GPT-OSS style model workflows.

### Why This Package

Use this package when you want Cerebras Inference behind the Swarmauri `LLMBase` interface. `CerebrasModel` formats Swarmauri conversations for the Cerebras chat completions endpoint, supports sync and async prediction, streams response deltas, runs sequential and concurrent batches, captures usage data, and exposes model options such as temperature, top-p, seed, stop sequences, and JSON output mode.

### When to Use

Choose `swarmauri_llm_cerebras` when your integration needs provider-specific Swarmauri import package for Cerebras Inference chat completions with sync, async, streaming, batch, and JSON workflows. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Provider-specific import: `from swarmauri_llm_cerebras import CerebrasModel`.
- Swarmauri `Conversation`, `HumanMessage`, `SystemMessage`, and `AgentMessage` integration.
- Sync `predict()` and async `apredict()` chat completion calls.
- Sync `stream()` and async `astream()` streaming deltas.
- Sync `batch()` and async `abatch()` helpers.
- Configurable `temperature`, `max_completion_tokens`, `top_p`, `seed`, `stop`, and `enable_json`.
- Usage metadata mapping to Swarmauri `UsageData` when provider usage data is returned.
- Model discovery through the Cerebras `/v1/models` endpoint.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

### Non-Goals

`swarmauri_llm_cerebras` owns provider-specific Swarmauri import package for Cerebras Inference chat completions with sync, async, streaming, batch, and JSON workflows. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

- Cerebras Inference API key.
- Network access to `api.cerebras.ai`.
- Swarmauri conversations built from Swarmauri message classes.

### Installation

Install with `uv`:

```bash
uv add swarmauri_llm_cerebras
```

Install with `pip`:

```bash
pip install swarmauri_llm_cerebras
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_llm_cerebras
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_llm_cerebras
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_llm_cerebras
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_cerebras/docs/readme/quick_start.py).

```python
import os

from swarmauri_llm_cerebras import CerebrasModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage
from swarmauri_standard.messages.SystemMessage import SystemMessage

conversation = Conversation()
conversation.add_message(
    SystemMessage(content="Answer with concise technical prose.")
)
conversation.add_message(HumanMessage(content="What is Cerebras Inference?"))

model = CerebrasModel(
    api_key=os.environ["CEREBRAS_API_KEY"],
    name="llama3.1-8b",
)
result = model.predict(
    conversation=conversation,
    temperature=0.2,
    max_completion_tokens=256,
)

print(result.get_last().content)
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_llm_cerebras` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_cerebras/docs/readme/usage.py).

```python
import os

from swarmauri_llm_cerebras import CerebrasModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage
from swarmauri_standard.messages.SystemMessage import SystemMessage

conversation = Conversation()
conversation.add_message(
    SystemMessage(content="Answer with concise technical prose.")
)
conversation.add_message(HumanMessage(content="What is Cerebras Inference?"))

model = CerebrasModel(
    api_key=os.environ["CEREBRAS_API_KEY"],
    name="llama3.1-8b",
)
result = model.predict(
    conversation=conversation,
    temperature=0.2,
    max_completion_tokens=256,
)

print(result.get_last().content)
```
<!-- readme-standards:end example.usage -->

Run a chat completion:


Stream response deltas:

```python
import os

from swarmauri_llm_cerebras import CerebrasModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(HumanMessage(content="Write a short product summary."))

model = CerebrasModel(api_key=os.environ["CEREBRAS_API_KEY"])

for token in model.stream(conversation=conversation, max_completion_tokens=180):
    print(token, end="")
```

Use the async API:

```python
import asyncio
import os

from swarmauri_llm_cerebras import CerebrasModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage


async def main() -> None:
    conversation = Conversation()
    conversation.add_message(HumanMessage(content="Return JSON with a status field."))

    model = CerebrasModel(api_key=os.environ["CEREBRAS_API_KEY"])
    result = await model.apredict(conversation=conversation, enable_json=True)

    print(result.get_last().content)


asyncio.run(main())
```

### Configuration

Configure `swarmauri_llm_cerebras` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_cerebras/swarmauri_llm_cerebras/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_cerebras/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_llm_cerebras` source does not establish a package-wide exception hierarchy. Preserve errors from its declared dependencies and validate inputs using the specific public contract in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_cerebras/swarmauri_llm_cerebras/__init__.py).

### Best Practices

- Store `CEREBRAS_API_KEY` in a secret manager or environment variable.
- Set `name` explicitly for reproducible model behavior.
- Use `seed` when deterministic replay matters for supported models.
- Use async methods for high-concurrency workloads.
- Validate JSON mode outputs before feeding them into strict downstream parsers.

---

## Package Boundary

### What It Owns

`swarmauri_llm_cerebras` is located in `community` and owns provider-specific Swarmauri import package for Cerebras Inference chat completions with sync, async, streaming, batch, and JSON workflows. Source-declared APIs include `CerebrasModel`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_cerebras/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_llm_cerebras`.

Source-declared exports or types: `CerebrasModel`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_cerebras/swarmauri_llm_cerebras/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.llms` → `CerebrasModel` → `swarmauri_llm_cerebras.CerebrasModel:CerebrasModel`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_llm_cerebras` are `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_cerebras/swarmauri_llm_cerebras/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_llm_cerebras` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_llm_cerebras`, use the source-declared public interfaces (`CerebrasModel`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_llm_cerebras` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_cerebras/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_llm_cerebras`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_cerebras/swarmauri_llm_cerebras/__init__.py). The `swarmauri_llm_cerebras` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_llm_cerebras` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_llm_cerebras` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/unit/test_CerebrasModel_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_cerebras/tests/unit/test_CerebrasModel_unit.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_llm_cerebras` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_cerebras/swarmauri_llm_cerebras/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Q: Which Cerebras endpoint does this adapter call?**

A: The adapter posts to `https://api.cerebras.ai/v1/chat/completions` and uses bearer-token authentication with a Cerebras API key.

**Q: Which model names are configured locally?**

A: The current configured list includes `llama-4-scout-17b-16e-instruct`, `llama3.1-8b`, `llama-3.3-70b`, `llama-4-maverick-17b-128e-instruct`, `qwen-3-32b`, `qwen-3-coder-480b`, and `gpt-oss-120b`. The default is `llama3.1-8b`.

**Q: Does this package contain a separate Cerebras implementation?**

A: No. It re-exports `CerebrasModel` from `swarmauri_standard.llms.CerebrasModel` so applications can depend on this provider package while sharing the common implementation.

### How

**Q: How do I request JSON output?**

A: Pass `enable_json=True` to `predict()`, `apredict()`, `stream()`, or `astream()`. The adapter sets `response_format` to `json_object`.

### When

**When should I validate an upgrade?** Recheck `swarmauri_llm_cerebras` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_cerebras/swarmauri_llm_cerebras/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_cerebras/pyproject.toml) provide the supporting context for `swarmauri_llm_cerebras`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

LLM provider packages:

- [swarmauri_llm_ai21](https://pypi.org/project/swarmauri_llm_ai21/)
- [swarmauri_llm_anthropic](https://pypi.org/project/swarmauri_llm_anthropic/)
- [swarmauri_llm_cohere](https://pypi.org/project/swarmauri_llm_cohere/)
- [swarmauri_llm_deepinfra](https://pypi.org/project/swarmauri_llm_deepinfra/)
- [swarmauri_llm_groq](https://pypi.org/project/swarmauri_llm_groq/)
- [swarmauri_llm_mistral](https://pypi.org/project/swarmauri_llm_mistral/)
- [swarmauri_llm_openai](https://pypi.org/project/swarmauri_llm_openai/)

Foundational packages:

- [swarmauri_core](https://pypi.org/project/swarmauri_core/) defines core interfaces.
- [swarmauri_base](https://pypi.org/project/swarmauri_base/) provides base component classes.
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/) contains the shared `CerebrasModel` implementation.
- [swarmauri](https://pypi.org/project/swarmauri/) provides namespace imports and plugin discovery.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_llm_cerebras](https://pypi.org/project/swarmauri_llm_cerebras/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_llm_cerebras`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/50-community/swarmauri_llm_cerebras` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_llm_cerebras` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_llm_cerebras` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_cerebras/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_llm_cerebras` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_llm_cerebras` source version is `0.11.0`.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_cerebras/LICENSE).
<!-- readme-standards:end license -->

Apache-2.0

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_cerebras/NOTICE) for attribution.
<!-- readme-standards:end notices -->
