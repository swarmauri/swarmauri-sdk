# swarmauri_parser_fitzpdf

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_parser_fitzpdf</strong></p>
<p align="center">High-performance PDF text parser for Swarmauri using PyMuPDF with aggregated whole-document output.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_parser_fitzpdf/"><img alt="pypi: swarmauri_parser_fitzpdf" src="https://img.shields.io/pypi/v/swarmauri_parser_fitzpdf"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_parser_fitzpdf/pyproject.toml"><img alt="Source version: 0.11.0.dev1" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev1&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_parser_fitzpdf/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_parser_fitzpdf/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_parser_fitzpdf/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_parser_fitzpdf/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_parser_fitzpdf/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_parser_fitzpdf/"><img alt="Monthly PyPI downloads: swarmauri_parser_fitzpdf" src="https://img.shields.io/pypi/dm/swarmauri_parser_fitzpdf"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_parser_fitzpdf/README.md"><img alt="README hits: swarmauri_parser_fitzpdf" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/community/swarmauri_parser_fitzpdf/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_parser_fitzpdf/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_parser_fitzpdf/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_parser_fitzpdf` is the Swarmauri PDF parser for high-performance
text extraction using [PyMuPDF](https://pymupdf.readthedocs.io/). It opens a
PDF, extracts text from every page, and returns a single Swarmauri `Document`
with the aggregated content and source metadata.

### Why This Package

- Use PyMuPDF's fast document engine for PDF extraction inside Swarmauri
  ingestion and indexing pipelines.
- Produce one normalized `Document` for whole-file workflows such as
  summarization, classification, or chunking after parse.
- Keep PDF parsing logic aligned with the Swarmauri parser interface used by
  other loaders and processors.
- Stay flexible if you later need PyMuPDF-specific extraction modes or OCR
  augmentation upstream.

### When to Use

Choose `swarmauri_parser_fitzpdf` when your integration needs high-performance PDF text parser for Swarmauri using PyMuPDF with aggregated whole-document output. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Aggregated PDF text extraction through PyMuPDF.
- Preserves the original source path in document metadata.
- Uses a lightweight Swarmauri parser surface for document pipelines.
- Appropriate for whole-document ingestion, chunking, and retrieval setup.
- Supports Python 3.10, 3.11, 3.12, 3.13, and 3.14.

### Non-Goals

`swarmauri_parser_fitzpdf` owns high-performance PDF text parser for Swarmauri using PyMuPDF with aggregated whole-document output. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_parser_fitzpdf/pyproject.toml) declares runtime dependencies including `pymupdf`, `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. Read the example’s inputs and service requirements before execution.

### Installation

```bash
uv add swarmauri_parser_fitzpdf
```

```bash
pip install swarmauri_parser_fitzpdf
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_parser_fitzpdf
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_parser_fitzpdf
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_parser_fitzpdf
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_parser_fitzpdf/docs/readme/quick_start.py).

```python
from swarmauri_parser_fitzpdf import FitzPdfParser

parser = FitzPdfParser()
documents = parser.parse("reports/quarterly.pdf")

for document in documents:
    print(document.metadata["source"])
    print(document.content[:500])
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_parser_fitzpdf` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_parser_fitzpdf/docs/readme/usage.py).

```python
from swarmauri_parser_fitzpdf import FitzPdfParser

parser = FitzPdfParser()
documents = parser.parse("reports/quarterly.pdf")

for document in documents:
    print(document.metadata["source"])
    print(document.content[:500])
```
<!-- readme-standards:end example.usage -->

**Parse a PDF into a single document**

```python
from swarmauri_parser_fitzpdf import FitzPdfParser

parser = FitzPdfParser()
docs = parser.parse("whitepapers/roadmap.pdf")

if docs:
    print(len(docs[0].content))
```

**Handle invalid input safely**

```python
from swarmauri_parser_fitzpdf import FitzPdfParser

parser = FitzPdfParser()

try:
    docs = parser.parse("missing.pdf")
    if not docs:
        print("Parsing failed or returned no text.")
except ValueError as exc:
    print(exc)
```

### Configuration

