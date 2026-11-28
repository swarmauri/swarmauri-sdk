# swarmauri_parser_pypdf2

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_parser_pypdf2</strong></p>
<p align="center">Page-by-page PDF text parser for Swarmauri using PyPDF2 with path and bytes input support.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_parser_pypdf2/"><img alt="pypi: swarmauri_parser_pypdf2" src="https://img.shields.io/pypi/v/swarmauri_parser_pypdf2?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_pypdf2/pyproject.toml"><img alt="Source version: 0.11.0" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_pypdf2/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_pypdf2/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_pypdf2/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_pypdf2/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_pypdf2/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_parser_pypdf2/"><img alt="Monthly PyPI downloads: swarmauri_parser_pypdf2" src="https://img.shields.io/pypi/dm/swarmauri_parser_pypdf2?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_pypdf2/README.md"><img alt="README hits: swarmauri_parser_pypdf2" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/50-community/swarmauri_parser_pypdf2/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_pypdf2/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_pypdf2/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_parser_pypdf2` is the Swarmauri PDF text parser for page-by-page
extraction using [PyPDF2](https://pypdf2.readthedocs.io/). It converts a PDF
file path or PDF bytes into a list of Swarmauri `Document` objects, preserving
page numbers and source metadata for downstream chunking, indexing, and agent
workflows.

### Why This Package

- Extract embedded PDF text without introducing OCR when the document already
  contains readable text objects.
- Preserve page boundaries by returning one `Document` per page.
- Accept either on-disk PDFs or PDF bytes already loaded in memory.
- Keep document ingestion aligned with the Swarmauri parser interface used
  across other loaders and converters.

### When to Use

Choose `swarmauri_parser_pypdf2` when your integration needs page-by-page PDF text parser for Swarmauri using PyPDF2 with path and bytes input support. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Page-by-page PDF text extraction through PyPDF2.
- Supports parsing from local file paths and raw PDF bytes.
- Returns Swarmauri `Document` objects with `content`, `page_number`, and
  `source`.
- Clean fit for ingestion pipelines, retrieval systems, and document analysis
  workflows.
- Supports Python 3.10, 3.11, 3.12, 3.13, and 3.14.

### Non-Goals

`swarmauri_parser_pypdf2` owns page-by-page PDF text parser for Swarmauri using PyPDF2 with path and bytes input support. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_pypdf2/pyproject.toml) declares runtime dependencies including `pypdf2`, `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. Read the example’s inputs and service requirements before execution.

### Installation

```bash
uv add swarmauri_parser_pypdf2
```

```bash
pip install swarmauri_parser_pypdf2
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_parser_pypdf2
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_parser_pypdf2
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_parser_pypdf2
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_pypdf2/docs/readme/quick_start.py).

```python
from swarmauri_parser_pypdf2 import PyPDF2Parser

parser = PyPDF2Parser()
documents = parser.parse("manuals/device.pdf")

for document in documents:
    print(document.metadata["page_number"])
    print(document.content[:160])
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_parser_pypdf2` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_pypdf2/docs/readme/usage.py).

```python
from swarmauri_parser_pypdf2 import PyPDF2Parser

parser = PyPDF2Parser()
documents = parser.parse("manuals/device.pdf")

for document in documents:
    print(document.metadata["page_number"])
    print(document.content[:160])
```
<!-- readme-standards:end example.usage -->

**Parse a PDF from bytes**

```python
from pathlib import Path
from swarmauri_parser_pypdf2 import PyPDF2Parser

pdf_bytes = Path("reports/statement.pdf").read_bytes()
parser = PyPDF2Parser()
pages = parser.parse(pdf_bytes)

for page in pages:
    print(page.metadata)
```

**Send parsed pages to downstream chunking**

```python
from swarmauri_parser_pypdf2 import PyPDF2Parser

parser = PyPDF2Parser()
pages = parser.parse("contracts/master-service-agreement.pdf")

for page in pages:
    if page.content.strip():
        print(page.metadata["page_number"], len(page.content))
```

### Configuration

