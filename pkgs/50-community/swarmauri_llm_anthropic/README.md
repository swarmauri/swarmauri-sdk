# swarmauri_llm_anthropic

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_llm_anthropic</strong></p>
<p align="center">Provider-specific Swarmauri imports for Anthropic Claude Messages API chat, streaming, async, batch, and tool-use workflows.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_llm_anthropic/"><img alt="pypi: swarmauri_llm_anthropic" src="https://img.shields.io/pypi/v/swarmauri_llm_anthropic?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_anthropic/pyproject.toml"><img alt="Source version: 0.11.0.dev3" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev3&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_anthropic/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_anthropic/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_anthropic/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_anthropic/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_anthropic/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_llm_anthropic/"><img alt="Monthly PyPI downloads: swarmauri_llm_anthropic" src="https://img.shields.io/pypi/dm/swarmauri_llm_anthropic?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_anthropic/README.md"><img alt="README hits: swarmauri_llm_anthropic" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/50-community/swarmauri_llm_anthropic/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_anthropic/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_anthropic/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_llm_anthropic` provides provider-specific imports for Anthropic Claude models in Swarmauri. It re-exports `AnthropicModel` for standard Messages API chat workflows and `AnthropicToolModel` for tool-assisted conversations, both backed by the maintained implementations in `swarmauri_standard`.

### Why This Package

Use this package when a Swarmauri application should depend explicitly on Anthropic Claude support while keeping the shared Swarmauri conversation and tool abstractions. The adapters send requests to Anthropic's `/v1/messages` endpoint, handle system-message extraction, support sync and async prediction, stream server-sent events, map token usage into Swarmauri `UsageData`, and connect Swarmauri toolkits to Anthropic tool schemas.

### When to Use

Choose `swarmauri_llm_anthropic` when your integration needs provider-specific Swarmauri imports for Anthropic Claude Messages API chat, streaming, async, batch, and tool-use workflows. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Provider-specific imports for `AnthropicModel` and `AnthropicToolModel`.
- Swarmauri `Conversation`, message, toolkit, and usage-data integration.
- Sync `predict()` and async `apredict()` message generation.
- Sync `stream()` and async `astream()` event streaming.
- Sync `batch()` and async `abatch()` helpers for multiple conversations.
- System-message extraction into Anthropic's top-level `system` field for `AnthropicModel`.
- Toolkit schema conversion for `AnthropicToolModel`.
- Retry handling for rate-limit and overloaded-provider status codes on the standard model.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

### Non-Goals

`swarmauri_llm_anthropic` owns provider-specific Swarmauri imports for Anthropic Claude Messages API chat, streaming, async, batch, and tool-use workflows. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

- Anthropic API key from the Anthropic Console.
- Network access to `api.anthropic.com`.
- Swarmauri conversations and messages.
- Swarmauri `Toolkit` objects when using `AnthropicToolModel`.

### Installation

Install with `uv`:

```bash
uv add swarmauri_llm_anthropic
```

Install with `pip`:

```bash
pip install swarmauri_llm_anthropic
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_llm_anthropic
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_llm_anthropic
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_llm_anthropic
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_anthropic/docs/readme/quick_start.py).

```python
import os

from swarmauri_llm_anthropic import AnthropicModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage
from swarmauri_standard.messages.SystemMessage import SystemMessage

conversation = Conversation()
conversation.add_message(
    SystemMessage(content="Answer in concise technical prose.")
)
conversation.add_message(HumanMessage(content="What is Swarmauri?"))

model = AnthropicModel(
    api_key=os.environ["ANTHROPIC_API_KEY"],
    name="claude-sonnet-4-0",
)
result = model.predict(
    conversation=conversation, max_tokens=256, temperature=0.2
)

print(result.get_last().content)
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_llm_anthropic` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_anthropic/docs/readme/usage.py).

```python
import os

from swarmauri_llm_anthropic import AnthropicModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage
from swarmauri_standard.messages.SystemMessage import SystemMessage

conversation = Conversation()
conversation.add_message(
    SystemMessage(content="Answer in concise technical prose.")
)
conversation.add_message(HumanMessage(content="What is Swarmauri?"))

model = AnthropicModel(
    api_key=os.environ["ANTHROPIC_API_KEY"],
    name="claude-sonnet-4-0",
)
result = model.predict(
    conversation=conversation, max_tokens=256, temperature=0.2
)

print(result.get_last().content)
```
<!-- readme-standards:end example.usage -->

Run a standard Claude Messages API request:


Stream a Claude response:

```python
import os

from swarmauri_llm_anthropic import AnthropicModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = Conversation()
conversation.add_message(HumanMessage(content="Draft a short API changelog entry."))

model = AnthropicModel(api_key=os.environ["ANTHROPIC_API_KEY"])

for token in model.stream(conversation=conversation, max_tokens=200):
    print(token, end="")
```

Use the tool model with a Swarmauri toolkit:

```python
import os

from swarmauri_llm_anthropic import AnthropicToolModel
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage
from swarmauri_standard.toolkits.Toolkit import Toolkit

toolkit = Toolkit()
# toolkit.add_tool(...)

conversation = Conversation()
conversation.add_message(HumanMessage(content="Use an available tool if needed."))

model = AnthropicToolModel(api_key=os.environ["ANTHROPIC_API_KEY"])
result = model.predict(conversation=conversation, toolkit=toolkit)

print(result.get_last().content)
```

### Configuration

Configure `swarmauri_llm_anthropic` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_anthropic/swarmauri_llm_anthropic/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_anthropic/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_llm_anthropic` source does not establish a package-wide exception hierarchy. Preserve errors from its declared dependencies and validate inputs using the specific public contract in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_anthropic/swarmauri_llm_anthropic/__init__.py).

