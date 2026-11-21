# swarmauri_conversation_compacting

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_conversation_compacting</strong></p>
<p align="center">A Swarmauri conversation with rolling summaries and configurable compaction.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_conversation_compacting/"><img alt="pypi: swarmauri_conversation_compacting" src="https://img.shields.io/pypi/v/swarmauri_conversation_compacting"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_conversation_compacting/pyproject.toml"><img alt="Source version: 0.1.0.dev0" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.1.0.dev0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_conversation_compacting/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_conversation_compacting/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_conversation_compacting/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_conversation_compacting/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_conversation_compacting/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_conversation_compacting/"><img alt="Monthly PyPI downloads: swarmauri_conversation_compacting" src="https://img.shields.io/pypi/dm/swarmauri_conversation_compacting"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_conversation_compacting/README.md"><img alt="README hits: swarmauri_conversation_compacting" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/standards/swarmauri_conversation_compacting/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_conversation_compacting/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_conversation_compacting/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

[![Downloads](https://img.shields.io/pypi/dm/swarmauri_conversation_compacting)](https://pepy.tech/projects/swarmauri_conversation_compacting)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_conversation_compacting.svg)](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_conversation_compacting)
[![Python](https://img.shields.io/pypi/pyversions/swarmauri_conversation_compacting.svg)](https://pypi.org/project/swarmauri_conversation_compacting/)
[![License](https://img.shields.io/pypi/l/swarmauri_conversation_compacting)](LICENSE)
[![Release](https://img.shields.io/pypi/v/swarmauri_conversation_compacting?label=swarmauri_conversation_compacting&color=green)](https://pypi.org/project/swarmauri_conversation_compacting/)

Keep a rolling summary of older conversation turns while retaining recent messages for the next model request. Supports Python 3.10 through 3.14.

### Why This Package

`swarmauri_conversation_compacting` isolates this responsibility: A Swarmauri conversation with rolling summaries and configurable compaction. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_conversation_compacting/swarmauri_conversation_compacting/__init__.py) exposes `CompactingConversation`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_conversation_compacting` when your integration needs a Swarmauri conversation with rolling summaries and configurable compaction. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Plans compaction for complete user turns and preserves the newest configured turns.
- Keeps leading system and developer instructions verbatim and checks that tool results match their calls before selecting an older turn.
- Previews compacted context and refuses to apply a stale plan.

### Non-Goals

`swarmauri_conversation_compacting` owns a Swarmauri conversation with rolling summaries and configurable compaction. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_conversation_compacting/pyproject.toml) declares runtime dependencies including `swarmauri-base`, `swarmauri-standard`. Read the example’s inputs and service requirements before execution.

### Installation

```sh
uv add --prerelease allow swarmauri_conversation_compacting
pip install --pre swarmauri_conversation_compacting
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_conversation_compacting
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_conversation_compacting
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_conversation_compacting
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_conversation_compacting/docs/readme/quick_start.py).

```python
from swarmauri_conversation_compacting import CompactingConversation
from swarmauri_standard.messages.AgentMessage import AgentMessage
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = CompactingConversation(keep_recent_turns=1)
conversation.add_messages(
    [
        HumanMessage(content="Use Python 3.12 for this project."),
        AgentMessage(content="I'll target Python 3.12."),
        HumanMessage(content="What should the project metadata say?"),
    ]
)

plan = conversation.plan_compaction()
if plan is not None:
    # In an application, summarize plan.previous_summary and plan.older_messages.
    conversation.apply_compaction(plan, "The project targets Python 3.12.")
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_conversation_compacting` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_conversation_compacting/docs/readme/usage.py).

```python
from swarmauri_conversation_compacting import CompactingConversation
from swarmauri_standard.messages.AgentMessage import AgentMessage
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = CompactingConversation(keep_recent_turns=1)
conversation.add_messages(
    [
        HumanMessage(content="Use Python 3.12 for this project."),
        AgentMessage(content="I'll target Python 3.12."),
        HumanMessage(content="What should the project metadata say?"),
    ]
)

plan = conversation.plan_compaction()
if plan is not None:
    # In an application, summarize plan.previous_summary and plan.older_messages.
    conversation.apply_compaction(plan, "The project targets Python 3.12.")
```
<!-- readme-standards:end example.usage -->

The model-facing `history` includes the rolling summary. Applying a plan removes the summarized messages from `messages`. Archive the original messages separately if your application needs a complete transcript.

Agents using `AgentCompactionMixin` supply sync and async summarization methods. An adopting agent can set `trigger_tokens` on the conversation and call `compact_if_needed()` or `acompact_if_needed()` before dispatch. Supply a token counter for the request format and include any current instructions and tool definitions.

### Configuration

Configure `swarmauri_conversation_compacting` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_conversation_compacting/swarmauri_conversation_compacting/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_conversation_compacting/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_conversation_compacting` source does not establish a package-wide exception hierarchy. Preserve errors from its declared dependencies and validate inputs using the specific public contract in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_conversation_compacting/swarmauri_conversation_compacting/__init__.py).

### Best Practices

Use the explicit `swarmauri_conversation_compacting` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `CompactingConversation`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_conversation_compacting` is located in `standards` and owns a Swarmauri conversation with rolling summaries and configurable compaction. Source-declared APIs include `CompactingConversation`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_conversation_compacting/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_conversation_compacting`.

Source-declared exports or types: `CompactingConversation`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_conversation_compacting/swarmauri_conversation_compacting/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.conversations` → `CompactingConversation` → `swarmauri_conversation_compacting:CompactingConversation`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_conversation_compacting` are `swarmauri-base`, `swarmauri-standard`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_conversation_compacting/swarmauri_conversation_compacting/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_conversation_compacting` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_conversation_compacting`, use the source-declared public interfaces (`CompactingConversation`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_conversation_compacting` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_conversation_compacting/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_conversation_compacting`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_conversation_compacting/swarmauri_conversation_compacting/__init__.py). The `swarmauri_conversation_compacting` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_conversation_compacting` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_conversation_compacting` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_compaction.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_conversation_compacting/tests/test_compaction.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_conversation_compacting` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_conversation_compacting/swarmauri_conversation_compacting/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_conversation_compacting` provides a Swarmauri conversation with rolling summaries and configurable compaction; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_conversation_compacting`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_conversation_compacting/swarmauri_conversation_compacting/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_conversation_compacting` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_conversation_compacting/swarmauri_conversation_compacting/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_conversation_compacting/pyproject.toml) provide the supporting context for `swarmauri_conversation_compacting`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_standard](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/swarmauri_standard/README.md): First-party Swarmauri standard components for agents, tools, parsers, vectors, model adapters, and composable intelligence workflows.

### Project Links

<!-- readme-standards:begin project-links -->
- [Repository](https://github.com/swarmauri/swarmauri-sdk)
- [pypi: swarmauri_conversation_compacting](https://pypi.org/project/swarmauri_conversation_compacting/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_conversation_compacting`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/standards/swarmauri_conversation_compacting` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

Edit authored prose directly in this `swarmauri_conversation_compacting` README. Update source examples in `docs/readme/`, then run `readme-standards render --root . --write` from the package directory and review the diff. Required headings and generated blocks come from package-guide-v1.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_conversation_compacting` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_conversation_compacting/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_conversation_compacting` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_conversation_compacting` source version is `0.1.0.dev0`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_conversation_compacting/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_conversation_compacting/NOTICE) for attribution.
<!-- readme-standards:end notices -->