Configure `swarmauri_parser_fitzpdf` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_parser_fitzpdf/swarmauri_parser_fitzpdf/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_parser_fitzpdf/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_parser_fitzpdf` source raises `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

- Use this parser when you want a whole-document text payload rather than
  page-by-page output.
- Use OCR earlier in the flow for scan-only documents that have no extractable
  text layer.
- Cache parse output for large PDFs if the same files are processed repeatedly.
- If reading order matters, verify the extracted output on representative
  documents because PDF text order depends on document structure.

---

## Package Boundary

### What It Owns

`swarmauri_parser_fitzpdf` is located in `community` and owns high-performance PDF text parser for Swarmauri using PyMuPDF with aggregated whole-document output. Source-declared APIs include `FitzPdfParser`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_parser_fitzpdf/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_parser_fitzpdf`.

Source-declared exports or types: `FitzPdfParser`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_parser_fitzpdf/swarmauri_parser_fitzpdf/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.parsers` → `FitzPdfParser` → `swarmauri_parser_fitzpdf.FitzPdfParser:FitzPdfParser`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_parser_fitzpdf` are `pymupdf`, `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_parser_fitzpdf/swarmauri_parser_fitzpdf/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_parser_fitzpdf` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_parser_fitzpdf`, use the source-declared public interfaces (`FitzPdfParser`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_parser_fitzpdf` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_parser_fitzpdf/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_parser_fitzpdf`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_parser_fitzpdf/swarmauri_parser_fitzpdf/__init__.py). The `swarmauri_parser_fitzpdf` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_parser_fitzpdf` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_parser_fitzpdf` package directory for the maintained example source checks (Python compilation and non-Python file presence). Behavioral tests may live in the repository’s shared suites; the new README syntax test is not presented as runtime coverage for high-performance PDF text parser for Swarmauri using PyMuPDF with aggregated whole-document output.

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_parser_fitzpdf` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_parser_fitzpdf/swarmauri_parser_fitzpdf/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

> **What does this parser return?**
> A list containing one Swarmauri `Document` whose `content` holds the combined
> extracted text for the PDF.

> **Does it return one document per page?**
> No. This parser aggregates all page text into a single document.

> **Can it parse scanned PDFs with no text layer?**
> Not by itself. PyMuPDF extracts text objects already present in the document.
> Scan-only PDFs should be OCR'd first.

> **What input type does it expect?**
> A file path string pointing to a local PDF.

### Why

**Why select this package?** `swarmauri_parser_fitzpdf` provides high-performance PDF text parser for Swarmauri using PyMuPDF with aggregated whole-document output; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_parser_fitzpdf`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_parser_fitzpdf/swarmauri_parser_fitzpdf/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_parser_fitzpdf` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

- [PyMuPDF basics](https://pymupdf.readthedocs.io/en/latest/the-basics.html)
- [PyMuPDF text extraction details](https://pymupdf.readthedocs.io/en/latest/app1.html)
- [PyMuPDF text recipes](https://pymupdf.readthedocs.io/en/latest/recipes-text.html)

### Related Packages

- [swarmauri_parser_pypdf2](https://pypi.org/project/swarmauri_parser_pypdf2/)
- [swarmauri_parser_pypdftk](https://pypi.org/project/swarmauri_parser_pypdftk/)
- [swarmauri_ocr_pytesseract](https://pypi.org/project/swarmauri_ocr_pytesseract/)
- [swarmauri_parser_fitzpdf](https://pypi.org/project/swarmauri_parser_fitzpdf/)

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_parser_fitzpdf](https://pypi.org/project/swarmauri_parser_fitzpdf/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_parser_fitzpdf`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/community/swarmauri_parser_fitzpdf` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

**Swarmauri Foundations**

- [swarmauri](https://pypi.org/project/swarmauri/)
- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_parser_fitzpdf` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_parser_fitzpdf/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_parser_fitzpdf` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_parser_fitzpdf` source version is `0.11.0.dev1`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_parser_fitzpdf/LICENSE).
<!-- readme-standards:end license -->

This project is licensed under the Apache-2.0 License.

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_parser_fitzpdf/NOTICE) for attribution.
<!-- readme-standards:end notices -->
