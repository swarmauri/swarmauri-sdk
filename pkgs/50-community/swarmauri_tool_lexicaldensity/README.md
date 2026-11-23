# swarmauri_tool_lexicaldensity

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_tool_lexicaldensity</strong></p>
<p align="center">NLTK-powered Swarmauri NLP tool for measuring lexical density across prompts, documents, and corpora.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_tool_lexicaldensity/"><img alt="pypi: swarmauri_tool_lexicaldensity" src="https://img.shields.io/pypi/v/swarmauri_tool_lexicaldensity"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_lexicaldensity/pyproject.toml"><img alt="Source version: 0.11.0.dev1" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev1&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_lexicaldensity/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_lexicaldensity/pyproject.toml"><img alt="Layer: community" src="https://img.shields.io/static/v1?label=Layer&amp;message=community&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_lexicaldensity/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_lexicaldensity/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_lexicaldensity/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_tool_lexicaldensity/"><img alt="Monthly PyPI downloads: swarmauri_tool_lexicaldensity" src="https://img.shields.io/pypi/dm/swarmauri_tool_lexicaldensity"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_lexicaldensity/README.md"><img alt="README hits: swarmauri_tool_lexicaldensity" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/50-community/swarmauri_tool_lexicaldensity/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_lexicaldensity/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_lexicaldensity/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`swarmauri_tool_lexicaldensity` is a Swarmauri NLP tool for estimating lexical
density, the ratio of content words to total word count. It helps quantify how
information-dense a passage is, which makes it useful for readability reviews,
editorial QA, prompt analysis, educational tools, and agent-based writing
assistance.

### Why This Package

- Measure how content-heavy or function-word-heavy a text is.
- Compare drafts, prompts, or knowledge articles with a simple numeric signal.
- Feed lexical-density metrics into Swarmauri quality or moderation workflows.
- Pair lexical density with readability metrics for more complete text review.

### When to Use

Choose `swarmauri_tool_lexicaldensity` when your integration needs nLTK-powered Swarmauri NLP tool for measuring lexical density across prompts, documents, and corpora. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Swarmauri `ToolBase` implementation registered as `LexicalDensityTool`.
- Computes lexical density as a percentage value.
- Uses NLTK POS tagging to isolate content words.
- Useful for editorial, educational, prompt, and corpus-analysis workflows.
- Supports Python 3.10, 3.11, 3.12, 3.13, and 3.14.

### Non-Goals

`swarmauri_tool_lexicaldensity` owns nLTK-powered Swarmauri NLP tool for measuring lexical density across prompts, documents, and corpora. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_lexicaldensity/pyproject.toml) declares runtime dependencies including `textstat`, `nltk`, `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. Read the example’s inputs and service requirements before execution.

### Installation

```bash
uv add swarmauri_tool_lexicaldensity
```

```bash
pip install swarmauri_tool_lexicaldensity
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_tool_lexicaldensity
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_tool_lexicaldensity
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_tool_lexicaldensity
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_lexicaldensity/docs/readme/quick_start.py).

```python
from swarmauri_tool_lexicaldensity import LexicalDensityTool

tool = LexicalDensityTool()
result = tool(
    "This report summarizes quarterly revenue growth across segments."
)

print(result["lexical_density"])
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_tool_lexicaldensity` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_lexicaldensity/docs/readme/usage.py).

```python
from swarmauri_tool_lexicaldensity import LexicalDensityTool

tool = LexicalDensityTool()
result = tool(
    "This report summarizes quarterly revenue growth across segments."
)

print(result["lexical_density"])
```
<!-- readme-standards:end example.usage -->

**Compare lexical density across drafts**

```python
from swarmauri_tool_lexicaldensity import LexicalDensityTool

tool = LexicalDensityTool()

for label, text in {
    "draft": "We made a thing and it does stuff for users.",
    "final": "The platform automates retrieval, classification, and policy enforcement.",
}.items():
    print(label, tool(text))
```

**Score a prompt before sending it to an LLM**

```python
from swarmauri_tool_lexicaldensity import LexicalDensityTool

tool = LexicalDensityTool()
metrics = tool("Summarize operational risks, mitigation plans, and release dependencies.")

print(metrics)
```

**Register the tool in a Swarmauri collection**

```python
from swarmauri_standard.tools.ToolCollection import ToolCollection
from swarmauri_tool_lexicaldensity import LexicalDensityTool

tools = ToolCollection(tools=[LexicalDensityTool()])
print(tools)
```