Configure `swarmauri_parser_pypdf2` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_pypdf2/swarmauri_parser_pypdf2/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_pypdf2/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_parser_pypdf2` source raises `TypeError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

- Use this parser when the PDF already contains embedded text.
- Use OCR first for scan-only PDFs, then parse or post-process the OCR output.
- Validate encrypted, malformed, or image-only PDFs earlier in the ingestion
  pipeline so downstream processing can route them correctly.
- Keep in mind that page text extraction quality depends on the PDF's internal
  structure and reading order.

---

## Package Boundary

### What It Owns

`swarmauri_parser_pypdf2` is located in `community` and owns page-by-page PDF text parser for Swarmauri using PyPDF2 with path and bytes input support. Source-declared APIs include `PyPDF2Parser`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_pypdf2/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_parser_pypdf2`.

Source-declared exports or types: `PyPDF2Parser`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_pypdf2/swarmauri_parser_pypdf2/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.parsers` → `PyPDF2Parser` → `swarmauri_parser_pypdf2.PyPDF2Parser:PyPDF2Parser`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_parser_pypdf2` are `pypdf2`, `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_pypdf2/swarmauri_parser_pypdf2/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_parser_pypdf2` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_parser_pypdf2`, use the source-declared public interfaces (`PyPDF2Parser`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_parser_pypdf2` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_pypdf2/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_parser_pypdf2`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_pypdf2/swarmauri_parser_pypdf2/__init__.py). The `swarmauri_parser_pypdf2` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_parser_pypdf2` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_parser_pypdf2` package directory for the maintained example source checks (Python compilation and non-Python file presence). Behavioral tests may live in the repository’s shared suites; the new README syntax test is not presented as runtime coverage for page-by-page PDF text parser for Swarmauri using PyPDF2 with path and bytes input support.

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_parser_pypdf2` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_pypdf2/swarmauri_parser_pypdf2/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

> **What does this parser return?**
> A list of Swarmauri `Document` objects, usually one for each page that
> contains extractable text.

> **Can it parse PDF bytes instead of a file path?**
> Yes. `parse()` accepts either a string path or `bytes`.

> **Does it perform OCR on scanned PDFs?**
> No. PyPDF2 extracts embedded text. Scanned PDFs without text objects should
> be handled with OCR first.

> **What metadata is attached to each page?**
> Each returned document includes `page_number` and `source`.

### Why

**Why select this package?** `swarmauri_parser_pypdf2` provides page-by-page PDF text parser for Swarmauri using PyPDF2 with path and bytes input support; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_parser_pypdf2`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_pypdf2/swarmauri_parser_pypdf2/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_parser_pypdf2` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

- [PyPDF2 text extraction guide](https://pypdf2.readthedocs.io/en/3.x/user/extract-text.html)
- [PyPDF2 documentation](https://pypdf2.readthedocs.io/)
- [PyPDF2 on PyPI](https://pypi.org/project/PyPDF2/)

### Related Packages

- [swarmauri_parser_fitzpdf](https://pypi.org/project/swarmauri_parser_fitzpdf/)
- [swarmauri_parser_pypdftk](https://pypi.org/project/swarmauri_parser_pypdftk/)
- [swarmauri_ocr_pytesseract](https://pypi.org/project/swarmauri_ocr_pytesseract/)
- [swarmauri_parser_pypdf2](https://pypi.org/project/swarmauri_parser_pypdf2/)

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_parser_pypdf2](https://pypi.org/project/swarmauri_parser_pypdf2/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_parser_pypdf2`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/50-community/swarmauri_parser_pypdf2` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

**Swarmauri Foundations**

- [swarmauri](https://pypi.org/project/swarmauri/)
- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_parser_pypdf2` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_pypdf2/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_parser_pypdf2` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_parser_pypdf2` source version is `0.11.0`.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_pypdf2/LICENSE).
<!-- readme-standards:end license -->

This project is licensed under the Apache-2.0 License.

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_pypdf2/NOTICE) for attribution.
<!-- readme-standards:end notices -->
