# swarmauri_parser_pypdftk

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_parser_pypdftk</strong></p>
<p align="center">PDF AcroForm field parser for Swarmauri using PyPDFTK and the native pdftk toolchain.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_parser_pypdftk/"><img alt="pypi: swarmauri_parser_pypdftk" src="https://img.shields.io/pypi/v/swarmauri_parser_pypdftk?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_pypdftk/pyproject.toml"><img alt="Source version: 0.11.0.dev3" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev3&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_pypdftk/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_pypdftk/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_pypdftk/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_pypdftk/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_pypdftk/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_parser_pypdftk/"><img alt="Monthly PyPI downloads: swarmauri_parser_pypdftk" src="https://img.shields.io/pypi/dm/swarmauri_parser_pypdftk?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_pypdftk/README.md"><img alt="README hits: swarmauri_parser_pypdftk" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/50-community/swarmauri_parser_pypdftk/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_pypdftk/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_pypdftk/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_parser_pypdftk` is the Swarmauri PDF form-field parser for
extracting AcroForm data through [PyPDFTK](https://pypi.org/project/pypdftk/)
and the native `pdftk` toolchain. It converts structured PDF form fields into a
single Swarmauri `Document` so downstream workflows can index, validate, or
route filled forms.

### Why This Package

- Extract structured PDF field data instead of only free-form text.
- Normalize AcroForm output into a Swarmauri `Document` for ingestion,
  automation, and analysis pipelines.
- Keep form parsing aligned with the same Swarmauri parser interface used by
  other document components.
- Pair form-field extraction with other PDF parsers when both structured fields
  and page text matter.

### When to Use

Choose `swarmauri_parser_pypdftk` when your integration needs pDF AcroForm field parser for Swarmauri using PyPDFTK and the native pdftk toolchain. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Extracts PDF AcroForm fields through PyPDFTK.
- Returns one Swarmauri `Document` with newline-delimited `key: value` content.
- Preserves the input source path in metadata.
- Useful for form ingestion, validation, compliance workflows, and automation.
- Supports Python 3.10, 3.11, 3.12, 3.13, and 3.14.

### Non-Goals

`swarmauri_parser_pypdftk` owns pDF AcroForm field parser for Swarmauri using PyPDFTK and the native pdftk toolchain. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_pypdftk/pyproject.toml) declares runtime dependencies including `pypdftk`, `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. Read the example’s inputs and service requirements before execution.

### Installation

```bash
uv add swarmauri_parser_pypdftk
```

```bash
pip install swarmauri_parser_pypdftk
```

System requirement:

- Install `pdftk` or `pdftk-java` and make sure the executable is available on
  `PATH`.

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_parser_pypdftk
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_parser_pypdftk
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_parser_pypdftk
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_pypdftk/docs/readme/quick_start.py).

```python
from swarmauri_parser_pypdftk import PyPDFTKParser

parser = PyPDFTKParser()
documents = parser.parse("forms/enrollment.pdf")

for document in documents:
    print(document.metadata["source"])
    print(document.content)
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_parser_pypdftk` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_pypdftk/docs/readme/usage.py).

```python
from swarmauri_parser_pypdftk import PyPDFTKParser

parser = PyPDFTKParser()
documents = parser.parse("forms/enrollment.pdf")

for document in documents:
    print(document.metadata["source"])
    print(document.content)
```
<!-- readme-standards:end example.usage -->

**Extract form fields from a filled PDF**

```python
from swarmauri_parser_pypdftk import PyPDFTKParser

parser = PyPDFTKParser()
docs = parser.parse("forms/application.pdf")

if docs:
    print(docs[0].content)
```

Example output:

```text
GivenName: John
FamilyName: Doe
BirthDate: 1990-01-01
```

**Detect forms without field data**

```python
from swarmauri_parser_pypdftk import PyPDFTKParser

parser = PyPDFTKParser()
docs = parser.parse("forms/plain.pdf")

if not docs:
    print("No PDF form fields were detected.")
