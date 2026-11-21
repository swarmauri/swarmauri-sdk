# swarmauri_evaluatorpool_accessibility

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_evaluatorpool_accessibility</strong></p>
<p align="center">A package providing accessibility and readability evaluators for SwarmAuri</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_evaluatorpool_accessibility/"><img alt="pypi: swarmauri_evaluatorpool_accessibility" src="https://img.shields.io/pypi/v/swarmauri_evaluatorpool_accessibility"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_evaluatorpool_accessibility/pyproject.toml"><img alt="Source version: 0.11.0.dev2" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev2&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_evaluatorpool_accessibility/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_evaluatorpool_accessibility/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_evaluatorpool_accessibility/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_evaluatorpool_accessibility/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_evaluatorpool_accessibility/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_evaluatorpool_accessibility/"><img alt="Monthly PyPI downloads: swarmauri_evaluatorpool_accessibility" src="https://img.shields.io/pypi/dm/swarmauri_evaluatorpool_accessibility"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_evaluatorpool_accessibility/README.md"><img alt="README hits: swarmauri_evaluatorpool_accessibility" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/standards/swarmauri_evaluatorpool_accessibility/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_evaluatorpool_accessibility/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_evaluatorpool_accessibility/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

Accessibility-focused evaluator pool for Swarmauri programs. The pool bundles a
set of classic readability metrics (Automated Readability Index, Coleman?Liau,
Flesch?Kincaid Grade, Flesch Reading Ease, and Gunning Fog) and normalises their
scores onto a single 0?1 scale where higher values mean easier-to-read content.

### Why This Package

`swarmauri_evaluatorpool_accessibility` isolates this responsibility: A package providing accessibility and readability evaluators for SwarmAuri. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_evaluatorpool_accessibility/swarmauri_evaluatorpool_accessibility/__init__.py) exposes `AccessibilityEvaluatorPool`, `AutomatedReadabilityIndexEvaluator`, `ColemanLiauIndexEvaluator`, `FleschKincaidGradeEvaluator`, `FleschReadingEaseEvaluator`, `GunningFogEvaluator`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_evaluatorpool_accessibility` when your integration needs a package providing accessibility and readability evaluators for SwarmAuri. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- `AccessibilityEvaluatorPool`: Pool that aggregates classic readability / accessibility metrics.
- `AutomatedReadabilityIndexEvaluator`: Computes the Automated Readability Index (ARI) for a Program’s textual
- `ColemanLiauIndexEvaluator`: Coleman–Liau Index evaluator compliant with the Program/Evaluator
- `FleschKincaidGradeEvaluator`: Evaluator that computes the Flesch-Kincaid Grade Level of text.
- `FleschReadingEaseEvaluator`: Evaluator that computes the Flesch Reading Ease score for text content.
- `GunningFogEvaluator`: Evaluator that computes the Gunning Fog Index (GFI) for text readability.

### Non-Goals

`swarmauri_evaluatorpool_accessibility` owns a package providing accessibility and readability evaluators for SwarmAuri. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_evaluatorpool_accessibility/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`, `nltk`, `beautifulsoup4`, `markdown`, `pydantic`. Read the example’s inputs and service requirements before execution.

### Installation

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_evaluatorpool_accessibility
```
<!-- readme-standards:end installation.uv -->

```bash
# Install into the current environment
uv pip install swarmauri_evaluatorpool_accessibility

# Or add it to the project pyproject.toml
uv add swarmauri_evaluatorpool_accessibility
```

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_evaluatorpool_accessibility
```
<!-- readme-standards:end installation.pip -->

```bash
pip install swarmauri_evaluatorpool_accessibility
```

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_evaluatorpool_accessibility
```
<!-- readme-standards:end installation.poetry -->

```bash
poetry add swarmauri_evaluatorpool_accessibility
```

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_evaluatorpool_accessibility/docs/readme/quick_start.py).

```python
from swarmauri_evaluatorpool_accessibility.AccessibilityEvaluatorPool import (
    AccessibilityEvaluatorPool,
)
from swarmauri_standard.programs.Program import Program

program = Program(
    content={"example.txt": "This is a simple sentence. Here is another one."}
)

pool = AccessibilityEvaluatorPool()
pool.initialize()  # spin up the thread pool once before evaluating