### Configuration

Configure `swarmauri_tool_lexicaldensity` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_lexicaldensity/swarmauri_tool_lexicaldensity/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_lexicaldensity/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_tool_lexicaldensity` source does not establish a package-wide exception hierarchy. Preserve errors from its declared dependencies and validate inputs using the specific public contract in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_lexicaldensity/swarmauri_tool_lexicaldensity/__init__.py).

### Best Practices

- Pre-download NLTK models in offline or containerized deployments.
- Compare lexical-density values across similar content types, not unrelated
  genres.
- Use lexical density alongside readability scores rather than as a sole
  quality metric.
- Expect shorter texts to produce noisier percentages.

---

## Package Boundary

### What It Owns

`swarmauri_tool_lexicaldensity` is located in `community` and owns nLTK-powered Swarmauri NLP tool for measuring lexical density across prompts, documents, and corpora. Source-declared APIs include `LexicalDensityTool`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_lexicaldensity/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_tool_lexicaldensity`.

Source-declared exports or types: `LexicalDensityTool`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_lexicaldensity/swarmauri_tool_lexicaldensity/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.tools` → `LexicalDensityTool` → `swarmauri_tool_lexicaldensity.LexicalDensityTool:LexicalDensityTool`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_tool_lexicaldensity` are `textstat`, `nltk`, `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_lexicaldensity/swarmauri_tool_lexicaldensity/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_tool_lexicaldensity` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_tool_lexicaldensity`, use the source-declared public interfaces (`LexicalDensityTool`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_tool_lexicaldensity` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_lexicaldensity/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_tool_lexicaldensity`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_lexicaldensity/swarmauri_tool_lexicaldensity/__init__.py). The `swarmauri_tool_lexicaldensity` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_tool_lexicaldensity` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_tool_lexicaldensity` package directory for the maintained example source checks (Python compilation and non-Python file presence). Behavioral tests may live in the repository’s shared suites; the new README syntax test is not presented as runtime coverage for nLTK-powered Swarmauri NLP tool for measuring lexical density across prompts, documents, and corpora.

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_tool_lexicaldensity` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_lexicaldensity/swarmauri_tool_lexicaldensity/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

> **What does lexical density measure?**
> It estimates the percentage of content words such as nouns, verbs,
> adjectives, and adverbs relative to all words in the text.

> **What does the tool return?**
> A dictionary with one key: `lexical_density`.

> **Does it rely on NLTK models?**
> Yes. It uses NLTK tokenization and POS tagging resources.

> **Is it best suited for English text?**
> Yes. The current POS-tagging setup is English-oriented.

### Why

**Why select this package?** `swarmauri_tool_lexicaldensity` provides nLTK-powered Swarmauri NLP tool for measuring lexical density across prompts, documents, and corpora; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_tool_lexicaldensity`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_lexicaldensity/swarmauri_tool_lexicaldensity/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_tool_lexicaldensity` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

- [NLTK documentation](https://www.nltk.org/)
- [textstat documentation](https://github.com/textstat/textstat)
- [Swarmauri SDK repository](https://github.com/swarmauri/swarmauri-sdk)

### Related Packages

- [swarmauri_tool_textlength](https://pypi.org/project/swarmauri_tool_textlength/)
- [swarmauri_tool_sentencecomplexity](https://pypi.org/project/swarmauri_tool_sentencecomplexity/)
- [swarmauri_tool_smogindex](https://pypi.org/project/swarmauri_tool_smogindex/)
- [swarmauri_tool_dalechallreadability](https://pypi.org/project/swarmauri_tool_dalechallreadability/)

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_tool_lexicaldensity](https://pypi.org/project/swarmauri_tool_lexicaldensity/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_tool_lexicaldensity`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/50-community/swarmauri_tool_lexicaldensity` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

**Swarmauri Foundations**

- [swarmauri](https://pypi.org/project/swarmauri/)
- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_tool_lexicaldensity` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_lexicaldensity/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_tool_lexicaldensity` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_tool_lexicaldensity` source version is `0.11.0.dev1`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_lexicaldensity/LICENSE).
<!-- readme-standards:end license -->

This project is licensed under the Apache-2.0 License.

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/50-community/swarmauri_tool_lexicaldensity/NOTICE) for attribution.
<!-- readme-standards:end notices -->
