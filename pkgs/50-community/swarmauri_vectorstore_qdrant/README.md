# swarmauri_vectorstore_qdrant

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_vectorstore_qdrant</strong></p>
<p align="center">Swarmauri Persistent Qdrant Vector Store</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_vectorstore_qdrant/"><img alt="pypi: swarmauri_vectorstore_qdrant" src="https://img.shields.io/pypi/v/swarmauri_vectorstore_qdrant"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_vectorstore_qdrant/pyproject.toml"><img alt="Source version: 0.11.0.dev3" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev3&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_vectorstore_qdrant/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_vectorstore_qdrant/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_vectorstore_qdrant/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_vectorstore_qdrant/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_vectorstore_qdrant/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_vectorstore_qdrant/"><img alt="Monthly PyPI downloads: swarmauri_vectorstore_qdrant" src="https://img.shields.io/pypi/dm/swarmauri_vectorstore_qdrant"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_vectorstore_qdrant/README.md"><img alt="README hits: swarmauri_vectorstore_qdrant" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/50-community/swarmauri_vectorstore_qdrant/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_vectorstore_qdrant/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_vectorstore_qdrant/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

A vector store implementation using Qdrant as the backend, supporting both persistent local storage and cloud-based operations for document storage and retrieval.

### Why This Package

`swarmauri_vectorstore_qdrant` isolates this responsibility: Swarmauri Persistent Qdrant Vector Store. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_vectorstore_qdrant/swarmauri_vectorstore_qdrant/__init__.py) exposes `CloudQdrantVectorStore`, `PersistentQdrantVectorStore`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_vectorstore_qdrant` when your integration needs swarmauri Persistent Qdrant Vector Store. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- `CloudQdrantVectorStore`: CloudQdrantVectorStore is a concrete implementation that integrates
- `PersistentQdrantVectorStore`: PersistentQdrantVectorStore is a concrete implementation that integrates

### Non-Goals

`swarmauri_vectorstore_qdrant` owns swarmauri Persistent Qdrant Vector Store. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_vectorstore_qdrant/pyproject.toml) declares runtime dependencies including `qdrant-client`, `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`, `swarmauri-embedding-doc2vec`. Read the example’s inputs and service requirements before execution.

### Installation

```bash
pip install swarmauri_vectorstore_qdrant
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_vectorstore_qdrant
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_vectorstore_qdrant
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_vectorstore_qdrant
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_vectorstore_qdrant/docs/readme/quick_start.py).

```python
from swarmauri.documents.Document import Document
from swarmauri.vectorstores.PersistentQdrantVectorStore import (
    PersistentQdrantVectorStore,
)
from swarmauri.vector_stores.CloudQdrantVectorStore import (
    CloudQdrantVectorStore,
)

# Local Persistent Storage
local_store = PersistentQdrantVectorStore(
    collection_name="my_collection",
    vector_size=100,
    path="http://localhost:6333",
)
local_store.connect()

# Cloud Storage
cloud_store = CloudQdrantVectorStore(
    api_key="your_api_key",
    collection_name="my_collection",
    vector_size=100,
    url="your_qdrant_cloud_url",
)
cloud_store.connect()

# Add documents
documents = [
    Document(content="sample text 1"),
    Document(content="sample text 2"),
]
local_store.add_documents(documents)

# Retrieve similar documents
results = local_store.retrieve("sample query", top_k=5)
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_vectorstore_qdrant` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_vectorstore_qdrant/docs/readme/usage.py).

```python
from swarmauri.documents.Document import Document
from swarmauri.vectorstores.PersistentQdrantVectorStore import (
    PersistentQdrantVectorStore,
)
from swarmauri.vector_stores.CloudQdrantVectorStore import (
    CloudQdrantVectorStore,
)

# Local Persistent Storage
local_store = PersistentQdrantVectorStore(
    collection_name="my_collection",
    vector_size=100,
    path="http://localhost:6333",
)
local_store.connect()

# Cloud Storage
cloud_store = CloudQdrantVectorStore(
    api_key="your_api_key",
    collection_name="my_collection",
    vector_size=100,
    url="your_qdrant_cloud_url",
)
cloud_store.connect()

# Add documents
documents = [
    Document(content="sample text 1"),
    Document(content="sample text 2"),
]
local_store.add_documents(documents)

# Retrieve similar documents
results = local_store.retrieve("sample query", top_k=5)
```
<!-- readme-standards:end example.usage -->

