# swarmauri_standard

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_standard</strong></p>
<p align="center">First-party Swarmauri standard components for agents, tools, parsers, vectors, model adapters, and composable intelligence workflows.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_standard/"><img alt="pypi: swarmauri_standard" src="https://img.shields.io/pypi/v/swarmauri_standard?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/30-standard-kernel/swarmauri_standard/pyproject.toml"><img alt="Source version: 0.11.0.dev13" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev13&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/30-standard-kernel/swarmauri_standard/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/30-standard-kernel/swarmauri_standard/pyproject.toml"><img alt="Layer: swarmauri_standard" src="https://img.shields.io/static/v1?label=Layer&amp;message=swarmauri_standard&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/30-standard-kernel/swarmauri_standard/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/30-standard-kernel/swarmauri_standard/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/30-standard-kernel/swarmauri_standard/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_standard/"><img alt="Monthly PyPI downloads: swarmauri_standard" src="https://img.shields.io/pypi/dm/swarmauri_standard?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/30-standard-kernel/swarmauri_standard/README.md"><img alt="README hits: swarmauri_standard" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/30-standard-kernel/swarmauri_standard/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/30-standard-kernel/swarmauri_standard/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/30-standard-kernel/swarmauri_standard/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_standard` provides first-party, ready-to-use Swarmauri components built on `swarmauri_core` interfaces and `swarmauri_base` component behavior. It is the standard component bundle for agents, chains, chunkers, conversations, documents, tools, toolkits, parsers, prompts, schema converters, metrics, similarities, deprecated distance compatibility shims, vectors, vector stores, tracing utilities, STT/TTS/VLM adapters, signing helpers, and key-provider components.

### Why This Package

`swarmauri_standard` provides maintained first-party components that users can install and instantiate directly. It also demonstrates the expected Swarmauri component style: typed base classes, direct class imports, dynamic serialization, and namespace-ready registration.

### When to Use

Use `swarmauri_standard` when you want maintained first-party implementations that are ready for examples, prototypes, tests, and production workflows where the included component behavior fits. Use smaller standalone component packages when you want a narrower dependency surface for a specific provider, algorithm, or runtime integration.

### Features

- Standard agents including question-answering, RAG, simple conversation, and tool-using agent patterns.
- Tool and toolkit components such as calculator, HTTP request, readability, code extraction, temperature conversion, weather, and accessibility utilities.
- Parser and document components for CSV, XML, OpenAPI specs, markdown-to-HTML, URLs, regular expressions, Python code, and phone-number extraction.
- Chunkers, conversations, prompts, prompt templates, chains, pipelines, service registries, state objects, and tracing helpers for application workflows.
- Deprecated distance compatibility shims, vectors, vector stores, measurements, metrics, norms, similarities, and related numerical components.
- Model adapter classes for LLM, tool LLM, embedding, image generation, STT, TTS, OCR, and VLM workflows where provider configuration is available.
- Signing and key-provider components that align with Swarmauri's security-oriented interfaces.
- Dynamic JSON, YAML, and TOML serialization through `ComponentBase`, `DynamicBase`, and `SubclassUnion`.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

### Non-Goals

`swarmauri_standard` owns first-party Swarmauri standard components for agents, tools, parsers, vectors, model adapters, and composable intelligence workflows. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/30-standard-kernel/swarmauri_standard/pyproject.toml) declares runtime dependencies including `toml`, `pydantic`, `h11`, `httpx`, `numpy`, `pandas`, `joblib`, `pillow`, `aiofiles`, `rich`, `typing-extensions`, `swarmauri-core`. Read the example’s inputs and service requirements before execution.

### Installation

Install with `uv`:

```bash
uv add swarmauri_standard
```

Install with `pip`:

```bash
pip install swarmauri_standard
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_standard
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_standard
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_standard
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/30-standard-kernel/swarmauri_standard/docs/readme/quick_start.py).

```python
from swarmauri_standard.tools.CalculatorTool import CalculatorTool

