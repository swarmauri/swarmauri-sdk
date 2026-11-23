# DistanceMetrics

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>DistanceMetrics</strong></p>
<p align="center">DistanceMetrics package with C++ extensions for calculating various distance metrics.</p>
<p align="center">
<a href="https://pypi.org/project/DistanceMetrics/"><img alt="pypi: DistanceMetrics unpublished" src="https://img.shields.io/static/v1?label=pypi&amp;message=DistanceMetrics%20unpublished&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/RapidSimilarity/DistanceMetrics/pyproject.toml"><img alt="Source version: 0.1.0" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.1.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/RapidSimilarity/DistanceMetrics/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/RapidSimilarity/DistanceMetrics/pyproject.toml"><img alt="Layer: experimental" src="https://img.shields.io/static/v1?label=Layer&amp;message=experimental&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/RapidSimilarity/DistanceMetrics/README.md#lifecycle-and-migration"><img alt="Lifecycle: experimental" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=experimental&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/RapidSimilarity/DistanceMetrics/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/RapidSimilarity/DistanceMetrics/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/DistanceMetrics/"><img alt="pypi downloads: DistanceMetrics: unpublished" src="https://img.shields.io/static/v1?label=pypi%20downloads&amp;message=DistanceMetrics%3A%20unpublished&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/RapidSimilarity/DistanceMetrics/README.md"><img alt="README hits: DistanceMetrics" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/70-experimental/RapidSimilarity/DistanceMetrics/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/RapidSimilarity/DistanceMetrics/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/RapidSimilarity/DistanceMetrics/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

The `DistanceMetrics` package provides core distance and similarity measures, including implementations of various distance functions such as Euclidean distance and cosine similarity to evaluate similarity between high-dimensional vectors.

### Why This Package

`DistanceMetrics` isolates this responsibility: DistanceMetrics package with C++ extensions for calculating various distance metrics. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/RapidSimilarity/DistanceMetrics/DistanceMetrics/__init__.py) exposes `cosine`, `euclidean`, `euclidean_distance`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `DistanceMetrics` when your integration needs distanceMetrics package with C++ extensions for calculating various distance metrics. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Public source surface: `cosine`, `euclidean`, `euclidean_distance`.
- Declared responsibility: DistanceMetrics package with C++ extensions for calculating various distance metrics.
- Versioned package metadata and maintained checkout examples.

### Non-Goals

`DistanceMetrics` owns distanceMetrics package with C++ extensions for calculating various distance metrics. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/RapidSimilarity/DistanceMetrics/pyproject.toml) declares runtime dependencies including `numpy`, `scipy`. Read the example’s inputs and service requirements before execution.

### Installation

To install the `DistanceMetrics` package, you will need to have Python 3.10 or later and the Meson build system installed. You can install the required dependencies using pip:

```bash
pip install numpy scipy meson ninja pybind11
```

Then, navigate to the root directory of the package and run the following commands:

```bash
meson setup builddir
meson compile -C builddir
meson install -C builddir
```

#### uv

<!-- readme-standards:begin installation.uv -->
`DistanceMetrics` is not declared published. From the source checkout:

```bash
uv pip install .
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
`DistanceMetrics` is not declared published. From the source checkout:

```bash
python -m pip install .
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
`DistanceMetrics` is not declared published. From a separate Poetry project, replace the path with your checkout:

```bash
poetry add /path/to/DistanceMetrics
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/RapidSimilarity/DistanceMetrics/docs/readme/quick_start.py).

```python
import numpy as np
from DistanceMetrics import euclidean_distance, cosine_similarity

# Example usage of Euclidean distance
vec1 = np.array([1.0, 2.0, 3.0])
vec2 = np.array([4.0, 5.0, 6.0])
distance = euclidean_distance(vec1, vec2)
print(f"Euclidean Distance: {distance}")

# Example usage of Cosine similarity
similarity = cosine_similarity(vec1, vec2)
print(f"Cosine Similarity: {similarity}")
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `DistanceMetrics` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/RapidSimilarity/DistanceMetrics/docs/readme/usage.py).

```python
import numpy as np
from DistanceMetrics import euclidean_distance, cosine_similarity

# Example usage of Euclidean distance
vec1 = np.array([1.0, 2.0, 3.0])
vec2 = np.array([4.0, 5.0, 6.0])
distance = euclidean_distance(vec1, vec2)
print(f"Euclidean Distance: {distance}")

# Example usage of Cosine similarity
similarity = cosine_similarity(vec1, vec2)
print(f"Cosine Similarity: {similarity}")
```
<!-- readme-standards:end example.usage -->

