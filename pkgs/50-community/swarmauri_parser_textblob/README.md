# swarmauri_parser_textblob

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_parser_textblob</strong></p>
<p align="center">Lightweight sentence and noun-phrase parsing package for Swarmauri built on TextBlob and NLTK.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_parser_textblob/"><img alt="pypi: swarmauri_parser_textblob" src="https://img.shields.io/pypi/v/swarmauri_parser_textblob?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_textblob/pyproject.toml"><img alt="Source version: 0.11.0" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_textblob/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_textblob/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_textblob/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_textblob/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_textblob/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_parser_textblob/"><img alt="Monthly PyPI downloads: swarmauri_parser_textblob" src="https://img.shields.io/pypi/dm/swarmauri_parser_textblob?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_textblob/README.md"><img alt="README hits: swarmauri_parser_textblob" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/50-community/swarmauri_parser_textblob/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_textblob/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_textblob/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_parser_textblob` provides two Swarmauri text parsing components built
on [TextBlob](https://textblob.readthedocs.io/): `TextBlobSentenceParser` for
sentence segmentation and `TextBlobNounParser` for noun-phrase extraction. It
is designed for lightweight NLP preprocessing before chunking, retrieval,
classification, or agent workflows.

### Why This Package

- Split long passages into sentence-level documents for downstream processing.
- Extract noun phrases without introducing a larger transformer stack.
- Keep lightweight linguistic preprocessing aligned with the Swarmauri parser
  interface.
- Use simple NLP enrichment before embeddings, retrieval, or task routing.

### When to Use

Choose `swarmauri_parser_textblob` when your integration needs lightweight sentence and noun-phrase parsing package for Swarmauri built on TextBlob and NLTK. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Sentence segmentation through `TextBlobSentenceParser`.
- Noun phrase extraction through `TextBlobNounParser`.
- Fits Swarmauri ingestion and preprocessing workflows using parser-style
  components.
- Useful for lightweight English NLP pipelines where a smaller dependency stack
  is preferred.
- Supports Python 3.10, 3.11, 3.12, 3.13, and 3.14.

### Non-Goals

`swarmauri_parser_textblob` owns lightweight sentence and noun-phrase parsing package for Swarmauri built on TextBlob and NLTK. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_textblob/pyproject.toml) declares runtime dependencies including `textblob`, `nltk`, `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. Read the example’s inputs and service requirements before execution.

### Installation

```bash
uv add swarmauri_parser_textblob
```

```bash
pip install swarmauri_parser_textblob
```

Optional setup:

```bash
python -m textblob.download_corpora
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_parser_textblob
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_parser_textblob
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_parser_textblob
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_textblob/docs/readme/quick_start.py).

```python
from swarmauri_parser_textblob import TextBlobSentenceParser

parser = TextBlobSentenceParser()
documents = parser.parse(
    "One more large chapula please. It should be extra spicy!"
)

for document in documents:
    print(document.content)
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_parser_textblob` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_textblob/docs/readme/usage.py).

```python
from swarmauri_parser_textblob import TextBlobSentenceParser

parser = TextBlobSentenceParser()
documents = parser.parse(
    "One more large chapula please. It should be extra spicy!"
)

for document in documents:
    print(document.content)
```
<!-- readme-standards:end example.usage -->

**Sentence parsing**


**Noun phrase extraction**

```python
from swarmauri_parser_textblob import TextBlobNounParser

parser = TextBlobNounParser()
documents = parser.parse("One more large chapula please.")

print(documents[0].content)
print(documents[0].metadata["noun_phrases"])
```

**Prepare sentence-level documents**

```python
from swarmauri_parser_textblob import TextBlobSentenceParser

parser = TextBlobSentenceParser()
sentences = parser.parse(
    "Swarmauri coordinates tools. It also routes data through composable components."
)

for sentence in sentences:
    print(sentence.metadata["parser"], sentence.content)
```

**Extract noun phrases for downstream tagging**

```python
from swarmauri_parser_textblob import TextBlobNounParser

parser = TextBlobNounParser()
docs = parser.parse("The Swarmauri agent indexed a customer support knowledge base.")

print(docs[0].metadata["noun_phrases"])
```