calculator = CalculatorTool()
result = calculator("add", 5, 3)

assert result == {"operation": "add", "calculated_result": "8.0"}
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_standard` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/30-standard-kernel/swarmauri_standard/docs/readme/usage.py).

```python
from swarmauri_standard.tools.CalculatorTool import CalculatorTool

calculator = CalculatorTool()
result = calculator("add", 5, 3)

assert result == {"operation": "add", "calculated_result": "8.0"}
```
<!-- readme-standards:end example.usage -->

Use standard components directly from their implementation modules:


Create documents and serialize them as Swarmauri components:

```python
from swarmauri_standard.documents.Document import Document

doc = Document(content="Composable intelligence infrastructure")
payload = doc.model_dump_json()
restored = Document.model_validate_json(payload)

assert restored.type == "Document"
assert restored.content == doc.content
```

Hydrate registered standard components through a base-family union:

```python
from pydantic import BaseModel

from swarmauri_base.DynamicBase import SubclassUnion
from swarmauri_base.toolkits.ToolkitBase import ToolkitBase
from swarmauri_standard.toolkits.Toolkit import Toolkit


class ToolkitEnvelope(BaseModel):
    toolkit: SubclassUnion[ToolkitBase]


payload = ToolkitEnvelope(toolkit=Toolkit()).model_dump_json()
restored = ToolkitEnvelope.model_validate_json(payload)

assert isinstance(restored.toolkit, Toolkit)
```

### Configuration

The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/30-standard-kernel/swarmauri_standard/swarmauri_standard/llms/HyperbolicAudioTTS.py) references configuration keys `FAL_KEY`. Consult the constructor or function signature before supplying them; a referenced key is not necessarily a global environment variable.

### Error Handling

The inspected `swarmauri_standard` source raises `AttributeError`, `Exception`, `IndexErrorWithContext`, `KeyError`, `ModuleNotFoundError`, `NotImplementedError`, `RuntimeError`, `TimeoutError`, `TypeError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_standard` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `QAAgent`, `RagAgent`, `SimpleConversationAgent`, `ToolAgent`, `CallableChain`, `ChainStep`, `ContextChain`, `PromptContextChain`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_standard` is located in `swarmauri_standard` and owns first-party Swarmauri standard components for agents, tools, parsers, vectors, model adapters, and composable intelligence workflows. Source-declared APIs include `QAAgent`, `RagAgent`, `SimpleConversationAgent`, `ToolAgent`, `CallableChain`, `ChainStep`, `ContextChain`, `PromptContextChain`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/30-standard-kernel/swarmauri_standard/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_standard`.

Source-declared exports or types: `QAAgent`, `RagAgent`, `SimpleConversationAgent`, `ToolAgent`, `CallableChain`, `ChainStep`, `ContextChain`, `PromptContextChain`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/30-standard-kernel/swarmauri_standard/swarmauri_standard/llms/HyperbolicAudioTTS.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
This package declares no command-line, GUI, or plugin entry points in its manifest.
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_standard` are `toml`, `pydantic`, `h11`, `httpx`, `numpy`, `pandas`, `joblib`, `pillow`, `aiofiles`, `rich`, `typing-extensions`, `swarmauri-core`, `swarmauri-base`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/30-standard-kernel/swarmauri_standard/swarmauri_standard/llms/HyperbolicAudioTTS.py).

### Protocol Consumers

Direct consumers in this checkout’s package manifests include `swarmauri-demo-package-maintenance`, `swarmauri_certs_acme`, `swarmauri_certs_cfssl`, `swarmauri_certs_ocspverify`, `swarmauri_certservice_aws_kms`, `swarmauri_certservice_gcpkms`, `swarmauri_certservice_ms_adcs`, `swarmauri_certservice_stepca`, `swarmauri_embedding_mlm`, `swarmauri_keyprovider_aws_kms`, `swarmauri_keyprovider_gcpkms`, `swarmauri_keyprovider_vaulttransit`, `swarmauri_llm_ai21`, `swarmauri_llm_anthropic`, `swarmauri_llm_azureopenai`. These edges describe declared dependencies, not protocol-conformance evidence.