results = pool.evaluate([program])
result = results[0]

print(f"Aggregate accessibility score: {result.score:.2f}")
print("Per-evaluator scores:", result.metadata["evaluator_scores"])
flesch_meta = result.metadata["evaluator_metadata"].get(
    "FleschReadingEaseEvaluator", {}
)
print(
    "Flesch interpretation:",
    flesch_meta.get(
        "readability_interpretation", flesch_meta.get("error", "not available")
    ),
)

pool.shutdown()  # release resources when finished
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_evaluatorpool_accessibility` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_evaluatorpool_accessibility/docs/readme/usage.py).

```python
from swarmauri_evaluatorpool_accessibility.AccessibilityEvaluatorPool import (
    AccessibilityEvaluatorPool,
)
from swarmauri_standard.programs.Program import Program

program = Program(
    content={"example.txt": "This is a simple sentence. Here is another one."}
)

pool = AccessibilityEvaluatorPool()
pool.initialize()  # spin up the thread pool once before evaluating

results = pool.evaluate([program])
result = results[0]

print(f"Aggregate accessibility score: {result.score:.2f}")
print("Per-evaluator scores:", result.metadata["evaluator_scores"])
flesch_meta = result.metadata["evaluator_metadata"].get(
    "FleschReadingEaseEvaluator", {}
)
print(
    "Flesch interpretation:",
    flesch_meta.get(
        "readability_interpretation", flesch_meta.get("error", "not available")
    ),
)

