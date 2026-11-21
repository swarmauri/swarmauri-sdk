# swarmauri_agent_runner

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_agent_runner</strong></p>
<p align="center">Run model tool calls and resume checkpointed human interactions.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_agent_runner/"><img alt="pypi: swarmauri_agent_runner" src="https://img.shields.io/pypi/v/swarmauri_agent_runner"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_agent_runner/pyproject.toml"><img alt="Source version: 0.1.2" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.1.2&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_agent_runner/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_agent_runner/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_agent_runner/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_agent_runner/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_agent_runner/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_agent_runner/"><img alt="Monthly PyPI downloads: swarmauri_agent_runner" src="https://img.shields.io/pypi/dm/swarmauri_agent_runner"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_agent_runner/README.md"><img alt="README hits: swarmauri_agent_runner" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/standards/swarmauri_agent_runner/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_agent_runner/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_agent_runner/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

[![Downloads](https://img.shields.io/pypi/dm/swarmauri_agent_runner)](https://pepy.tech/projects/swarmauri_agent_runner)
[![Hits](https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_agent_runner.svg)](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_agent_runner)
[![Python](https://img.shields.io/pypi/pyversions/swarmauri_agent_runner)](https://pypi.org/project/swarmauri_agent_runner/)
[![License](https://img.shields.io/pypi/l/swarmauri_agent_runner)](LICENSE)
[![Release](https://img.shields.io/pypi/v/swarmauri_agent_runner?label=swarmauri_agent_runner&color=green)](https://pypi.org/project/swarmauri_agent_runner/)

Run model tool calls and resume checkpointed human interactions.

### Why This Package

`swarmauri_agent_runner` isolates this responsibility: Run model tool calls and resume checkpointed human interactions. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_agent_runner/swarmauri_agent_runner/AgentRunnerExecutionDriver.py) exposes `AgentRunner`, `AgentRunnerExecutionDriver`, `ApprovalDecision`, `ApprovalRequest`, `RunConflictError`, `RunEvent`, `RunState`, `SqliteRunStore`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_agent_runner` when your integration needs run model tool calls and resume checkpointed human interactions. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Run model tool calls and resume checkpointed human interactions.
- Supports Python 3.10 through 3.14.

### Non-Goals

`swarmauri_agent_runner` owns run model tool calls and resume checkpointed human interactions. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_agent_runner/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`, `swarmauri-tool-askuser`. Read the example’s inputs and service requirements before execution.

### Installation

```sh
uv add swarmauri_agent_runner
pip install swarmauri_agent_runner
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_agent_runner
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_agent_runner
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_agent_runner
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_agent_runner/docs/readme/quick_start.py).

```python
from swarmauri_agent_runner import AgentRunner
from swarmauri_runstore_sqlite import SqliteRunStore
from swarmauri_standard.tool_llms.OpenAIToolModel import OpenAIToolModel

model = OpenAIToolModel(api_key="your-api-key")
runner = AgentRunner(model, SqliteRunStore(path="runs.db"))
state = runner.start("Ask me which package to inspect.")
if state.status == "input_required":
    from swarmauri_standard.messages.AnswerMessage import AnswerMessage

    question = state.event().question
    reply = AnswerMessage(
        question_id=question.question_id, answer=input(question.content)
    )
    state = runner.resume(state.run_id, reply)
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_agent_runner` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_agent_runner/docs/readme/usage.py).

```python
from swarmauri_agent_runner import AgentRunner
from swarmauri_runstore_sqlite import SqliteRunStore
from swarmauri_standard.tool_llms.OpenAIToolModel import OpenAIToolModel

model = OpenAIToolModel(api_key="your-api-key")
runner = AgentRunner(model, SqliteRunStore(path="runs.db"))
state = runner.start("Ask me which package to inspect.")
if state.status == "input_required":
    from swarmauri_standard.messages.AnswerMessage import AnswerMessage

    question = state.event().question
    reply = AnswerMessage(
        question_id=question.question_id, answer=input(question.content)
    )
    state = runner.resume(state.run_id, reply)
```
<!-- readme-standards:end example.usage -->

Reopen the same SQLite database and configure the same model and tools to
resume a pending question or approval in another process. The application
authenticates the caller before exposing a run or accepting a decision.
Set a stable approval scope that identifies the workspace and permissions.
A run interrupted during tool dispatch records that state for reconciliation.
Runtime tool instances and open process handles live in the application process.

### Configuration

Configure `swarmauri_agent_runner` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_agent_runner/swarmauri_agent_runner/AgentRunnerExecutionDriver.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_agent_runner/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_agent_runner` source raises `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_agent_runner` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `AgentRunner`, `AgentRunnerExecutionDriver`, `ApprovalDecision`, `ApprovalRequest`, `RunConflictError`, `RunEvent`, `RunState`, `SqliteRunStore`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_agent_runner` is located in `standards` and owns run model tool calls and resume checkpointed human interactions. Source-declared APIs include `AgentRunner`, `AgentRunnerExecutionDriver`, `ApprovalDecision`, `ApprovalRequest`, `RunConflictError`, `RunEvent`, `RunState`, `SqliteRunStore`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_agent_runner/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_agent_runner`.

Source-declared exports or types: `AgentRunner`, `AgentRunnerExecutionDriver`, `ApprovalDecision`, `ApprovalRequest`, `RunConflictError`, `RunEvent`, `RunState`, `SqliteRunStore`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_agent_runner/swarmauri_agent_runner/AgentRunnerExecutionDriver.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.execution_drivers` → `AgentRunnerExecutionDriver` → `swarmauri_agent_runner:AgentRunnerExecutionDriver`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_agent_runner` are `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`, `swarmauri-tool-askuser`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_agent_runner/swarmauri_agent_runner/AgentRunnerExecutionDriver.py).

### Protocol Consumers

Direct consumers in this checkout’s package manifests include `swarmauri-demo-package-maintenance`, `swarmauri_agent_package_maintenance`, `swarmauri_workflow_documentassistant`. These edges describe declared dependencies, not protocol-conformance evidence.

### Extensions

For `swarmauri_agent_runner`, use the source-declared public interfaces (`AgentRunner`, `AgentRunnerExecutionDriver`, `ApprovalDecision`, `ApprovalRequest`, `RunConflictError`, `RunEvent`, `RunState`, `SqliteRunStore`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_agent_runner` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_agent_runner/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_agent_runner`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_agent_runner/swarmauri_agent_runner/AgentRunnerExecutionDriver.py). The `swarmauri_agent_runner` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_agent_runner` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_agent_runner` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/unit/test_approval.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_agent_runner/tests/unit/test_approval.py)
- [tests/unit/test_checkpoint_compatibility.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_agent_runner/tests/unit/test_checkpoint_compatibility.py)
- [tests/unit/test_execution_driver.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_agent_runner/tests/unit/test_execution_driver.py)
- [tests/unit/test_restart.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_agent_runner/tests/unit/test_restart.py)
- [tests/unit/test_tool_step_batch.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_agent_runner/tests/unit/test_tool_step_batch.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_agent_runner` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_agent_runner/swarmauri_agent_runner/AgentRunnerExecutionDriver.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_agent_runner` provides run model tool calls and resume checkpointed human interactions; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_agent_runner`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_agent_runner/swarmauri_agent_runner/AgentRunnerExecutionDriver.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_agent_runner` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_agent_runner/swarmauri_agent_runner/AgentRunnerExecutionDriver.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_agent_runner/pyproject.toml) provide the supporting context for `swarmauri_agent_runner`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.
- [swarmauri_tool_askuser](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_tool_askuser/README.md): Collect validated human input through an application-provided handler.
- [swarmauri_standard](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/swarmauri_standard/README.md): First-party Swarmauri standard components for agents, tools, parsers, vectors, model adapters, and composable intelligence workflows.

### Project Links

<!-- readme-standards:begin project-links -->
- [Repository](https://github.com/swarmauri/swarmauri-sdk)
- [pypi: swarmauri_agent_runner](https://pypi.org/project/swarmauri_agent_runner/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_agent_runner`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/standards/swarmauri_agent_runner` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

**Execution controller integration**

`AgentRunnerExecutionDriver(runner=runner)` adapts the existing runner to
`IExecutionDriver`. `initialize(prompt)` creates a checkpoint without running
work; `advance(run_id, max_steps=1)` yields after one runner step. Existing
`start`, `resume` and approval APIs remain supported. Pause/stop acknowledge
between steps, not in the middle of an external tool effect.
See the [composition guide](../../../docs/examples/composable-execution/README.md).

**Tool approvals and run stores**

Install `swarmauri-runstore-sqlite` to run the SQLite example. The runner
accepts an `IRunStore` and an OpenAI or Gemini tool model. Existing
OpenAI-shaped model callables and legacy typed run stores remain supported.

Set `approval_policy(tool, arguments)` to return `"ask"` for calls that
need review and configure an `approval_scope`. Render `state.event()` in your
application, then submit the authorized reviewer’s decision.

```python
from swarmauri_agent_runner import ApprovalDecision

state = runner.decide(
    run_id,
    ApprovalDecision(approval_id=approval_id, approved=True),
)
```

Use `runner.load(run_id)` to retrieve typed state from a reopened database.
`state.approval_requests` and `state.approval_decisions` retain the information
needed to render resolved approval cards. Tool execution status is separate.
When a process stops during tool dispatch, reconcile the external side effect
before recovering the run.

Existing SQLite databases work with the standalone adapter. The old
`swarmauri_agent_runner.SqliteRunStore` import accepts and returns typed
`RunState` objects. Install `swarmauri_agent_runner[sqlite]` to use that
compatibility wrapper.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_agent_runner` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_agent_runner/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_agent_runner` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_agent_runner` source version is `0.1.2`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_agent_runner/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/standards/swarmauri_agent_runner/NOTICE) for attribution.
<!-- readme-standards:end notices -->