### Extensions

For `swarmauri_standard`, use the source-declared public interfaces (`QAAgent`, `RagAgent`, `SimpleConversationAgent`, `ToolAgent`, `CallableChain`, `ChainStep`, `ContextChain`, `PromptContextChain`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_standard` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/30-standard-kernel/swarmauri_standard/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_standard`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/30-standard-kernel/swarmauri_standard/swarmauri_standard/llms/HyperbolicAudioTTS.py). The `swarmauri_standard` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_standard` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_standard` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/unit/key_providers/test_inmemory_provider_unit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/30-standard-kernel/swarmauri_standard/tests/unit/key_providers/test_inmemory_provider_unit.py)
- [tests/unit/tool_llms/test_gemini_tool_step.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/30-standard-kernel/swarmauri_standard/tests/unit/tool_llms/test_gemini_tool_step.py)
- [tests/unit/tool_llms/test_openai_tool_step.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/30-standard-kernel/swarmauri_standard/tests/unit/tool_llms/test_openai_tool_step.py)
- [tests/unit/tts/test_openai_tts_offline.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/30-standard-kernel/swarmauri_standard/tests/unit/tts/test_openai_tts_offline.py)
- [tests/unit/tts/test_playht_tts_model_selection.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/30-standard-kernel/swarmauri_standard/tests/unit/tts/test_playht_tts_model_selection.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_standard` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/30-standard-kernel/swarmauri_standard/swarmauri_standard/llms/HyperbolicAudioTTS.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Q: What kinds of components are included?**

A: The package includes agents, chains, chunkers, conversations, documents, tools, toolkits, parsers, prompts, schema converters, metrics, similarities, deprecated distance compatibility shims, vectors, vector stores, tracing utilities, STT/TTS/VLM adapters, signing helpers, and key-provider components.

**Q: Is this package the same as swarmauri?**

A: No. `swarmauri` provides the namespace importer and plugin discovery layer. `swarmauri_standard` provides concrete first-party implementation classes.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_standard`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/30-standard-kernel/swarmauri_standard/swarmauri_standard/llms/HyperbolicAudioTTS.py) for the exact types and signatures involved.

### When

**Q: Should examples instantiate plugins directly?**

A: Yes. Direct class imports and direct instantiation are the preferred documented workflow unless a package explicitly requires another integration pattern.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/30-standard-kernel/swarmauri_standard/swarmauri_standard/llms/HyperbolicAudioTTS.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/30-standard-kernel/swarmauri_standard/pyproject.toml) provide the supporting context for `swarmauri_standard`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

Foundational packages:

