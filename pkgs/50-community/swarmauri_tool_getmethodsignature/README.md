# swarmauri_tool_getmethodsignature

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_tool_getmethodsignature</strong></p>
<p align="center">A tool that retrieves method signatures from Python source code.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_tool_getmethodsignature/"><img alt="pypi: swarmauri_tool_getmethodsignature" src="https://img.shields.io/pypi/v/swarmauri_tool_getmethodsignature"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_getmethodsignature/pyproject.toml"><img alt="Source version: 0.11.0.dev3" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev3&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_getmethodsignature/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_getmethodsignature/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_getmethodsignature/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_getmethodsignature/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_getmethodsignature/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_tool_getmethodsignature/"><img alt="Monthly PyPI downloads: swarmauri_tool_getmethodsignature" src="https://img.shields.io/pypi/dm/swarmauri_tool_getmethodsignature"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_getmethodsignature/README.md"><img alt="README hits: swarmauri_tool_getmethodsignature" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/50-community/swarmauri_tool_getmethodsignature/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_getmethodsignature/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_getmethodsignature/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_tool_getmethodsignature` is a Swarmauri tool that parses Python
source code with the standard-library `ast` module and returns the
signature of a specified function or method, including its name,
parameters, and return type. It is useful for documentation generation,
refactoring assistants, agent-driven code review, and static
introspection workflows.

### Why This Package

- Inspect function and method signatures without importing source code.
- Capture parameter names, annotations, and defaults in one call.
- Detect overloaded definitions that share a single function name.
- Distinguish synchronous functions from `async def` coroutines.
- Reuse the same tool in agents, notebooks, scripts, and backend
  workflows.

### When to Use

Choose `swarmauri_tool_getmethodsignature` when your integration needs a tool that retrieves method signatures from Python source code. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Swarmauri `ToolBase` implementation registered as
  `GetMethodSignatureTool`.
- Static `ast`-based parsing with no dynamic code execution.
- Support for positional-only, keyword-only, `*args`, and `**kwargs`
  parameters.
- Detection of overloaded functions sharing a single name.
- Renders a human-readable `signature` string for each definition.
- Supports Python 3.10, 3.11, 3.12, 3.13, and 3.14.

### Non-Goals

`swarmauri_tool_getmethodsignature` owns a tool that retrieves method signatures from Python source code. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_getmethodsignature/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. Read the example’s inputs and service requirements before execution.

### Installation

```bash
uv add swarmauri_tool_getmethodsignature
```

```bash
pip install swarmauri_tool_getmethodsignature
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_tool_getmethodsignature
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_tool_getmethodsignature
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_tool_getmethodsignature
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_getmethodsignature/docs/readme/quick_start.py).

```python
from swarmauri_tool_getmethodsignature import GetMethodSignatureTool

tool = GetMethodSignatureTool()
source = "def add(a: int, b: int = 0) -> int:\n    return a + b\n"
result = tool(source=source, method_name="add")

print(result["signature"])
# def add(a: int, b: int = 0) -> int
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_tool_getmethodsignature` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_getmethodsignature/docs/readme/usage.py).

```python
from swarmauri_tool_getmethodsignature import GetMethodSignatureTool

tool = GetMethodSignatureTool()
source = "def add(a: int, b: int = 0) -> int:\n    return a + b\n"
result = tool(source=source, method_name="add")

print(result["signature"])
# def add(a: int, b: int = 0) -> int
```
<!-- readme-standards:end example.usage -->

**Inspect an async method inside a class**

```python
from swarmauri_tool_getmethodsignature import GetMethodSignatureTool

tool = GetMethodSignatureTool()
source = (
    "class Service:\n"
    "    async def fetch(self, url: str) -> bytes:\n"
    "        ...\n"
)
result = tool(source=source, method_name="fetch")

print(result["is_async"])  # True
print(result["return_type"])  # bytes
```

**Detect overloaded definitions**

```python
from swarmauri_tool_getmethodsignature import GetMethodSignatureTool

tool = GetMethodSignatureTool()
source = (
    "def process(x: int) -> int:\n"
    "    return x\n"
    "def process(x: str) -> str:\n"
    "    return x\n"
)
result = tool(source=source, method_name="process")

print(len(result["overloads"]))  # 2
```

**Register the tool inside a Swarmauri tool registry**

```python
from swarmauri_standard.tools.ToolCollection import ToolCollection
from swarmauri_tool_getmethodsignature import GetMethodSignatureTool

