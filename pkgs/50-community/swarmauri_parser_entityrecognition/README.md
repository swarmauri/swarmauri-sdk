# swarmauri_parser_entityrecognition

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_parser_entityrecognition</strong></p>
<p align="center">spaCy-based named-entity recognition parser for Swarmauri with structured entity document output.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_parser_entityrecognition/"><img alt="pypi: swarmauri_parser_entityrecognition" src="https://img.shields.io/pypi/v/swarmauri_parser_entityrecognition"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_entityrecognition/pyproject.toml"><img alt="Source version: 0.11.0.dev1" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev1&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_entityrecognition/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_entityrecognition/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_entityrecognition/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_entityrecognition/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_entityrecognition/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_parser_entityrecognition/"><img alt="Monthly PyPI downloads: swarmauri_parser_entityrecognition" src="https://img.shields.io/pypi/dm/swarmauri_parser_entityrecognition"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_entityrecognition/README.md"><img alt="README hits: swarmauri_parser_entityrecognition" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/50-community/swarmauri_parser_entityrecognition/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_entityrecognition/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_entityrecognition/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_parser_entityrecognition` is the Swarmauri named-entity recognition
parser built on [spaCy](https://spacy.io/). It extracts named entities such as
people, organizations, and geopolitical entities from unstructured text and
returns Swarmauri `Document` objects containing the entity text and entity
metadata.

### Why This Package

- Turn raw text into structured entity objects inside a Swarmauri parser
  workflow.
- Preserve entity labels and entity ids in a predictable `Document` shape for
  downstream enrichment, filtering, or indexing.
- Use spaCy's English NER pipeline when available, while still retaining a
  minimal fallback path for constrained environments.
- Fit entity extraction into larger ingestion, retrieval, anonymization, and
  knowledge-graph workflows.

### When to Use

Choose `swarmauri_parser_entityrecognition` when your integration needs spaCy-based named-entity recognition parser for Swarmauri with structured entity document output. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Named-entity extraction via spaCy's English NER model.
- Automatic attempt to download `en_core_web_sm` if the model is missing.
- Best-effort fallback behavior for environments where the full model cannot be
  loaded.
- Returns Swarmauri `Document` objects with entity label metadata.
- Supports Python 3.10, 3.11, 3.12, 3.13, and 3.14.

### Non-Goals

`swarmauri_parser_entityrecognition` owns spaCy-based named-entity recognition parser for Swarmauri with structured entity document output. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_entityrecognition/pyproject.toml) declares runtime dependencies including `spacy`, `spacy-lookups-data`, `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. Read the example’s inputs and service requirements before execution.

### Installation

```bash
uv add swarmauri_parser_entityrecognition
```

```bash
pip install swarmauri_parser_entityrecognition
```

Optional model bootstrap:

```bash
python -m spacy download en_core_web_sm
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_parser_entityrecognition
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_parser_entityrecognition
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_parser_entityrecognition
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_entityrecognition/docs/readme/quick_start.py).

```python
from swarmauri_parser_entityrecognition import EntityRecognitionParser

text = (
    "Barack Obama was born in Hawaii and served as "
    "President of the United States."
)
parser = EntityRecognitionParser()
entities = parser.parse(text)

for entity in entities:
    print(entity.content, entity.metadata["entity_type"])
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_parser_entityrecognition` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_entityrecognition/docs/readme/usage.py).

```python
from swarmauri_parser_entityrecognition import EntityRecognitionParser

text = (
    "Barack Obama was born in Hawaii and served as "
    "President of the United States."
)
parser = EntityRecognitionParser()
entities = parser.parse(text)

for entity in entities:
    print(entity.content, entity.metadata["entity_type"])
```
<!-- readme-standards:end example.usage -->

**Parse organizations, places, and people**

```python
from swarmauri_parser_entityrecognition import EntityRecognitionParser

parser = EntityRecognitionParser()
docs = parser.parse(
    "Apple Inc. is planning to open a new office in New York City, according to CEO Tim Cook."
)

for doc in docs:
    print(doc.content, doc.metadata)
```

**Handle non-string input**

```python
from swarmauri_parser_entityrecognition import EntityRecognitionParser

parser = EntityRecognitionParser()
print(parser.parse(42))
```

**Inspect fallback-compatible metadata**

