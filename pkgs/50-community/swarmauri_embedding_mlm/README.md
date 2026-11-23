# swarmauri_embedding_mlm

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_embedding_mlm</strong></p>
<p align="center">Trainable Swarmauri embedding component for Hugging Face masked language models, tokenizer adaptation, local fine-tuning, and Vector output.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_embedding_mlm/"><img alt="pypi: swarmauri_embedding_mlm" src="https://img.shields.io/pypi/v/swarmauri_embedding_mlm"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_embedding_mlm/pyproject.toml"><img alt="Source version: 0.11.0.dev1" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev1&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_embedding_mlm/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_embedding_mlm/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_embedding_mlm/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_embedding_mlm/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_embedding_mlm/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_embedding_mlm/"><img alt="Monthly PyPI downloads: swarmauri_embedding_mlm" src="https://img.shields.io/pypi/dm/swarmauri_embedding_mlm"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_embedding_mlm/README.md"><img alt="README hits: swarmauri_embedding_mlm" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/50-community/swarmauri_embedding_mlm/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_embedding_mlm/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_embedding_mlm/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_embedding_mlm` provides `MlmEmbedding`, a Swarmauri embedding component built on Hugging Face `transformers` and PyTorch masked language models. It can fine-tune a masked language model on local text, optionally expand the tokenizer vocabulary, and return Swarmauri `Vector` objects for retrieval, clustering, similarity search, and downstream agent memory workflows.

### Why This Package

Use this package when you want a trainable embedding adapter inside the Swarmauri component system instead of a fixed API-only embedding provider. `MlmEmbedding` keeps model loading, masking, fine-tuning, pooling, vector wrapping, and save/load behavior behind the shared `EmbeddingBase` interface so it can plug into Swarmauri vector stores and retrieval pipelines.

### When to Use

Choose `swarmauri_embedding_mlm` when your integration needs trainable Swarmauri embedding component for Hugging Face masked language models, tokenizer adaptation, local fine-tuning, and Vector output. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- `MlmEmbedding` registered under the `swarmauri.embeddings` entry point.
- Hugging Face masked-language-model loading through `AutoTokenizer` and `AutoModelForMaskedLM`.
- PyTorch training loop with automatic CUDA or CPU selection.
- Configurable `embedding_name`, `batch_size`, `learning_rate`, `masking_ratio`, and `randomness_ratio`.
- Optional tokenizer vocabulary expansion with `add_new_tokens=True`.
- `fit()`, `transform()`, `fit_transform()`, and `infer_vector()` workflows.
- `save_model()` and `load_model()` helpers for model reuse.
- Swarmauri `Vector` outputs for vector stores and retrieval pipelines.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

### Non-Goals

`swarmauri_embedding_mlm` owns trainable Swarmauri embedding component for Hugging Face masked language models, tokenizer adaptation, local fine-tuning, and Vector output. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

- PyTorch installed for your target CPU or GPU environment.
- Network access or a local Hugging Face cache for the selected model.
- Enough disk and memory for the selected masked language model.
- Training data as a list of text strings.

### Installation

Install with `uv`:

```bash
uv add swarmauri_embedding_mlm
```

Install with `pip`:

```bash
pip install swarmauri_embedding_mlm
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_embedding_mlm
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_embedding_mlm
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_embedding_mlm
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_embedding_mlm/docs/readme/quick_start.py).

```python
from swarmauri_embedding_mlm import MlmEmbedding

documents = [
    "Swarmauri components compose agents, memory, and tools.",
    "Masked language models can adapt to domain terminology.",
]

embedder = MlmEmbedding(
    embedding_name="distilbert-base-uncased",
    batch_size=8,
    learning_rate=3e-5,
)

embedder.fit(documents)
vectors = embedder.transform(
    [
        "Agents retrieve context from vector stores.",
        "Domain adaptation improves local vocabulary coverage.",
    ]
)

print(len(vectors))
print(vectors[0].value[:5])
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_embedding_mlm` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_embedding_mlm/docs/readme/usage.py).

```python
from swarmauri_embedding_mlm import MlmEmbedding

documents = [
    "Swarmauri components compose agents, memory, and tools.",
    "Masked language models can adapt to domain terminology.",
]

embedder = MlmEmbedding(
    embedding_name="distilbert-base-uncased",
    batch_size=8,
    learning_rate=3e-5,
)

embedder.fit(documents)
vectors = embedder.transform(
    [
        "Agents retrieve context from vector stores.",
        "Domain adaptation improves local vocabulary coverage.",
    ]
)

print(len(vectors))
print(vectors[0].value[:5])
```
<!-- readme-standards:end example.usage -->

Fine-tune a masked language model and embed documents:


Expand the tokenizer vocabulary before fine-tuning:

```python
from swarmauri_embedding_mlm import MlmEmbedding

corpus = [
    "Swarmauri pipelines use composable intelligence infrastructure.",
    "Qdrant and Redis vector stores support retrieval workflows.",
]

embedder = MlmEmbedding(add_new_tokens=True)
embedder.fit(corpus)

print(embedder.epochs)
print(len(embedder.extract_features()))
```

Save and reload a tuned model:

```python
from pathlib import Path

from swarmauri_embedding_mlm import MlmEmbedding

model_dir = Path("models/domain-mlm")