```

### Configuration

Configure `swarmauri_parser_pypdftk` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_pypdftk/swarmauri_parser_pypdftk/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_pypdftk/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_parser_pypdftk` source raises `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

- Use this parser for PDFs with real AcroForm fields, not for generic PDF page
  text.
- Validate that the `pdftk` binary is installed in deployment targets before
  running pipelines that depend on this package.
- Pair this package with `swarmauri_parser_pypdf2` or
  `swarmauri_parser_fitzpdf` if you also need free-form page text.
- Route scan-only documents through OCR if they are image-based and contain no
  useful form structure.

---

## Package Boundary

### What It Owns

`swarmauri_parser_pypdftk` is located in `community` and owns pDF AcroForm field parser for Swarmauri using PyPDFTK and the native pdftk toolchain. Source-declared APIs include `PyPDFTKParser`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_pypdftk/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_parser_pypdftk`.

Source-declared exports or types: `PyPDFTKParser`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_pypdftk/swarmauri_parser_pypdftk/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.parsers` → `PyPDFTKParser` → `swarmauri_parser_pypdftk.PyPDFTKParser:PyPDFTKParser`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_parser_pypdftk` are `pypdftk`, `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_pypdftk/swarmauri_parser_pypdftk/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_parser_pypdftk` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_parser_pypdftk`, use the source-declared public interfaces (`PyPDFTKParser`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_parser_pypdftk` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_pypdftk/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_parser_pypdftk`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_pypdftk/swarmauri_parser_pypdftk/__init__.py). The `swarmauri_parser_pypdftk` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_parser_pypdftk` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_parser_pypdftk` package directory for the maintained example source checks (Python compilation and non-Python file presence). Behavioral tests may live in the repository’s shared suites; the new README syntax test is not presented as runtime coverage for pDF AcroForm field parser for Swarmauri using PyPDFTK and the native pdftk toolchain.

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_parser_pypdftk` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_pypdftk/swarmauri_parser_pypdftk/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

> **What does this parser extract?**
> PDF form fields returned by `pypdftk.dump_data_fields`, such as AcroForm
> names and values.

> **Does it parse ordinary PDF text?**
> No. This package is for structured PDF form fields. Use another parser for
> general page text.

> **Does it need a system binary?**
> Yes. It depends on the `pdftk` or `pdftk-java` executable being installed and
> available on `PATH`.

> **What happens when the PDF has no form fields?**
> The parser returns an empty list.

### Why

**Why select this package?** `swarmauri_parser_pypdftk` provides pDF AcroForm field parser for Swarmauri using PyPDFTK and the native pdftk toolchain; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_parser_pypdftk`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_pypdftk/swarmauri_parser_pypdftk/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_parser_pypdftk` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

- [PyPDFTK on PyPI](https://pypi.org/project/pypdftk/)
- [pdftk-java project](https://gitlab.com/pdftk-java/pdftk)

### Related Packages

- [swarmauri_parser_pypdf2](https://pypi.org/project/swarmauri_parser_pypdf2/)
- [swarmauri_parser_fitzpdf](https://pypi.org/project/swarmauri_parser_fitzpdf/)
- [swarmauri_ocr_pytesseract](https://pypi.org/project/swarmauri_ocr_pytesseract/)
- [swarmauri_parser_pypdftk](https://pypi.org/project/swarmauri_parser_pypdftk/)

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_parser_pypdftk](https://pypi.org/project/swarmauri_parser_pypdftk/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_parser_pypdftk`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/50-community/swarmauri_parser_pypdftk` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

**Swarmauri Foundations**

- [swarmauri](https://pypi.org/project/swarmauri/)
- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_parser_pypdftk` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_pypdftk/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_parser_pypdftk` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_parser_pypdftk` source version is `0.11.0.dev3`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_pypdftk/LICENSE).
<!-- readme-standards:end license -->

This project is licensed under the Apache-2.0 License.

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_parser_pypdftk/NOTICE) for attribution.
<!-- readme-standards:end notices -->
