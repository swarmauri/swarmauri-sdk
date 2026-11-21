# swarmauri_metric_hamming

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_metric_hamming</strong></p>
<p align="center">Hamming-distance metric for Swarmauri with raw mismatch counts, batched comparisons, and metric-axiom helpers.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_metric_hamming/"><img alt="pypi: swarmauri_metric_hamming" src="https://img.shields.io/pypi/v/swarmauri_metric_hamming"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_metric_hamming/pyproject.toml"><img alt="Source version: 0.11.0.dev3" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev3&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_metric_hamming/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_metric_hamming/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_metric_hamming/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_metric_hamming/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_metric_hamming/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_metric_hamming/"><img alt="Monthly PyPI downloads: swarmauri_metric_hamming" src="https://img.shields.io/pypi/dm/swarmauri_metric_hamming"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_metric_hamming/README.md"><img alt="README hits: swarmauri_metric_hamming" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/community/swarmauri_metric_hamming/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_metric_hamming/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_metric_hamming/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_metric_hamming` is the Swarmauri metric implementation for Hamming
distance. It compares equal-length sequences and returns the count of positions
that differ, while also exposing batched distance helpers and metric-axiom
checks for downstream validation workflows.

### Why This Package

- Measure discrete sequence differences inside Swarmauri retrieval, coding,
  validation, or comparison workflows.
- Compare binary vectors, strings, NumPy arrays, and Swarmauri vector or matrix
  surfaces through one metric component.
- Reuse a metric implementation that also exposes symmetry, identity, and
  triangle-inequality checks.
- Build exact distance-based workflows for error-correcting codes, bitstring
  analysis, and symbolic comparison.

### When to Use

Choose `swarmauri_metric_hamming` when your integration needs hamming-distance metric for Swarmauri with raw mismatch counts, batched comparisons, and metric-axiom helpers. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Raw Hamming distance for equal-length sequences.
- Pairwise `distances()` support for collections of vectors.
- Input normalization for strings, bytes, dicts, arrays, matrices, and
  vectors.
- Metric-axiom helpers: non-negativity, symmetry, identity of indiscernibles,
  and triangle inequality.
- Supports Python 3.10, 3.11, 3.12, 3.13, and 3.14.

### Non-Goals

`swarmauri_metric_hamming` owns hamming-distance metric for Swarmauri with raw mismatch counts, batched comparisons, and metric-axiom helpers. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_metric_hamming/pyproject.toml) declares runtime dependencies including `numpy`, `swarmauri-core`, `swarmauri-base`. Read the example’s inputs and service requirements before execution.

### Installation

```bash
uv add swarmauri_metric_hamming
```

```bash
pip install swarmauri_metric_hamming
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_metric_hamming
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_metric_hamming
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_metric_hamming
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_metric_hamming/docs/readme/quick_start.py).

```python
from swarmauri_metric_hamming import HammingMetric

metric = HammingMetric()
codeword = [1, 0, 1, 1, 0, 0, 1]
received = [1, 1, 1, 1, 0, 0, 1]

print(metric.distance(codeword, received))
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_metric_hamming` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_metric_hamming/docs/readme/usage.py).

```python
from swarmauri_metric_hamming import HammingMetric

metric = HammingMetric()
codeword = [1, 0, 1, 1, 0, 0, 1]
received = [1, 1, 1, 1, 0, 0, 1]

print(metric.distance(codeword, received))
```
<!-- readme-standards:end example.usage -->

**Compare binary vectors**

```python
from swarmauri_metric_hamming import HammingMetric

metric = HammingMetric()
print(metric.distance([1, 0, 1, 1], [1, 1, 0, 1]))
```

**Compare strings and arrays**

```python
import numpy as np
from swarmauri_metric_hamming import HammingMetric

metric = HammingMetric()
left = "1011001"
right = np.array([1, 0, 1, 0, 0, 0, 1])

print(metric.distance(left, right))
```

**Compute pairwise distances across collections**

```python
from swarmauri_metric_hamming import HammingMetric

metric = HammingMetric()
left = [[0, 0, 0], [1, 1, 1]]
right = [[0, 0, 1], [1, 0, 1]]

