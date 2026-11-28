# zdx

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>zdx</strong></p>
<p align="center">Z Doc Builder Experience by Swarmauri</p>
<p align="center">
<a href="https://pypi.org/project/zdx/"><img alt="pypi: zdx" src="https://img.shields.io/pypi/v/zdx?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/zdx/pyproject.toml"><img alt="Source version: 0.11.0" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/zdx/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/zdx/pyproject.toml"><img alt="Layer: plugins" src="https://img.shields.io/static/v1?label=Layer&amp;message=plugins&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/zdx/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/zdx/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/zdx/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/zdx/"><img alt="Monthly PyPI downloads: zdx" src="https://img.shields.io/pypi/dm/zdx?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/zdx/README.md"><img alt="README hits: zdx" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/60-plugins/zdx/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/zdx/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/zdx/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

Z Doc Builder Experience by Swarmauri. Reusable tooling to build and serve MkDocs-based documentation sites for Swarmauri projects.

### Why This Package

`zdx` isolates this responsibility: Z Doc Builder Experience by Swarmauri. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/zdx/zdx/__init__.py) exposes `FailureMode`, `WorkspaceSpec`, `Target`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `zdx` when your integration needs z Doc Builder Experience by Swarmauri. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Material for MkDocs configuration
- mkdocstrings support for API reference generation
- README harvesting across workspaces
- Dockerfile for containerized deployments

### Non-Goals

`zdx` owns z Doc Builder Experience by Swarmauri. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

1. Place your documentation sources in a dedicated directory (e.g., `docs/swarmauri-sdk`).
2. Customize `mkdocs.yml` and `api_manifest.yaml` for your project.
3. Install `zdx` and use the `zdx` CLI to build and preview the site.

### Installation

```bash
pip install zdx
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add zdx
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install zdx
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add zdx
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/zdx/docs/readme/quick_start.py).

```python
import importlib

package = importlib.import_module("zdx")
assert package.__name__ == "zdx"
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

This quick start is explicitly an import smoke check for `zdx`. It confirms that the documented namespace loads; it does not demonstrate or certify a complete application workflow. The detailed source and retained usage guidance below describe the integration boundary.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/zdx/docs/readme/usage.py).

```python
import importlib

package = importlib.import_module("zdx")
assert package.__name__ == "zdx"
```
<!-- readme-standards:end example.usage -->

### Configuration

The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/zdx/zdx/__init__.py) references configuration keys `VIRTUAL_ENV`, `ZDX_FAILURE_MODE`. Consult the constructor or function signature before supplying them; a referenced key is not necessarily a global environment variable.

### Error Handling

The inspected `zdx` source raises `argparse.ArgumentTypeError`, `subprocess.CalledProcessError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `zdx` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `FailureMode`, `WorkspaceSpec`, `Target`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`zdx` is located in `plugins` and owns z Doc Builder Experience by Swarmauri. Source-declared APIs include `FailureMode`, `WorkspaceSpec`, `Target`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/zdx/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `zdx`.

Source-declared exports or types: `FailureMode`, `WorkspaceSpec`, `Target`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/zdx/zdx/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `console_scripts` → `zdx` → `zdx.cli:main`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `zdx` are `mkdocs`, `mkdocs-gen-files`, `mkdocs-literate-nav`, `mkdocs-material`, `mkdocstrings`, `mkdocs-autorefs`, `griffe-typingdoc`, `pyyaml`, `ruff`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/zdx/zdx/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `zdx` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `zdx`, use the source-declared public interfaces (`FailureMode`, `WorkspaceSpec`, `Target`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `zdx` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/zdx/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `zdx`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/zdx/zdx/__init__.py). The `zdx` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `zdx` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `zdx` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_cli.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/zdx/tests/test_cli.py)
- [tests/test_gen_api.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/zdx/tests/test_gen_api.py)
- [tests/test_performance.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/zdx/tests/test_performance.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `zdx` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/zdx/zdx/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `zdx` provides z Doc Builder Experience by Swarmauri; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `zdx`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/zdx/zdx/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `zdx` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/zdx/zdx/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/zdx/pyproject.toml) provide the supporting context for `zdx`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

No direct local dependency was identified for `zdx` in this checkout. External dependency names are listed under Prerequisites; packages in the same directory layer are not automatically dependencies.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: zdx](https://pypi.org/project/zdx/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `zdx`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/60-plugins/zdx` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

**Generate from a manifest**

```bash
zdx generate --docs-dir /path/to/docs --manifest api_manifest.yaml
```

**Build READMEs into pages**

```bash
zdx readmes --docs-dir /path/to/docs
```

**Serve the site**

```bash
zdx serve --docs-dir /path/to/docs
```

**Generate and serve together**

```bash
zdx serve --generate --docs-dir /path/to/docs --manifest api_manifest.yaml
```

**Control failure handling**

Use the `--on-error` flag with any command that installs packages or generates
documentation to decide how strictly `zdx` reacts to subprocess failures:

```bash
zdx generate --on-error warn
```

Valid values are:

* `fail` ? stop immediately if a package installation or API build fails
* `warn` ? print a warning but keep going
* `ignore` ? suppress warnings and continue

You can also define the `ZDX_FAILURE_MODE` environment variable to set the
default for every invocation. For example, the provided Docker assets default to
`warn` so that optional packages do not abort a deployment.

**API Manifest**

`zdx` uses a YAML manifest to decide which Python packages to document and how
those pages are organized. Each project keeps its manifest alongside the docs
sources. This repository includes manifests for:

| Path | Purpose |
| --- | --- |
| `infra/docs/swarmauri-sdk/api_manifest.yaml` | Generates API docs for the SDK packages. |
| `infra/docs/peagen/api_manifest.yaml` | Drives documentation for the `peagen` tool. |
| `infra/docs/tigrbl/api_manifest.yaml` | Builds docs for the `tigrbl` project. |
| `pkgs/50-community/zdx/api_manifest.yaml` | Template manifest for new sites. |

**Manifest Schema**

An `api_manifest.yaml` file defines a list of **targets**. Each target produces
Markdown pages under `docs/api/<name>/` and a corresponding navigation entry in
the MkDocs configuration.

```yaml
targets:
  - name: Core
    package: swarmauri_core
    search_path: /pkgs/10-interfaces/swarmauri_core
    include:
      - swarmauri_core.*
    exclude:
      - "*.tests.*"
```

Every field controls a different part of the generation process:

| Field | Description |
| --- | --- |
| `name` | Label used for the top-level navigation item and the folder under `docs/api/`. |
| `search_path` | Directory containing the source package(s). The generator scans this path for modules. |
| `package` | Root import name when documenting a single package. Omit when using `discover`. |
| `discover` | When `true`, automatically finds all packages under `search_path` and builds docs for each. Generates separate folders and nav entries per package. |
| `include` | Glob patterns of fully qualified modules to include. Classes from matching modules get individual Markdown files. |
| `exclude` | Glob patterns of modules to skip. Use to drop tests or experimental code from the docs. |

For each module that survives the include/exclude filters, `zdx` writes a page
per public class. Pages land in
`docs/api/<name>/<module path>/<Class>.md` and a simple `index.md` is created if
one does not exist. The navigation section for the target is appended to
`mkdocs.yml`, ensuring the new pages appear in the rendered site.

---

## Governance

### Ownership and Decision Making

Changes to `zdx` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/zdx/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`zdx` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `zdx` source version is `0.11.0`.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/zdx/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/60-plugins/zdx/NOTICE) for attribution.
<!-- readme-standards:end notices -->