pool.shutdown()  # release resources when finished
```
<!-- readme-standards:end example.usage -->

`AccessibilityEvaluatorPool` is a registered `EvaluatorPoolBase` component. It
expects a sequence of Swarmauri `Program` objects, runs the configured
evaluators concurrently, then returns standard `EvalResultBase` instances with
the aggregated score and detailed metadata for every evaluator.

**Result structure**

Each entry returned from `evaluate` is an `EvalResultBase` with:

- `score`: the weighted mean of the evaluator scores mapped to the 0?1 range.
- `metadata["evaluator_scores"]`: raw scores keyed by evaluator name.
- `metadata["evaluator_metadata"]`: evaluator-specific metadata (e.g. sentence
  counts, syllable estimates, interpretation strings).
- `metadata["aggregate_score"]`: mirrors `.score` for convenience.

You can customise the weighting of each evaluator by passing a `weights`
dictionary (name ? float) when constructing the pool.

### Configuration

The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_evaluatorpool_accessibility/swarmauri_evaluatorpool_accessibility/__init__.py) references configuration keys `NLTK_DATA_DIR`. Consult the constructor or function signature before supplying them; a referenced key is not necessarily a global environment variable.

### Error Handling

The inspected `swarmauri_evaluatorpool_accessibility` source raises `RuntimeError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_evaluatorpool_accessibility` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `AccessibilityEvaluatorPool`, `AutomatedReadabilityIndexEvaluator`, `ColemanLiauIndexEvaluator`, `FleschKincaidGradeEvaluator`, `FleschReadingEaseEvaluator`, `GunningFogEvaluator`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_evaluatorpool_accessibility` is located in `standards` and owns a package providing accessibility and readability evaluators for SwarmAuri. Source-declared APIs include `AccessibilityEvaluatorPool`, `AutomatedReadabilityIndexEvaluator`, `ColemanLiauIndexEvaluator`, `FleschKincaidGradeEvaluator`, `FleschReadingEaseEvaluator`, `GunningFogEvaluator`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_evaluatorpool_accessibility/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_evaluatorpool_accessibility`.

Source-declared exports or types: `AccessibilityEvaluatorPool`, `AutomatedReadabilityIndexEvaluator`, `ColemanLiauIndexEvaluator`, `FleschKincaidGradeEvaluator`, `FleschReadingEaseEvaluator`, `GunningFogEvaluator`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_evaluatorpool_accessibility/swarmauri_evaluatorpool_accessibility/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.evaluator_pools` → `AccessibilityEvaluatorPool` → `swarmauri_evaluatorpool_accessibility:AccessibilityEvaluatorPool`
- `swarmauri.evaluators` → `AutomatedReadabilityIndexEvaluator` → `swarmauri_evaluatorpool_accessibility:AutomatedReadabilityIndexEvaluator`
- `swarmauri.evaluators` → `ColemanLiauIndexEvaluator` → `swarmauri_evaluatorpool_accessibility:ColemanLiauIndexEvaluator`
- `swarmauri.evaluators` → `FleschKincaidGradeEvaluator` → `swarmauri_evaluatorpool_accessibility:FleschKincaidGradeEvaluator`
- `swarmauri.evaluators` → `FleschReadingEaseEvaluator` → `swarmauri_evaluatorpool_accessibility:FleschReadingEaseEvaluator`
- `swarmauri.evaluators` → `GunningFogEvaluator` → `swarmauri_evaluatorpool_accessibility:GunningFogEvaluator`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_evaluatorpool_accessibility` are `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`, `nltk`, `beautifulsoup4`, `markdown`, `pydantic`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_evaluatorpool_accessibility/swarmauri_evaluatorpool_accessibility/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_evaluatorpool_accessibility` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_evaluatorpool_accessibility`, use the source-declared public interfaces (`AccessibilityEvaluatorPool`, `AutomatedReadabilityIndexEvaluator`, `ColemanLiauIndexEvaluator`, `FleschKincaidGradeEvaluator`, `FleschReadingEaseEvaluator`, `GunningFogEvaluator`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_evaluatorpool_accessibility` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_evaluatorpool_accessibility/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_evaluatorpool_accessibility`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_evaluatorpool_accessibility/swarmauri_evaluatorpool_accessibility/__init__.py). The `swarmauri_evaluatorpool_accessibility` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_evaluatorpool_accessibility` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_evaluatorpool_accessibility` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/i9n/test_i9n__init__.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_evaluatorpool_accessibility/tests/i9n/test_i9n__init__.py)
- [tests/unit/test_AccessibilityEvaluatorPool.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_evaluatorpool_accessibility/tests/unit/test_AccessibilityEvaluatorPool.py)
- [tests/unit/test_AutomatedReadabilityIndexEvaluator.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_evaluatorpool_accessibility/tests/unit/test_AutomatedReadabilityIndexEvaluator.py)
- [tests/unit/test_ColemanLiauIndexEvaluator.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_evaluatorpool_accessibility/tests/unit/test_ColemanLiauIndexEvaluator.py)
- [tests/unit/test_FleschKincaidGradeEvaluator.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_evaluatorpool_accessibility/tests/unit/test_FleschKincaidGradeEvaluator.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_evaluatorpool_accessibility` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_evaluatorpool_accessibility/swarmauri_evaluatorpool_accessibility/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_evaluatorpool_accessibility` provides a package providing accessibility and readability evaluators for SwarmAuri; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_evaluatorpool_accessibility`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_evaluatorpool_accessibility/swarmauri_evaluatorpool_accessibility/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_evaluatorpool_accessibility` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_evaluatorpool_accessibility/swarmauri_evaluatorpool_accessibility/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_evaluatorpool_accessibility/pyproject.toml) provide the supporting context for `swarmauri_evaluatorpool_accessibility`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.
- [swarmauri_standard](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/swarmauri_standard/README.md): First-party Swarmauri standard components for agents, tools, parsers, vectors, model adapters, and composable intelligence workflows.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_evaluatorpool_accessibility](https://pypi.org/project/swarmauri_evaluatorpool_accessibility/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.

### Development Setup

Work from the `pkgs/standards/swarmauri_evaluatorpool_accessibility` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

- The pool automatically registers the bundled evaluators when no explicit list
  is provided. You can pass your own evaluators that satisfy the `IEvaluate`
  interface to override or extend the defaults.
- `FleschReadingEaseEvaluator` downloads NLTK's `punkt` tokenizer and
  `cmudict` pronunciation dictionary on first use. Set `NLTK_DATA_DIR` to point
  to a writable cache location if required. When these resources are not
  available the evaluator reports an `"error"` entry in its metadata instead of
  raising an exception.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_evaluatorpool_accessibility` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_evaluatorpool_accessibility/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_evaluatorpool_accessibility` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_evaluatorpool_accessibility` source version is `0.11.0.dev2`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_evaluatorpool_accessibility/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_evaluatorpool_accessibility/NOTICE) for attribution.
<!-- readme-standards:end notices -->
