# swarmauri_prompt_j2prompttemplate

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_prompt_j2prompttemplate</strong></p>
<p align="center">Jinja2 Prompt Template for Swarmauri.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_prompt_j2prompttemplate/"><img alt="pypi: swarmauri_prompt_j2prompttemplate" src="https://img.shields.io/pypi/v/swarmauri_prompt_j2prompttemplate"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_prompt_j2prompttemplate/pyproject.toml"><img alt="Source version: 0.11.0.dev3" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev3&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_prompt_j2prompttemplate/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_prompt_j2prompttemplate/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_prompt_j2prompttemplate/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_prompt_j2prompttemplate/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_prompt_j2prompttemplate/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_prompt_j2prompttemplate/"><img alt="Monthly PyPI downloads: swarmauri_prompt_j2prompttemplate" src="https://img.shields.io/pypi/dm/swarmauri_prompt_j2prompttemplate"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_prompt_j2prompttemplate/README.md"><img alt="README hits: swarmauri_prompt_j2prompttemplate" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/40-standards/swarmauri_prompt_j2prompttemplate/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_prompt_j2prompttemplate/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_prompt_j2prompttemplate/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`J2PromptTemplate` is the Swarmauri Jinja2 prompt template implementation. It
accepts literal template strings or template files, renders them with the
variables you provide, and registers itself as the `J2PromptTemplate`
`swarmauri.prompts` entry point.

### Why This Package

`swarmauri_prompt_j2prompttemplate` isolates this responsibility: Jinja2 Prompt Template for Swarmauri. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_prompt_j2prompttemplate/swarmauri_prompt_j2prompttemplate/__init__.py) exposes `J2PromptTemplate`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_prompt_j2prompttemplate` when your integration needs jinja2 Prompt Template for Swarmauri. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Load template content from inline strings or filesystem paths.
- Configure one or more search directories via `templates_dir` for reusable
  Jinja2 templates with fallback lookup.
- Ship with helpful filters (`split`, `make_singular`, `make_plural`) for prompt
  engineering tasks.
- Render in an immutable Jinja sandbox by default so template source cannot
  traverse the Python object graph, invoke supplied callables, or mutate
  caller-provided containers.
- Call the instance directly (`template({...})`) or use `generate_prompt()` to
  render with the stored variables.

### Non-Goals

`swarmauri_prompt_j2prompttemplate` owns jinja2 Prompt Template for Swarmauri. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_prompt_j2prompttemplate/pyproject.toml) declares runtime dependencies including `inflect`, `jinja2`, `pydantic`, `swarmauri-core`, `swarmauri-base`. Read the example’s inputs and service requirements before execution.

### Installation

Choose the tool that matches your workflow:

```bash
# pip
pip install swarmauri_prompt_j2prompttemplate

# Poetry
poetry add swarmauri_prompt_j2prompttemplate

# uv
uv add swarmauri_prompt_j2prompttemplate
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_prompt_j2prompttemplate
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_prompt_j2prompttemplate
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_prompt_j2prompttemplate
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_prompt_j2prompttemplate/docs/readme/quick_start.py).

```python
from swarmauri_prompt_j2prompttemplate import J2PromptTemplate

template = J2PromptTemplate(template="Hello, {{ name }}!")
result = template({"name": "World"})
print(result)  # Hello, World!
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_prompt_j2prompttemplate` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_prompt_j2prompttemplate/docs/readme/usage.py).

```python
from swarmauri_prompt_j2prompttemplate import J2PromptTemplate

template = J2PromptTemplate(template="Hello, {{ name }}!")
result = template({"name": "World"})
print(result)  # Hello, World!
```
<!-- readme-standards:end example.usage -->

**Render a template string**


**Load templates from disk (with filters and search paths)**

```python
from pathlib import Path

from swarmauri_prompt_j2prompttemplate import J2PromptTemplate

templates_dir = Path("templates")
templates_dir.mkdir(parents=True, exist_ok=True)

template_path = templates_dir / "greeting.j2"
template_path.write_text("Hello, {{ animal|make_plural }}!", encoding="utf-8")

prompt = J2PromptTemplate(templates_dir=str(templates_dir))
prompt.set_template(template_path)

print(prompt({"animal": "fox"}))  # Hello, foxes!
```

