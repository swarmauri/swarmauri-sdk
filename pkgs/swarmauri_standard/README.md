![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_standard/">
        <img src="https://static.pepy.tech/badge/swarmauri_standard/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/swarmauri_standard/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/swarmauri_standard.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_standard/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_standard/">
        <img src="https://img.shields.io/pypi/l/swarmauri_standard" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_standard/">
        <img src="https://img.shields.io/pypi/v/swarmauri_standard?label=swarmauri_standard&color=green" alt="PyPI - swarmauri_standard"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Standard

`swarmauri_standard` provides first-party, ready-to-use Swarmauri components built on `swarmauri_core` interfaces and `swarmauri_base` component behavior. It is the standard component bundle for agents, chains, chunkers, conversations, documents, tools, toolkits, parsers, prompts, schema converters, metrics, similarities, deprecated distance compatibility shims, vectors, vector stores, tracing utilities, STT/TTS/VLM adapters, signing helpers, and key-provider components.

## Why Swarmauri Standard?

`swarmauri_standard` provides maintained first-party components that users can install and instantiate directly. It also demonstrates the expected Swarmauri component style: typed base classes, direct class imports, dynamic serialization, and namespace-ready registration.

## FAQ

### Q: What kinds of components are included?

A: The package includes agents, chains, chunkers, conversations, documents, tools, toolkits, parsers, prompts, schema converters, metrics, similarities, deprecated distance compatibility shims, vectors, vector stores, tracing utilities, STT/TTS/VLM adapters, signing helpers, and key-provider components.

### Q: Is this package the same as `swarmauri`?

A: No. `swarmauri` provides the namespace importer and plugin discovery layer. `swarmauri_standard` provides concrete first-party implementation classes.

### Q: Should examples instantiate plugins directly?

A: Yes. Direct class imports and direct instantiation are the preferred documented workflow unless a package explicitly requires another integration pattern.

## Features

- Standard agents including question-answering, RAG, simple conversation, and tool-using agent patterns.
- Tool and toolkit components such as calculator, HTTP request, readability, code extraction, temperature conversion, weather, and accessibility utilities.
- Parser and document components for CSV, XML, OpenAPI specs, markdown-to-HTML, URLs, regular expressions, Python code, and phone-number extraction.
- Chunkers, conversations, prompts, prompt templates, chains, pipelines, service registries, state objects, and tracing helpers for application workflows.
- Deprecated distance compatibility shims, vectors, vector stores, measurements, metrics, norms, similarities, and related numerical components.
- Model adapter classes for LLM, tool LLM, embedding, image generation, STT, TTS, OCR, and VLM workflows where provider configuration is available.
- Signing and key-provider components that align with Swarmauri's security-oriented interfaces.
- Dynamic JSON, YAML, and TOML serialization through `ComponentBase`, `DynamicBase`, and `SubclassUnion`.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

## Installation

Install with `uv`:

```bash
uv add swarmauri_standard
```

Install with `pip`:

```bash
pip install swarmauri_standard
```

## Usage

Use standard components directly from their implementation modules:

```python
from swarmauri_standard.tools.CalculatorTool import CalculatorTool

calculator = CalculatorTool()
result = calculator("add", 5, 3)

assert result == {"operation": "add", "calculated_result": "8.0"}
```

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

## Component Families

The package includes these standard component families:

- Agents: `QAAgent`, `RagAgent`, `SimpleConversationAgent`, and `ToolAgent`.
- Chains and workflow: callable chains, chain steps, context chains, prompt context chains, pipelines, service registries, swarms, and round-robin task management.
- Text and document processing: chunkers, documents, conversations, prompts, prompt templates, parsers, messages, and schema converters.
- Tools and toolkits: calculator, arithmetic, HTTP requests, JSON requests, code extraction, code interpretation, readability scoring, weather, temperature conversion, parameters, accessibility toolkit, and generic toolkit support.
- Vector and numerical work: vectors, TF-IDF vector store, deprecated distance compatibility shims, measurements, metrics, norms, similarities, pseudometrics, seminorms, matrices, tensors, and inner products.
- AI model surfaces: LLMs, tool LLMs, embeddings, image generators, OCR, STT, TTS, and VLM classes for supported providers.
- Runtime support: decorators, tracing, transports, state, logging, and utility classes.
- Trust and security surfaces: signing and key-provider components that align with Swarmauri's core interfaces.

## Distance Migration

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

## Related Packages

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

## When To Use This Package

Use `swarmauri_standard` when you want maintained first-party implementations that are ready for examples, prototypes, tests, and production workflows where the included component behavior fits. Use smaller standalone component packages when you want a narrower dependency surface for a specific provider, algorithm, or runtime integration.

## License

Apache-2.0

## Contributing

When adding standard components, inherit from the matching `swarmauri_base` class, satisfy the `swarmauri_core` interface, register the component type, document direct instantiation, and follow the [Swarmauri SDK contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md).