tools = ToolCollection(tools=[GetMethodSignatureTool()])
print(tools)
```

### Configuration

Configure `swarmauri_tool_getmethodsignature` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_getmethodsignature/swarmauri_tool_getmethodsignature/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_getmethodsignature/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_tool_getmethodsignature` source does not establish a package-wide exception hierarchy. Preserve errors from its declared dependencies and validate inputs using the specific public contract in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_getmethodsignature/swarmauri_tool_getmethodsignature/__init__.py).

### Best Practices

- Pass complete, syntactically valid Python source for best results.
- Treat the `signature` string as a rendering hint rather than canonical
  source; round-trip formatting depends on the Python version.
- Use the `overloads` list when auditing code that relies on name reuse.
- Pair this tool with documentation generators to enrich API references.
- Avoid relying on dynamic imports; this tool performs static analysis
  only.

> **Note:** This tool performs static analysis on Python source code
> strings via the `ast` module. For runtime inspection of
> already-imported callables, see `MethodSignatureExtractor` in
> `swarmauri_standard.utils.method_signature_extractor_decorator`.

---

## Package Boundary

### What It Owns

`swarmauri_tool_getmethodsignature` is located in `community` and owns a tool that retrieves method signatures from Python source code. Source-declared APIs include `GetMethodSignatureTool`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_getmethodsignature/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_tool_getmethodsignature`.

Source-declared exports or types: `GetMethodSignatureTool`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_getmethodsignature/swarmauri_tool_getmethodsignature/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.tools` → `GetMethodSignatureTool` → `swarmauri_tool_getmethodsignature:GetMethodSignatureTool`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_tool_getmethodsignature` are `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_getmethodsignature/swarmauri_tool_getmethodsignature/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_tool_getmethodsignature` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_tool_getmethodsignature`, use the source-declared public interfaces (`GetMethodSignatureTool`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_tool_getmethodsignature` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_getmethodsignature/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_tool_getmethodsignature`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_getmethodsignature/swarmauri_tool_getmethodsignature/__init__.py). The `swarmauri_tool_getmethodsignature` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_tool_getmethodsignature` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_tool_getmethodsignature` package directory for the maintained example source checks (Python compilation and non-Python file presence). Behavioral tests may live in the repository’s shared suites; the new README syntax test is not presented as runtime coverage for a tool that retrieves method signatures from Python source code.

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_tool_getmethodsignature` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_getmethodsignature/swarmauri_tool_getmethodsignature/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

> **What does the tool return?**
> A dictionary with `name`, `parameters`, `return_type`, `signature`,
> and `is_async`. When multiple definitions share the requested name, it
> returns `{"overloads": [...]}` instead.

> **Does the tool execute the source code?**
> No. It uses `ast.parse` for purely static analysis and never imports
> or executes the supplied source.

> **What happens when the function is missing?**
> The tool returns `{"error": "..."}` describing the failure, including
> cases where the source cannot be parsed.

> **Are parameter defaults and annotations captured?**
> Yes. Each parameter entry includes `name`, `annotation` (when present),
> and `default` (when present), rendered back to source text via
> `ast.unparse`.

### Why

**Why select this package?** `swarmauri_tool_getmethodsignature` provides a tool that retrieves method signatures from Python source code; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_tool_getmethodsignature`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_getmethodsignature/swarmauri_tool_getmethodsignature/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_tool_getmethodsignature` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

- [Python ast module](https://docs.python.org/3/library/ast.html)
- [Swarmauri SDK repository](https://github.com/swarmauri/swarmauri-sdk)

### Related Packages

- [swarmauri_tool_searchword](https://pypi.org/project/swarmauri_tool_searchword/)
- [swarmauri_tool_textlength](https://pypi.org/project/swarmauri_tool_textlength/)
- [swarmauri_tool_sentencecomplexity](https://pypi.org/project/swarmauri_tool_sentencecomplexity/)
- [swarmauri_tool_lexicaldensity](https://pypi.org/project/swarmauri_tool_lexicaldensity/)
- [swarmauri_tool_smogindex](https://pypi.org/project/swarmauri_tool_smogindex/)

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_tool_getmethodsignature](https://pypi.org/project/swarmauri_tool_getmethodsignature/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_tool_getmethodsignature`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/50-community/swarmauri_tool_getmethodsignature` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

**Swarmauri Foundations**

- [swarmauri](https://pypi.org/project/swarmauri/)
- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_tool_getmethodsignature` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_getmethodsignature/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_tool_getmethodsignature` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_tool_getmethodsignature` source version is `0.11.0.dev3`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_getmethodsignature/LICENSE).
<!-- readme-standards:end license -->

This project is licensed under the Apache-2.0 License.

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_getmethodsignature/NOTICE) for attribution.
<!-- readme-standards:end notices -->
