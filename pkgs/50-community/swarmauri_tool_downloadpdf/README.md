# swarmauri_tool_downloadpdf

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_tool_downloadpdf</strong></p>
<p align="center">Swarmauri document-ingestion tool for downloading PDFs and returning base64-encoded content.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_tool_downloadpdf/"><img alt="pypi: swarmauri_tool_downloadpdf" src="https://img.shields.io/pypi/v/swarmauri_tool_downloadpdf"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_downloadpdf/pyproject.toml"><img alt="Source version: 0.11.0.dev3" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev3&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_downloadpdf/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_downloadpdf/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_downloadpdf/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_downloadpdf/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_downloadpdf/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_tool_downloadpdf/"><img alt="Monthly PyPI downloads: swarmauri_tool_downloadpdf" src="https://img.shields.io/pypi/dm/swarmauri_tool_downloadpdf"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_downloadpdf/README.md"><img alt="README hits: swarmauri_tool_downloadpdf" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/50-community/swarmauri_tool_downloadpdf/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_downloadpdf/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_downloadpdf/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_tool_downloadpdf` is a Swarmauri document-ingestion tool for
fetching a PDF from a URL and returning its contents as a base64-encoded
string. It is useful for agent workflows, document capture, API handoffs, and
pipelines that need PDF content in memory without writing directly to disk.

### Why This Package

- Retrieve PDFs from remote URLs inside Swarmauri workflows.
- Keep document transfer in-memory with base64 output.
- Hand off downloaded PDF content to parsers, storage layers, or APIs.
- Surface structured success or error responses from HTTP downloads.

### When to Use

Choose `swarmauri_tool_downloadpdf` when your integration needs swarmauri document-ingestion tool for downloading PDFs and returning base64-encoded content. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Swarmauri `ToolBase` implementation registered as `DownloadPDFTool`.
- Fetches PDF bytes with `httpx`.
- Returns PDF content as base64 for easy transport.
- Avoids filesystem writes in the default flow.
- Supports Python 3.10, 3.11, 3.12, 3.13, and 3.14.

### Non-Goals

`swarmauri_tool_downloadpdf` owns swarmauri document-ingestion tool for downloading PDFs and returning base64-encoded content. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_downloadpdf/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. Read the example’s inputs and service requirements before execution.

### Installation

```bash
uv add swarmauri_tool_downloadpdf
```

```bash
pip install swarmauri_tool_downloadpdf
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_tool_downloadpdf
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_tool_downloadpdf
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_tool_downloadpdf
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_downloadpdf/docs/readme/quick_start.py).

```python
from swarmauri_tool_downloadpdf import DownloadPDFTool

tool = DownloadPDFTool()
result = tool(
    "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
)

print(result.keys())
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_tool_downloadpdf` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_downloadpdf/docs/readme/usage.py).

```python
from swarmauri_tool_downloadpdf import DownloadPDFTool

tool = DownloadPDFTool()
result = tool(
    "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
)

print(result.keys())
```
<!-- readme-standards:end example.usage -->

**Decode the returned PDF payload**

```python
import base64
from swarmauri_tool_downloadpdf import DownloadPDFTool

tool = DownloadPDFTool()
result = tool("https://example.com/report.pdf")

if "content" in result:
    pdf_bytes = base64.b64decode(result["content"])
    print(len(pdf_bytes))
```

**Send PDF content to another API**

```python
import httpx
from swarmauri_tool_downloadpdf import DownloadPDFTool

tool = DownloadPDFTool()
result = tool("https://example.com/form.pdf")

if "content" in result:
    httpx.post("https://api.example.com/upload", json=result)
```

**Use the tool in a Swarmauri collection**

```python
from swarmauri_standard.tools.ToolCollection import ToolCollection
from swarmauri_tool_downloadpdf import DownloadPDFTool