print(metric.distances(left, right))
```

**Verify metric axioms**

```python
from swarmauri_metric_hamming import HammingMetric

metric = HammingMetric()
x = [0, 1, 0, 1]
y = [0, 0, 1, 1]
z = [1, 0, 1, 0]

assert metric.check_non_negativity(x, y)
assert metric.check_symmetry(x, y)
assert metric.check_triangle_inequality(x, y, z)
```

### Configuration

Configure `swarmauri_metric_hamming` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_metric_hamming/swarmauri_metric_hamming/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_metric_hamming/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_metric_hamming` source raises `TypeError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

- Validate equal-length inputs before calling `distance()` in external
  pipelines.
- Use raw Hamming counts when exact mismatch positions matter more than a
  normalized ratio.
- Normalize heterogeneous input types consistently before comparing large
  collections.
- Pair this metric with domain-specific encoders when comparing symbolic or
  categorical data.

---

## Package Boundary

### What It Owns

`swarmauri_metric_hamming` is located in `community` and owns hamming-distance metric for Swarmauri with raw mismatch counts, batched comparisons, and metric-axiom helpers. Source-declared APIs include `HammingMetric`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_metric_hamming/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_metric_hamming`.

Source-declared exports or types: `HammingMetric`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_metric_hamming/swarmauri_metric_hamming/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.metrics` → `HammingMetric` → `swarmauri_metric_hamming.HammingMetric:HammingMetric`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_metric_hamming` are `numpy`, `swarmauri-core`, `swarmauri-base`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_metric_hamming/swarmauri_metric_hamming/__init__.py).

### Protocol Consumers

Direct consumers in this checkout’s package manifests include `swarmauri_matrix_hamming74`. These edges describe declared dependencies, not protocol-conformance evidence.

### Extensions

For `swarmauri_metric_hamming`, use the source-declared public interfaces (`HammingMetric`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_metric_hamming` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_metric_hamming/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_metric_hamming`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_metric_hamming/swarmauri_metric_hamming/__init__.py). The `swarmauri_metric_hamming` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_metric_hamming` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_metric_hamming` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_hamming_metric.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_metric_hamming/tests/test_hamming_metric.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_metric_hamming` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_metric_hamming/swarmauri_metric_hamming/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

> **What does `distance()` return?**
> A float equal to the number of differing positions between two equal-length
> inputs.

> **What input types are supported?**
> Strings, bytes, dictionaries, NumPy arrays, generic sequences, and
> Swarmauri matrix/vector interfaces.

> **Does it normalize the distance?**
> No. The current implementation returns the raw count of mismatched positions.

> **Can it compare batches of vectors?**
> Yes. Use `distances()` to generate pairwise distance rows across collections.

### Why

**Why select this package?** `swarmauri_metric_hamming` provides hamming-distance metric for Swarmauri with raw mismatch counts, batched comparisons, and metric-axiom helpers; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_metric_hamming`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_metric_hamming/swarmauri_metric_hamming/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_metric_hamming` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

- [Hamming distance overview](https://en.wikipedia.org/wiki/Hamming_distance)
- [NumPy documentation](https://numpy.org/doc/)

### Related Packages

- [swarmauri_measurement_mutualinformation](https://pypi.org/project/swarmauri_measurement_mutualinformation/)
- [swarmauri_measurement_tokencountestimator](https://pypi.org/project/swarmauri_measurement_tokencountestimator/)
- [swarmauri_metric_hamming](https://pypi.org/project/swarmauri_metric_hamming/)

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_metric_hamming](https://pypi.org/project/swarmauri_metric_hamming/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_metric_hamming`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/community/swarmauri_metric_hamming` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

**Swarmauri Foundations**

- [swarmauri](https://pypi.org/project/swarmauri/)
- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_metric_hamming` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_metric_hamming/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_metric_hamming` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_metric_hamming` source version is `0.11.0.dev3`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_metric_hamming/LICENSE).
<!-- readme-standards:end license -->

This project is licensed under the Apache-2.0 License.

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/community/swarmauri_metric_hamming/NOTICE) for attribution.
<!-- readme-standards:end notices -->