### Best Practices

- Store `ANTHROPIC_API_KEY` in a secret manager or environment variable.
- Set `name` explicitly for reproducible model behavior.
- Use async methods for high-concurrency service workloads.
- Keep system instructions in `SystemMessage` so the standard model can map them to Anthropic's `system` field.
- Test tool schemas before production use so Anthropic tool calls map cleanly to Swarmauri toolkit functions.

---

## Package Boundary

### What It Owns

`swarmauri_llm_anthropic` is located in `community` and owns provider-specific Swarmauri imports for Anthropic Claude Messages API chat, streaming, async, batch, and tool-use workflows. Source-declared APIs include `AnthropicModel`, `AnthropicToolModel`, `AnthropicVLM`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_anthropic/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_llm_anthropic`.

Source-declared exports or types: `AnthropicModel`, `AnthropicToolModel`, `AnthropicVLM`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_anthropic/swarmauri_llm_anthropic/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.llms` → `AnthropicModel` → `swarmauri_llm_anthropic.AnthropicModel:AnthropicModel`
- `swarmauri.tool_llms` → `AnthropicToolModel` → `swarmauri_llm_anthropic.AnthropicToolModel:AnthropicToolModel`
- `swarmauri.vlms` → `AnthropicVLM` → `swarmauri_llm_anthropic.AnthropicVLM:AnthropicVLM`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_llm_anthropic` are `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_anthropic/swarmauri_llm_anthropic/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_llm_anthropic` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_llm_anthropic`, use the source-declared public interfaces (`AnthropicModel`, `AnthropicToolModel`, `AnthropicVLM`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_llm_anthropic` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_anthropic/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_llm_anthropic`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_anthropic/swarmauri_llm_anthropic/__init__.py). The `swarmauri_llm_anthropic` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_llm_anthropic` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_llm_anthropic` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/i9n/test_AnthropicModel_i9n.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_anthropic/tests/i9n/test_AnthropicModel_i9n.py)
- [tests/r8n/test_AnthropicToolModel_r8n.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_anthropic/tests/r8n/test_AnthropicToolModel_r8n.py)
- [tests/unit/test_AnthropicModel_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_anthropic/tests/unit/test_AnthropicModel_unit.py)
- [tests/unit/test_AnthropicToolModel_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_anthropic/tests/unit/test_AnthropicToolModel_unit.py)
- [tests/xfail/test_AnthropicToolModel_xfail.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_anthropic/tests/xfail/test_AnthropicToolModel_xfail.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_llm_anthropic` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_anthropic/swarmauri_llm_anthropic/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Q: Which Anthropic API does this package use?**

A: Both adapters use the Anthropic Messages API at `https://api.anthropic.com/v1/messages` with the `anthropic-version` header set to `2023-06-01`.

**Q: Which classes are exported?**

A: The package exports `AnthropicModel` through the `swarmauri.llms` entry point and `AnthropicToolModel` through the `swarmauri.tool_llms` entry point.

**Q: Which Claude model names are configured locally?**

A: `AnthropicModel` and `AnthropicToolModel` include configured model IDs such as `claude-opus-4-1`, `claude-opus-4-0`, `claude-sonnet-4-0`, `claude-3-7-sonnet-latest`, and `claude-3-5-haiku-latest`. Set `name` explicitly in production.

**Q: Does the tool model execute Swarmauri tools?**

A: Yes. `AnthropicToolModel` converts Swarmauri toolkit tool schemas, sends them in the Anthropic `tools` payload, invokes matching Swarmauri tools when a `tool_use` block is returned, and adds the result to the conversation.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_llm_anthropic`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_anthropic/swarmauri_llm_anthropic/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_llm_anthropic` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_anthropic/swarmauri_llm_anthropic/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_anthropic/pyproject.toml) provide the supporting context for `swarmauri_llm_anthropic`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

LLM provider packages:

- [swarmauri_llm_ai21](https://pypi.org/project/swarmauri_llm_ai21/)
- [swarmauri_llm_cerebras](https://pypi.org/project/swarmauri_llm_cerebras/)
- [swarmauri_llm_cohere](https://pypi.org/project/swarmauri_llm_cohere/)
- [swarmauri_llm_gemini](https://pypi.org/project/swarmauri_llm_gemini/)
- [swarmauri_llm_groq](https://pypi.org/project/swarmauri_llm_groq/)
- [swarmauri_llm_mistral](https://pypi.org/project/swarmauri_llm_mistral/)
- [swarmauri_llm_openai](https://pypi.org/project/swarmauri_llm_openai/)

Foundational packages:

- [swarmauri_core](https://pypi.org/project/swarmauri_core/) defines core interfaces.
- [swarmauri_base](https://pypi.org/project/swarmauri_base/) provides base component classes.
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/) contains the shared Anthropic implementations.
- [swarmauri](https://pypi.org/project/swarmauri/) provides namespace imports and plugin discovery.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_llm_anthropic](https://pypi.org/project/swarmauri_llm_anthropic/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_llm_anthropic`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/50-community/swarmauri_llm_anthropic` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_llm_anthropic` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_llm_anthropic` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_anthropic/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_llm_anthropic` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_llm_anthropic` source version is `0.11.0.dev3`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_anthropic/LICENSE).
<!-- readme-standards:end license -->

Apache-2.0

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_llm_anthropic/NOTICE) for attribution.
<!-- readme-standards:end notices -->