tools = ToolCollection(tools=[DownloadPDFTool()])
print(tools)
```

### Configuration

Configure `swarmauri_tool_downloadpdf` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_downloadpdf/swarmauri_tool_downloadpdf/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_downloadpdf/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_tool_downloadpdf` source does not establish a package-wide exception hierarchy. Preserve errors from its declared dependencies and validate inputs using the specific public contract in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_downloadpdf/swarmauri_tool_downloadpdf/__init__.py).

### Best Practices

- Validate and sanitize URLs before downloading untrusted documents.
- Guard against large PDFs if memory pressure matters in your runtime.
- Check for `error` before decoding returned content.
- Hand base64 output directly to downstream services when possible to avoid
  unnecessary temporary files.

---

## Package Boundary

### What It Owns

`swarmauri_tool_downloadpdf` is located in `community` and owns swarmauri document-ingestion tool for downloading PDFs and returning base64-encoded content. Source-declared APIs include `DownloadPDFTool`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_downloadpdf/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_tool_downloadpdf`.

Source-declared exports or types: `DownloadPDFTool`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_downloadpdf/swarmauri_tool_downloadpdf/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.tools` → `DownloadPdfTool` → `swarmauri_tool_downloadpdf.DownloadPdfTool:DownloadPdfTool`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_tool_downloadpdf` are `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_downloadpdf/swarmauri_tool_downloadpdf/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_tool_downloadpdf` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_tool_downloadpdf`, use the source-declared public interfaces (`DownloadPDFTool`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_tool_downloadpdf` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_downloadpdf/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_tool_downloadpdf`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_downloadpdf/swarmauri_tool_downloadpdf/__init__.py). The `swarmauri_tool_downloadpdf` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_tool_downloadpdf` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_tool_downloadpdf` package directory for the maintained example source checks (Python compilation and non-Python file presence). Behavioral tests may live in the repository’s shared suites; the new README syntax test is not presented as runtime coverage for swarmauri document-ingestion tool for downloading PDFs and returning base64-encoded content.

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_tool_downloadpdf` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_downloadpdf/swarmauri_tool_downloadpdf/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

> **What does the tool return on success?**
> A dictionary with `message` and base64-encoded `content`.

> **Does it save files to disk?**
> No. It downloads bytes into memory and returns them encoded as base64.

> **What input does it expect?**
> The callable runtime surface currently expects a single `url` string.

> **How are download failures reported?**
> The tool returns an `error` key with a descriptive message.

### Why

**Why select this package?** `swarmauri_tool_downloadpdf` provides swarmauri document-ingestion tool for downloading PDFs and returning base64-encoded content; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_tool_downloadpdf`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_downloadpdf/swarmauri_tool_downloadpdf/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_tool_downloadpdf` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

- [HTTPX documentation](https://www.python-httpx.org/)
- [Base64 encoding in Python](https://docs.python.org/3/library/base64.html)
- [Swarmauri SDK repository](https://github.com/swarmauri/swarmauri-sdk)

### Related Packages

- [swarmauri_parser_pypdf2](https://pypi.org/project/swarmauri_parser_pypdf2/)
- [swarmauri_parser_fitzpdf](https://pypi.org/project/swarmauri_parser_fitzpdf/)
- [swarmauri_parser_pypdftk](https://pypi.org/project/swarmauri_parser_pypdftk/)
- [swarmauri_tool_webscraping](https://pypi.org/project/swarmauri_tool_webscraping/)

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_tool_downloadpdf](https://pypi.org/project/swarmauri_tool_downloadpdf/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_tool_downloadpdf`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/50-community/swarmauri_tool_downloadpdf` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

**Swarmauri Foundations**

- [swarmauri](https://pypi.org/project/swarmauri/)
- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_tool_downloadpdf` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_downloadpdf/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_tool_downloadpdf` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_tool_downloadpdf` source version is `0.11.0.dev3`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_downloadpdf/LICENSE).
<!-- readme-standards:end license -->

This project is licensed under the Apache-2.0 License.

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_downloadpdf/NOTICE) for attribution.
<!-- readme-standards:end notices -->
