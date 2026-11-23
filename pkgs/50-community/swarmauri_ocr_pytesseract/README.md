# swarmauri_ocr_pytesseract

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_ocr_pytesseract</strong></p>
<p align="center">Local Tesseract OCR adapter for Swarmauri with sync, async, and batch image-to-text workflows.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_ocr_pytesseract/"><img alt="pypi: swarmauri_ocr_pytesseract" src="https://img.shields.io/pypi/v/swarmauri_ocr_pytesseract?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_ocr_pytesseract/pyproject.toml"><img alt="Source version: 0.11.0.dev3" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev3&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_ocr_pytesseract/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_ocr_pytesseract/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_ocr_pytesseract/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_ocr_pytesseract/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_ocr_pytesseract/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_ocr_pytesseract/"><img alt="Monthly PyPI downloads: swarmauri_ocr_pytesseract" src="https://img.shields.io/pypi/dm/swarmauri_ocr_pytesseract?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_ocr_pytesseract/README.md"><img alt="README hits: swarmauri_ocr_pytesseract" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/50-community/swarmauri_ocr_pytesseract/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_ocr_pytesseract/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_ocr_pytesseract/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_ocr_pytesseract` is the Swarmauri OCR adapter for running local
Tesseract-powered image-to-text extraction through a consistent Swarmauri
`OCRBase` interface. It accepts file paths, raw bytes, or in-memory PIL images
and supports synchronous, asynchronous, and batch OCR workflows.

### Why This Package

- Use the same OCR component shape across local and pipeline-based Swarmauri
  workflows.
- Run OCR on local infrastructure without routing images through a hosted API.
- Tune Tesseract language selection and engine flags for receipts, forms,
  scanned PDFs, screenshots, and other document images.
- Reuse the same component in parsing, ingestion, indexing, and agent
  workflows.

### When to Use