**Python Interface**

Once installed, you can use the `DistanceMetrics` package in your Python code as follows:


**C++ Implementation Example**

The package includes C++ extensions for the distance calculations. Below is an example of how to use the C++ functionalities directly:

**C++ Code Example**

```cpp
#include <iostream>
#include "DistanceMetrics/euclidean.h"
#include "DistanceMetrics/cosine.h"

int main() {
    std::vector<double> a = {1.0, 2.0, 3.0};
    std::vector<double> b = {4.0, 5.0, 6.0};

    double euclidean_dist = euclidean_distance(a, b);
    double cosine_sim = cosine_similarity(a, b);

    std::cout << "Euclidean Distance: " << euclidean_dist << std::endl;
    std::cout << "Cosine Similarity: " << cosine_sim << std::endl;

    return 0;
}
```

### Configuration

Configure `DistanceMetrics` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/RapidSimilarity/DistanceMetrics/DistanceMetrics/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/RapidSimilarity/DistanceMetrics/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `DistanceMetrics` source does not establish a package-wide exception hierarchy. Preserve errors from its declared dependencies and validate inputs using the specific public contract in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/RapidSimilarity/DistanceMetrics/DistanceMetrics/__init__.py).

### Best Practices

Use the explicit `DistanceMetrics` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `cosine`, `euclidean`, `euclidean_distance`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`DistanceMetrics` is located in `experimental` and owns distanceMetrics package with C++ extensions for calculating various distance metrics. Source-declared APIs include `cosine`, `euclidean`, `euclidean_distance`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/RapidSimilarity/DistanceMetrics/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `DistanceMetrics`.

Source-declared exports or types: `cosine`, `euclidean`, `euclidean_distance`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/RapidSimilarity/DistanceMetrics/DistanceMetrics/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
This package declares no command-line, GUI, or plugin entry points in its manifest.
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `DistanceMetrics` are `numpy`, `scipy`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/RapidSimilarity/DistanceMetrics/DistanceMetrics/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `DistanceMetrics` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `DistanceMetrics`, use the source-declared public interfaces (`cosine`, `euclidean`, `euclidean_distance`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `DistanceMetrics` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/RapidSimilarity/DistanceMetrics/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `DistanceMetrics`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/RapidSimilarity/DistanceMetrics/DistanceMetrics/__init__.py). The `DistanceMetrics` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `DistanceMetrics` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

The package includes tests that can be run using pytest. To execute the tests, navigate to the root directory of the package and run:

```bash
pytest
```

This will ensure that all functionalities are working as expected.

### Certification Status

No external certification is asserted for `DistanceMetrics` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/RapidSimilarity/DistanceMetrics/DistanceMetrics/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `DistanceMetrics` provides distanceMetrics package with C++ extensions for calculating various distance metrics; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `DistanceMetrics`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/RapidSimilarity/DistanceMetrics/DistanceMetrics/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `DistanceMetrics` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/RapidSimilarity/DistanceMetrics/DistanceMetrics/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/RapidSimilarity/DistanceMetrics/pyproject.toml) provide the supporting context for `DistanceMetrics`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

No direct local dependency was identified for `DistanceMetrics` in this checkout. External dependency names are listed under Prerequisites; packages in the same directory layer are not automatically dependencies.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: DistanceMetrics](https://pypi.org/project/DistanceMetrics/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `DistanceMetrics`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/70-experimental/RapidSimilarity/DistanceMetrics` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

**Authors**

- Michael Nwogha

**Dependencies**

The `DistanceMetrics` package relies on the following Python packages:
- `numpy`
- `scipy`
- `meson-python`
- `ninja`
- `pybind11`

Make sure to install these dependencies before building the package.

---

## Governance

### Ownership and Decision Making

Changes to `DistanceMetrics` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/RapidSimilarity/DistanceMetrics/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`DistanceMetrics` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `DistanceMetrics` source version is `0.1.0`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/RapidSimilarity/DistanceMetrics/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/70-experimental/RapidSimilarity/DistanceMetrics/NOTICE) for attribution.
<!-- readme-standards:end notices -->