```python
from swarmauri_parser_entityrecognition import EntityRecognitionParser

parser = EntityRecognitionParser()
entities = parser.parse("Tim Cook announced new products in New York City for Apple Inc.")
print([entity.metadata for entity in entities])
```

### Configuration

Configure `swarmauri_parser_entityrecognition` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_entityrecognition/swarmauri_parser_entityrecognition/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_entityrecognition/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_parser_entityrecognition` source raises `OSError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

- Preinstall `en_core_web_sm` in CI and production environments to avoid
  runtime downloads.
- Treat the regex fallback as a compatibility path, not as production-quality
  entity recognition.
- Strip markup or noisy boilerplate before parsing to improve entity quality.
- Persist entity spans or link them to downstream IDs if you need durable
  knowledge-graph or indexing workflows.

---

## Package Boundary

### What It Owns

`swarmauri_parser_entityrecognition` is located in `community` and owns spaCy-based named-entity recognition parser for Swarmauri with structured entity document output. Source-declared APIs include `EntityRecognitionParser`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_entityrecognition/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_parser_entityrecognition`.

Source-declared exports or types: `EntityRecognitionParser`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_entityrecognition/swarmauri_parser_entityrecognition/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.parsers` → `EntityRecognitionParser` → `swarmauri_parser_entityrecognition.EntityRecognitionParser:EntityRecognitionParser`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_parser_entityrecognition` are `spacy`, `spacy-lookups-data`, `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_entityrecognition/swarmauri_parser_entityrecognition/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_parser_entityrecognition` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_parser_entityrecognition`, use the source-declared public interfaces (`EntityRecognitionParser`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_parser_entityrecognition` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_entityrecognition/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_parser_entityrecognition`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_entityrecognition/swarmauri_parser_entityrecognition/__init__.py). The `swarmauri_parser_entityrecognition` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_parser_entityrecognition` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_parser_entityrecognition` package directory for the maintained example source checks (Python compilation and non-Python file presence). Behavioral tests may live in the repository’s shared suites; the new README syntax test is not presented as runtime coverage for spaCy-based named-entity recognition parser for Swarmauri with structured entity document output.

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_parser_entityrecognition` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_entityrecognition/swarmauri_parser_entityrecognition/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

> **What does this parser return?**
> A list of Swarmauri `Document` objects, usually one per detected entity.

> **Which metadata fields are included?**
> `entity_type`, `entity_id`, and `text`.

> **What spaCy model does it use?**
> It tries to load `en_core_web_sm`.

> **What happens if the model is unavailable?**
> The parser attempts to download the model. If that fails, it falls back to a
> blank English pipeline plus a small regex-based fallback used as a best-effort
> compatibility path.

### Why

**Why select this package?** `swarmauri_parser_entityrecognition` provides spaCy-based named-entity recognition parser for Swarmauri with structured entity document output; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_parser_entityrecognition`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_entityrecognition/swarmauri_parser_entityrecognition/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_parser_entityrecognition` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

- [spaCy named entity recognition docs](https://spacy.io/usage/linguistic-features#named-entities)
- [spaCy model installation docs](https://spacy.io/usage/models)

### Related Packages

- [swarmauri_tool_entityrecognition](https://pypi.org/project/swarmauri_tool_entityrecognition/)
- [swarmauri_tool_sentimentanalysis](https://pypi.org/project/swarmauri_tool_sentimentanalysis/)
- [swarmauri_parser_textblob](https://pypi.org/project/swarmauri_parser_textblob/)
- [swarmauri_parser_bertembedding](https://pypi.org/project/swarmauri_parser_bertembedding/)

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_parser_entityrecognition](https://pypi.org/project/swarmauri_parser_entityrecognition/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_parser_entityrecognition`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/50-community/swarmauri_parser_entityrecognition` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

**Swarmauri Foundations**

- [swarmauri](https://pypi.org/project/swarmauri/)
- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_parser_entityrecognition` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_entityrecognition/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_parser_entityrecognition` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_parser_entityrecognition` source version is `0.11.0.dev1`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_entityrecognition/LICENSE).
<!-- readme-standards:end license -->

This project is licensed under the Apache-2.0 License.

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_entityrecognition/NOTICE) for attribution.
<!-- readme-standards:end notices -->