### Configuration

Configure `swarmauri_vectorstore_qdrant` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_vectorstore_qdrant/swarmauri_vectorstore_qdrant/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_vectorstore_qdrant/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_vectorstore_qdrant` source does not establish a package-wide exception hierarchy. Preserve errors from its declared dependencies and validate inputs using the specific public contract in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_vectorstore_qdrant/swarmauri_vectorstore_qdrant/__init__.py).

### Best Practices

Use the explicit `swarmauri_vectorstore_qdrant` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `CloudQdrantVectorStore`, `PersistentQdrantVectorStore`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_vectorstore_qdrant` is located in `community` and owns swarmauri Persistent Qdrant Vector Store. Source-declared APIs include `CloudQdrantVectorStore`, `PersistentQdrantVectorStore`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_vectorstore_qdrant/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_vectorstore_qdrant`.

Source-declared exports or types: `CloudQdrantVectorStore`, `PersistentQdrantVectorStore`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_vectorstore_qdrant/swarmauri_vectorstore_qdrant/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.vector_stores` → `CloudQdrantVectorStore` → `swarmauri_vectorstore_qdrant.CloudQdrantVectorStore:CloudQdrantVectorStore`
- `swarmauri.vector_stores` → `PersistentQdrantVectorStore` → `swarmauri_vectorstore_qdrant.PersistentQdrantVectorStore:PersistentQdrantVectorStore`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_vectorstore_qdrant` are `qdrant-client`, `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`, `swarmauri-embedding-doc2vec`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_vectorstore_qdrant/swarmauri_vectorstore_qdrant/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_vectorstore_qdrant` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_vectorstore_qdrant`, use the source-declared public interfaces (`CloudQdrantVectorStore`, `PersistentQdrantVectorStore`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_vectorstore_qdrant` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_vectorstore_qdrant/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_vectorstore_qdrant`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_vectorstore_qdrant/swarmauri_vectorstore_qdrant/__init__.py). The `swarmauri_vectorstore_qdrant` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_vectorstore_qdrant` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_vectorstore_qdrant` package directory for the maintained example source checks (Python compilation and non-Python file presence). Behavioral tests may live in the repository’s shared suites; the new README syntax test is not presented as runtime coverage for swarmauri Persistent Qdrant Vector Store.

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_vectorstore_qdrant` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_vectorstore_qdrant/swarmauri_vectorstore_qdrant/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_vectorstore_qdrant` provides swarmauri Persistent Qdrant Vector Store; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_vectorstore_qdrant`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_vectorstore_qdrant/swarmauri_vectorstore_qdrant/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_vectorstore_qdrant` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_vectorstore_qdrant/swarmauri_vectorstore_qdrant/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_vectorstore_qdrant/pyproject.toml) provide the supporting context for `swarmauri_vectorstore_qdrant`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.
- [swarmauri_embedding_doc2vec](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_embedding_doc2vec/README.md): A Doc2Vec based Embedding Model.
- [swarmauri_standard](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/30-standard-kernel/swarmauri_standard/README.md): First-party Swarmauri standard components for agents, tools, parsers, vectors, model adapters, and composable intelligence workflows.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_vectorstore_qdrant](https://pypi.org/project/swarmauri_vectorstore_qdrant/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.

### Development Setup

Work from the `pkgs/50-community/swarmauri_vectorstore_qdrant` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_vectorstore_qdrant` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_vectorstore_qdrant` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_vectorstore_qdrant/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_vectorstore_qdrant` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_vectorstore_qdrant` source version is `0.11.0.dev3`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_vectorstore_qdrant/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_vectorstore_qdrant/NOTICE) for attribution.
<!-- readme-standards:end notices -->