`set_template()` loads the file with the configured environment. The template
file is located relative to the provided `templates_dir`. If the loader cannot
find it immediately, the class searches recursively before falling back to the
template's own directory.

**Template trust and sandboxing**

`J2PromptTemplate` uses a strict `ImmutableSandboxedEnvironment` by default.
Use this mode for template strings and files that may come from users,
registries, generated artifacts, or any source that is not fully controlled by
the application. Default-mode templates cannot call functions or methods,
including callables supplied as variables, and cannot invoke mutating methods
on list, dictionary, or set inputs. Variable interpolation and registered
filters remain available.

Applications that intentionally rely on unrestricted Jinja behavior can opt
in explicitly:

```python
trusted = J2PromptTemplate(
    template="{{ trusted_helper() }}",
    trusted_templates=True,
)
```

Trusted mode allows templates to access the same Python capabilities as a
normal Jinja `Environment`; never enable it for untrusted template source.
Precompiled templates not created by this strict environment are rejected in
the default mode because they cannot be retroactively restricted. The sandbox
limits Python object access and callable execution, but applications should
still apply time and resource limits when rendering adversarial templates.

### Configuration

Configure `swarmauri_prompt_j2prompttemplate` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_prompt_j2prompttemplate/swarmauri_prompt_j2prompttemplate/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_prompt_j2prompttemplate/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_prompt_j2prompttemplate` source raises `SecurityError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_prompt_j2prompttemplate` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `J2PromptTemplate`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_prompt_j2prompttemplate` is located in `standards` and owns jinja2 Prompt Template for Swarmauri. Source-declared APIs include `J2PromptTemplate`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_prompt_j2prompttemplate/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_prompt_j2prompttemplate`.

Source-declared exports or types: `J2PromptTemplate`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_prompt_j2prompttemplate/swarmauri_prompt_j2prompttemplate/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.prompts` → `J2PromptTemplate` → `swarmauri_prompt_j2prompttemplate:J2PromptTemplate`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_prompt_j2prompttemplate` are `inflect`, `jinja2`, `pydantic`, `swarmauri-core`, `swarmauri-base`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_prompt_j2prompttemplate/swarmauri_prompt_j2prompttemplate/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_prompt_j2prompttemplate` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_prompt_j2prompttemplate`, use the source-declared public interfaces (`J2PromptTemplate`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_prompt_j2prompttemplate` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_prompt_j2prompttemplate/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_prompt_j2prompttemplate`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_prompt_j2prompttemplate/swarmauri_prompt_j2prompttemplate/__init__.py). The `swarmauri_prompt_j2prompttemplate` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_prompt_j2prompttemplate` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_prompt_j2prompttemplate` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_readme_examples.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_prompt_j2prompttemplate/tests/test_readme_examples.py)
- [tests/unit/test_J2PromptTemplate.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_prompt_j2prompttemplate/tests/unit/test_J2PromptTemplate.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_prompt_j2prompttemplate` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_prompt_j2prompttemplate/swarmauri_prompt_j2prompttemplate/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_prompt_j2prompttemplate` provides jinja2 Prompt Template for Swarmauri; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_prompt_j2prompttemplate`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_prompt_j2prompttemplate/swarmauri_prompt_j2prompttemplate/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_prompt_j2prompttemplate` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_prompt_j2prompttemplate/swarmauri_prompt_j2prompttemplate/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_prompt_j2prompttemplate/pyproject.toml) provide the supporting context for `swarmauri_prompt_j2prompttemplate`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_prompt_j2prompttemplate](https://pypi.org/project/swarmauri_prompt_j2prompttemplate/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) that will help you get started.

### Development Setup

Work from the `pkgs/40-standards/swarmauri_prompt_j2prompttemplate` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_prompt_j2prompttemplate` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_prompt_j2prompttemplate` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_prompt_j2prompttemplate/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_prompt_j2prompttemplate` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_prompt_j2prompttemplate` source version is `0.11.0.dev3`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_prompt_j2prompttemplate/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_prompt_j2prompttemplate/NOTICE) for attribution.
<!-- readme-standards:end notices -->