### Configuration

Configure `swarmauri_parser_textblob` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_textblob/swarmauri_parser_textblob/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_textblob/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_parser_textblob` source raises `RuntimeError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

- Pre-download NLTK corpora in CI, containers, or production images to avoid
  runtime setup costs.
- Use these parsers for lightweight English NLP tasks; domain-specific or
  multilingual corpora may require a different component.
- Combine sentence parsing with embeddings or vector stores when building
  retrieval-oriented pipelines.
- Treat noun phrase extraction as heuristic enrichment rather than a strict
  ontology or entity-linking system.

---

## Package Boundary

### What It Owns

`swarmauri_parser_textblob` is located in `community` and owns lightweight sentence and noun-phrase parsing package for Swarmauri built on TextBlob and NLTK. Source-declared APIs include `TextBlobNounParser`, `TextBlobSentenceParser`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_textblob/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_parser_textblob`.

Source-declared exports or types: `TextBlobNounParser`, `TextBlobSentenceParser`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_textblob/swarmauri_parser_textblob/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.parsers` → `TextBlobNounParser` → `swarmauri_parser_textblob.TextBlobNounParser:TextBlobNounParser`
- `swarmauri.parsers` → `TextBlobSentenceParser` → `swarmauri_parser_textblob.TextBlobSentenceParser:TextBlobSentenceParser`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_parser_textblob` are `textblob`, `nltk`, `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_textblob/swarmauri_parser_textblob/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_parser_textblob` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_parser_textblob`, use the source-declared public interfaces (`TextBlobNounParser`, `TextBlobSentenceParser`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_parser_textblob` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_textblob/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_parser_textblob`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_textblob/swarmauri_parser_textblob/__init__.py). The `swarmauri_parser_textblob` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_parser_textblob` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_parser_textblob` package directory for the maintained example source checks (Python compilation and non-Python file presence). Behavioral tests may live in the repository’s shared suites; the new README syntax test is not presented as runtime coverage for lightweight sentence and noun-phrase parsing package for Swarmauri built on TextBlob and NLTK.

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_parser_textblob` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_textblob/swarmauri_parser_textblob/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

> **What parser classes are included?**
> `TextBlobSentenceParser` and `TextBlobNounParser`.

> **What does the sentence parser return?**
> A `Document` per detected sentence, with metadata indicating the parser.

> **What does the noun parser return?**
> A single `Document` containing the original text and a `noun_phrases` list in
> metadata.

> **Does it require NLTK resources?**
> Yes. The package downloads required NLTK corpora during initialization unless
> they are already present.

### Why

**Why select this package?** `swarmauri_parser_textblob` provides lightweight sentence and noun-phrase parsing package for Swarmauri built on TextBlob and NLTK; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_parser_textblob`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_textblob/swarmauri_parser_textblob/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_parser_textblob` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

- [TextBlob documentation](https://textblob.readthedocs.io/)
- [NLTK documentation](https://www.nltk.org/)

### Related Packages

- [swarmauri_parser_entityrecognition](https://pypi.org/project/swarmauri_parser_entityrecognition/)
- [swarmauri_tool_entityrecognition](https://pypi.org/project/swarmauri_tool_entityrecognition/)
- [swarmauri_tool_sentimentanalysis](https://pypi.org/project/swarmauri_tool_sentimentanalysis/)
- [swarmauri_parser_bertembedding](https://pypi.org/project/swarmauri_parser_bertembedding/)

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_parser_textblob](https://pypi.org/project/swarmauri_parser_textblob/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_parser_textblob`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/50-community/swarmauri_parser_textblob` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

**Swarmauri Foundations**

- [swarmauri](https://pypi.org/project/swarmauri/)
- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_parser_textblob` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_textblob/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_parser_textblob` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_parser_textblob` source version is `0.11.0`.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_textblob/LICENSE).
<!-- readme-standards:end license -->

This project is licensed under the Apache-2.0 License.

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_textblob/NOTICE) for attribution.
<!-- readme-standards:end notices -->