embedder = MlmEmbedding(embedding_name="distilbert-base-uncased")
embedder.fit(["short adaptation corpus"])
embedder.save_model(model_dir.as_posix())

restored = MlmEmbedding(embedding_name=model_dir.as_posix())
vector = restored.infer_vector("reuse the tuned model")

print(len(vector.value))
```

### Configuration

Configure `swarmauri_embedding_mlm` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_embedding_mlm/swarmauri_embedding_mlm/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_embedding_mlm/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_embedding_mlm` source does not establish a package-wide exception hierarchy. Preserve errors from its declared dependencies and validate inputs using the specific public contract in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_embedding_mlm/swarmauri_embedding_mlm/__init__.py).

### Best Practices

- Pin `embedding_name` to a model you have tested in your deployment environment.
- Pre-download or cache Hugging Face model weights for offline or repeatable builds.
- Use smaller models and smaller batches on memory-constrained machines.
- Save tuned models after adaptation so workers do not repeat fine-tuning.
- Pair generated vectors with a Swarmauri vector store for retrieval-augmented workflows.

---

## Package Boundary

### What It Owns

`swarmauri_embedding_mlm` is located in `community` and owns trainable Swarmauri embedding component for Hugging Face masked language models, tokenizer adaptation, local fine-tuning, and Vector output. Source-declared APIs include `MlmEmbedding`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_embedding_mlm/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_embedding_mlm`.

Source-declared exports or types: `MlmEmbedding`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_embedding_mlm/swarmauri_embedding_mlm/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.embeddings` → `MlmEmbedding` → `swarmauri_embedding_mlm.MlmEmbedding:MlmEmbedding`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_embedding_mlm` are `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`, `torch`, `transformers`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_embedding_mlm/swarmauri_embedding_mlm/__init__.py).

### Protocol Consumers

Direct consumers in this checkout’s package manifests include `swarmauri_vectorstore_mlm`. These edges describe declared dependencies, not protocol-conformance evidence.

### Extensions

For `swarmauri_embedding_mlm`, use the source-declared public interfaces (`MlmEmbedding`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_embedding_mlm` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_embedding_mlm/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_embedding_mlm`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_embedding_mlm/swarmauri_embedding_mlm/__init__.py). The `swarmauri_embedding_mlm` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_embedding_mlm` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_embedding_mlm` package directory for the maintained example source checks (Python compilation and non-Python file presence). Behavioral tests may live in the repository’s shared suites; the new README syntax test is not presented as runtime coverage for trainable Swarmauri embedding component for Hugging Face masked language models, tokenizer adaptation, local fine-tuning, and Vector output.

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_embedding_mlm` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_embedding_mlm/swarmauri_embedding_mlm/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Q: Which models can this package load?**

A: `MlmEmbedding` uses `AutoTokenizer.from_pretrained()` and `AutoModelForMaskedLM.from_pretrained()`, so use a Hugging Face model compatible with masked language modeling, such as BERT-style or DistilBERT-style models.

**Q: Does fit() train a complete embedding model from scratch?**

A: No. It fine-tunes an existing masked language model for one pass per `fit()` call using masked-token loss, AdamW, and the configured batch size and learning rate.

**Q: What does transform() return?**

A: It returns a list of Swarmauri `Vector` objects. The current implementation mean-pools model outputs and falls back to mean-pooled logits when the masked-language-model output does not expose `last_hidden_state`.

**Q: Can I persist a tuned model?**

A: Yes. Use `save_model(path)` to write the model and tokenizer, then `load_model(path)` to restore them later.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_embedding_mlm`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_embedding_mlm/swarmauri_embedding_mlm/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_embedding_mlm` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_embedding_mlm/swarmauri_embedding_mlm/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_embedding_mlm/pyproject.toml) provide the supporting context for `swarmauri_embedding_mlm`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

Embedding and vector packages:

- [swarmauri_embedding_doc2vec](https://pypi.org/project/swarmauri_embedding_doc2vec/)
- [swarmauri_embedding_nmf](https://pypi.org/project/swarmauri_embedding_nmf/)
- [swarmauri_vectorstore_mlm](https://pypi.org/project/swarmauri_vectorstore_mlm/)
- [swarmauri_vectorstore_qdrant](https://pypi.org/project/swarmauri_vectorstore_qdrant/)
- [swarmauri_vectorstore_redis](https://pypi.org/project/swarmauri_vectorstore_redis/)
- [swarmauri_vectorstore_pinecone](https://pypi.org/project/swarmauri_vectorstore_pinecone/)

Foundational packages:

- [swarmauri_core](https://pypi.org/project/swarmauri_core/) defines embedding interfaces.
- [swarmauri_base](https://pypi.org/project/swarmauri_base/) provides `EmbeddingBase`.
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/) provides `Vector`.
- [swarmauri](https://pypi.org/project/swarmauri/) provides namespace imports and plugin discovery.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_embedding_mlm](https://pypi.org/project/swarmauri_embedding_mlm/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_embedding_mlm`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/50-community/swarmauri_embedding_mlm` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_embedding_mlm` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_embedding_mlm` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_embedding_mlm/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_embedding_mlm` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_embedding_mlm` source version is `0.11.0.dev1`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_embedding_mlm/LICENSE).
<!-- readme-standards:end license -->

Apache-2.0

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_embedding_mlm/NOTICE) for attribution.
<!-- readme-standards:end notices -->