Choose `swarmauri_ocr_pytesseract` when your integration needs local Tesseract OCR adapter for Swarmauri with sync, async, and batch image-to-text workflows. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Local OCR backed by [PyTesseract](https://pypi.org/project/pytesseract/) and
  [Tesseract OCR](https://tesseract-ocr.github.io/).
- Supports configurable `language`, `config`, and explicit `tesseract_cmd`
  resolution.
- Accepts paths, bytes, and PIL image objects.
- Includes `extract_text`, `aextract_text`, `batch`, and `abatch` methods.
- Can report installed OCR languages through `get_supported_languages()`.
- Supports Python 3.10, 3.11, 3.12, 3.13, and 3.14.

### Non-Goals

`swarmauri_ocr_pytesseract` owns local Tesseract OCR adapter for Swarmauri with sync, async, and batch image-to-text workflows. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_ocr_pytesseract/pyproject.toml) declares runtime dependencies including `pytesseract`, `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. Read the example’s inputs and service requirements before execution.

### Installation

```bash
uv add swarmauri_ocr_pytesseract
```

```bash
pip install swarmauri_ocr_pytesseract
```

System requirement:

- Install the native `tesseract` binary and ensure it is available on `PATH`,
  or set `TESSERACT_CMD` to the executable location.

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_ocr_pytesseract
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_ocr_pytesseract
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_ocr_pytesseract
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_ocr_pytesseract/docs/readme/quick_start.py).

```python
from swarmauri_ocr_pytesseract import PytesseractOCR

ocr = PytesseractOCR(language="eng", config="--psm 6")
text = ocr.extract_text("docs/invoice.png")
print(text)
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_ocr_pytesseract` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_ocr_pytesseract/docs/readme/usage.py).

```python
from swarmauri_ocr_pytesseract import PytesseractOCR

ocr = PytesseractOCR(language="eng", config="--psm 6")
text = ocr.extract_text("docs/invoice.png")
print(text)
```
<!-- readme-standards:end example.usage -->

**OCR from image bytes**

```python
from pathlib import Path
from swarmauri_ocr_pytesseract import PytesseractOCR

ocr = PytesseractOCR(language="eng")
image_bytes = Path("receipts/ticket.png").read_bytes()
text = ocr.extract_text(image_bytes)
print(text)
```

**OCR from a PIL image**

```python
from PIL import Image
from swarmauri_ocr_pytesseract import PytesseractOCR

image = Image.open("scans/form.png")
ocr = PytesseractOCR(language="eng", config="--oem 3 --psm 4")
print(ocr.extract_text(image))
```

**Async batch OCR**

```python
import asyncio
from swarmauri_ocr_pytesseract import PytesseractOCR

ocr = PytesseractOCR(language="eng")

async def run():
    results = await ocr.abatch(
        ["scans/page1.png", "scans/page2.png", "scans/page3.png"],
        max_concurrent=2,
    )
    for index, text in enumerate(results, start=1):
        print(index, text[:120])

asyncio.run(run())
```

**List installed OCR languages**

```python
from swarmauri_ocr_pytesseract import PytesseractOCR

ocr = PytesseractOCR()
print(ocr.get_supported_languages())
```

### Configuration

The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_ocr_pytesseract/swarmauri_ocr_pytesseract/__init__.py) references configuration keys `TESSERACT_CMD`. Consult the constructor or function signature before supplying them; a referenced key is not necessarily a global environment variable.

### Error Handling

The inspected `swarmauri_ocr_pytesseract` source raises `Exception`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

- Use `--psm` and `--oem` options through `config` to match the page layout you
  expect.
- Install the correct `.traineddata` language packs for multilingual OCR.
- Pre-process noisy or skewed scans before OCR to improve extraction quality.
- Use PDF parsers when a PDF already contains embedded text; use OCR when the
  PDF or image is scan-only.

---

## Package Boundary

### What It Owns

`swarmauri_ocr_pytesseract` is located in `community` and owns local Tesseract OCR adapter for Swarmauri with sync, async, and batch image-to-text workflows. Source-declared APIs include `PytesseractOCR`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_ocr_pytesseract/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_ocr_pytesseract`.

Source-declared exports or types: `PytesseractOCR`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_ocr_pytesseract/swarmauri_ocr_pytesseract/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.ocrs` → `PytesseractOCR` → `swarmauri_ocr_pytesseract.PytesseractOCR:PytesseractOCR`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_ocr_pytesseract` are `pytesseract`, `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_ocr_pytesseract/swarmauri_ocr_pytesseract/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_ocr_pytesseract` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_ocr_pytesseract`, use the source-declared public interfaces (`PytesseractOCR`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_ocr_pytesseract` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_ocr_pytesseract/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_ocr_pytesseract`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_ocr_pytesseract/swarmauri_ocr_pytesseract/__init__.py). The `swarmauri_ocr_pytesseract` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_ocr_pytesseract` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_ocr_pytesseract` package directory for the maintained example source checks (Python compilation and non-Python file presence). Behavioral tests may live in the repository’s shared suites; the new README syntax test is not presented as runtime coverage for local Tesseract OCR adapter for Swarmauri with sync, async, and batch image-to-text workflows.

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_ocr_pytesseract` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_ocr_pytesseract/swarmauri_ocr_pytesseract/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

> **What does this package do?**
> It wraps PyTesseract and the local Tesseract binary behind Swarmauri's OCR
> component interface.

> **Does it require a hosted API key?**
> No. It runs locally, but the host must have the `tesseract` executable and
> any required language packs installed.

> **What image inputs are supported?**
> File path strings, raw image bytes, and `PIL.Image.Image` instances.

> **Can it process multiple images concurrently?**
> Yes. Use `batch()` for synchronous lists and `abatch()` for async execution
> with a concurrency limit.

### Why

**Why select this package?** `swarmauri_ocr_pytesseract` provides local Tesseract OCR adapter for Swarmauri with sync, async, and batch image-to-text workflows; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_ocr_pytesseract`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_ocr_pytesseract/swarmauri_ocr_pytesseract/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_ocr_pytesseract` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

- [Tesseract OCR documentation](https://tesseract-ocr.github.io/)
- [PyTesseract on PyPI](https://pypi.org/project/pytesseract/)
- [Pillow documentation](https://pillow.readthedocs.io/)

### Related Packages

- [swarmauri_parser_fitzpdf](https://pypi.org/project/swarmauri_parser_fitzpdf/)
- [swarmauri_parser_pypdf2](https://pypi.org/project/swarmauri_parser_pypdf2/)
- [swarmauri_parser_pypdftk](https://pypi.org/project/swarmauri_parser_pypdftk/)
- [swarmauri_ocr_pytesseract](https://pypi.org/project/swarmauri_ocr_pytesseract/)

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_ocr_pytesseract](https://pypi.org/project/swarmauri_ocr_pytesseract/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_ocr_pytesseract`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/50-community/swarmauri_ocr_pytesseract` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

**Swarmauri Foundations**

- [swarmauri](https://pypi.org/project/swarmauri/)
- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_ocr_pytesseract` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_ocr_pytesseract/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_ocr_pytesseract` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_ocr_pytesseract` source version is `0.11.0.dev3`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_ocr_pytesseract/LICENSE).
<!-- readme-standards:end license -->

This project is licensed under the Apache-2.0 License.

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_ocr_pytesseract/NOTICE) for attribution.
<!-- readme-standards:end notices -->