- [swarmauri](https://pypi.org/project/swarmauri/) provides namespace imports and plugin discovery.
- [swarmauri_core](https://pypi.org/project/swarmauri_core/) provides the interfaces implemented by these standard components.
- [swarmauri_base](https://pypi.org/project/swarmauri_base/) provides component base classes, mixins, and serialization behavior.
- [swarmauri_typing](https://pypi.org/project/swarmauri_typing/) provides dynamic typing utilities used by the component model.

Related component packages:

- [swarmauri_embedding_doc2vec](https://pypi.org/project/swarmauri_embedding_doc2vec/) for Doc2Vec embedding support.
- [swarmauri_embedding_nmf](https://pypi.org/project/swarmauri_embedding_nmf/) for NMF embedding support.
- [swarmauri_vectorstore_doc2vec](https://pypi.org/project/swarmauri_vectorstore_doc2vec/) for Doc2Vec vector-store workflows.
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/) for the active metric, similarity, and vector-store comparator surface.
- [swarmauri_tool_matplotlib](https://pypi.org/project/swarmauri_tool_matplotlib/) for Matplotlib tool support.
- [swarmauri_parser_keywordextractor](https://pypi.org/project/swarmauri_parser_keywordextractor/) for keyword extraction parsing.
- [swarmauri_signing_ed25519](https://pypi.org/project/swarmauri_signing_ed25519/) for Ed25519 signing.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_standard](https://pypi.org/project/swarmauri_standard/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

When adding standard components, inherit from the matching `swarmauri_base` class, satisfy the `swarmauri_core` interface, register the component type, document direct instantiation, and follow the [Swarmauri SDK contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md).

### Development Setup

Work from the `pkgs/30-standard-kernel/swarmauri_standard` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

**Component Families**

The package includes these standard component families:

- Agents: `QAAgent`, `RagAgent`, `SimpleConversationAgent`, and `ToolAgent`.
- Chains and workflow: callable chains, chain steps, context chains, prompt context chains, pipelines, service registries, swarms, and round-robin task management.
- Text and document processing: chunkers, documents, conversations, prompts, prompt templates, parsers, messages, and schema converters.
- Tools and toolkits: calculator, arithmetic, HTTP requests, JSON requests, code extraction, code interpretation, readability scoring, weather, temperature conversion, parameters, accessibility toolkit, and generic toolkit support.
- Vector and numerical work: vectors, TF-IDF vector store, deprecated distance compatibility shims, measurements, metrics, norms, similarities, pseudometrics, seminorms, matrices, tensors, and inner products.
- AI model surfaces: LLMs, tool LLMs, embeddings, image generators, OCR, STT, TTS, and VLM classes for supported providers.
- Runtime support: decorators, tracing, transports, state, logging, and utility classes.
- Trust and security surfaces: signing and key-provider components that align with Swarmauri's core interfaces.

**Distance Migration**

The `swarmauri_standard.distances` module remains available only as a deprecated compatibility surface. Prefer the active metric and similarity families instead:

- `CosineDistance` -> `CosineSimilarity`
- `EuclideanDistance` -> `EuclideanMetric`
- `LevenshteinDistance` -> `LevenshteinMetric`
- `JaccardIndexDistance` -> `JaccardIndexSimilarity`
- `SorensenDiceDistance` -> `DiceSimilarity`
- `ChebyshevDistance` -> `SupremumMetric`
- `ManhattanDistance` -> `LpMetric(p=1)`
- `MinkowskiDistance` -> `LpMetric(p=<order>)`
- `SquaredEuclideanDistance` -> `EuclideanMetric` or `GaussianRBFSimilarity`, depending on whether you need metric or similarity semantics
- `CanberraDistance`, `ChiSquaredDistance`, and `HaversineDistance` do not yet have active drop-in replacements in the workspace

**Resumable tool calls**

Pass either existing OpenAI or Gemini tool-model class to
`swarmauri_agent_runner.AgentRunner` with a run store and an approval policy.
The runner dispatches tools and the adapter preserves the provider transcript.

**Standalone alpha TTS providers**

Install `swarmauri_tts_openai` directly and import `OpenaiTTS` from that package.
DeepInfra and Together have separate `swarmauri_tts_deepinfra` and
`swarmauri_tts_together` alpha packages. Live provider verification is pending;
see [verification tracking](../../../docs/verification/tts-providers.md).

**TTS lifecycle and canonical imports**

New speech integrations use the standalone alpha provider packages, with
verification issues in docs/verification/tts-providers.md.
OpenAI's underlying Speech models shut down on 2027-01-06; Realtime requires
a different adapter. Play.ht and Hyperbolic's old audio endpoint are retired:
their legacy types remain importable and fail locally before network access.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_standard` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/30-standard-kernel/swarmauri_standard/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_standard` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_standard` source version is `0.11.0.dev13`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/30-standard-kernel/swarmauri_standard/LICENSE).
<!-- readme-standards:end license -->

Apache-2.0

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/30-standard-kernel/swarmauri_standard/NOTICE) for attribution.
<!-- readme-standards:end notices -->
