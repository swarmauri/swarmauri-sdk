# swarmauri-demo-package-maintenance

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri-demo-package-maintenance</strong></p>
<p align="center">A runnable Swarmauri demo for streaming Docker checks and resuming approvals.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri-demo-package-maintenance/"><img alt="pypi: swarmauri-demo-package-maintenance unpublished" src="https://img.shields.io/static/v1?label=pypi&amp;message=swarmauri-demo-package-maintenance%20unpublished&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/docs/examples/package-maintenance/pyproject.toml"><img alt="Source version: 0.1.1" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.1.1&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/docs/examples/package-maintenance/pyproject.toml"><img alt="Python: &gt;=3.12,&lt;3.13" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.12%2C%3C3.13&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/docs/examples/package-maintenance/pyproject.toml"><img alt="Layer: workspace" src="https://img.shields.io/static/v1?label=Layer&amp;message=workspace&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/docs/examples/package-maintenance/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/docs/examples/package-maintenance/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/docs/examples/package-maintenance/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri-demo-package-maintenance/"><img alt="pypi downloads: swarmauri-demo-package-maintenance: unpublished" src="https://img.shields.io/static/v1?label=pypi%20downloads&amp;message=swarmauri-demo-package-maintenance%3A%20unpublished&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/docs/examples/package-maintenance/README.md"><img alt="README hits: swarmauri-demo-package-maintenance" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/docs/examples/package-maintenance/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/docs/examples/package-maintenance/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/docs/examples/package-maintenance/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

Run real Ruff and pytest checks in Docker with
[`PackageMaintenanceAgent`](https://pypi.org/project/swarmauri-agent-package-maintenance/0.1.0/).
Its [`AgentRunner`](https://pypi.org/project/swarmauri-agent-runner/0.1.0/)
stores the pending approval in SQLite, so you can review it after the Python
process exits and apply your decision from a fresh process.

This example is maintained with the Swarmauri SDK examples. To share it,
copy this directory or link to it at a specific SDK commit. The host uses the
published versions declared in `pyproject.toml`. The Docker image contains a small
fixture package with an intentional formatting issue. A scripted model
selects the tool calls from the transcript, so the demo needs no LLM account
or API key.

### Why This Package

`swarmauri-demo-package-maintenance` isolates this responsibility: A runnable Swarmauri demo for streaming Docker checks and resuming approvals. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/docs/examples/package-maintenance/src/swarmauri_package_maintenance_demo/__init__.py) exposes `ScriptedMaintenanceModel`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri-demo-package-maintenance` when your integration needs a runnable Swarmauri demo for streaming Docker checks and resuming approvals. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- `ScriptedMaintenanceModel`: Choose the next tool from the transcript without calling a provider.

### Non-Goals

`swarmauri-demo-package-maintenance` owns a runnable Swarmauri demo for streaming Docker checks and resuming approvals. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.12,<3.13` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/docs/examples/package-maintenance/pyproject.toml) declares runtime dependencies including `swarmauri-agent-package-maintenance`, `swarmauri-runstore-sqlite`, `swarmauri-agent-runner`, `swarmauri-base`, `swarmauri-standard`, `swarmauri-toolkit-containertoolkit`. Read the example’s inputs and service requirements before execution.

### Installation

#### uv

<!-- readme-standards:begin installation.uv -->
`swarmauri-demo-package-maintenance` is not declared published. From the source checkout:

```bash
uv pip install .
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
`swarmauri-demo-package-maintenance` is not declared published. From the source checkout:

```bash
python -m pip install .
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
`swarmauri-demo-package-maintenance` is not declared published. From a separate Poetry project, replace the path with your checkout:

```bash
poetry add /path/to/swarmauri-demo-package-maintenance
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/docs/examples/package-maintenance/docs/readme/quick_start.py).

```python
import importlib

package = importlib.import_module("swarmauri_package_maintenance_demo")
assert package.__name__ == "swarmauri_package_maintenance_demo"
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

This quick start is explicitly an import smoke check for `swarmauri-demo-package-maintenance`. It confirms that the documented namespace loads; it does not demonstrate or certify a complete application workflow. The detailed source and retained usage guidance below describe the integration boundary.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/docs/examples/package-maintenance/docs/readme/usage.py).

```python
import importlib

package = importlib.import_module("swarmauri_package_maintenance_demo")
assert package.__name__ == "swarmauri_package_maintenance_demo"
```
<!-- readme-standards:end example.usage -->

### Configuration

Configure `swarmauri-demo-package-maintenance` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/docs/examples/package-maintenance/src/swarmauri_package_maintenance_demo/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/docs/examples/package-maintenance/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri-demo-package-maintenance` source raises `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri-demo-package-maintenance` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `ScriptedMaintenanceModel`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri-demo-package-maintenance` is located in `workspace` and owns a runnable Swarmauri demo for streaming Docker checks and resuming approvals. Source-declared APIs include `ScriptedMaintenanceModel`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/docs/examples/package-maintenance/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_package_maintenance_demo`.

Source-declared exports or types: `ScriptedMaintenanceModel`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/docs/examples/package-maintenance/src/swarmauri_package_maintenance_demo/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
This package declares no command-line, GUI, or plugin entry points in its manifest.
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri-demo-package-maintenance` are `swarmauri-agent-package-maintenance`, `swarmauri-runstore-sqlite`, `swarmauri-agent-runner`, `swarmauri-base`, `swarmauri-standard`, `swarmauri-toolkit-containertoolkit`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/docs/examples/package-maintenance/src/swarmauri_package_maintenance_demo/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri-demo-package-maintenance` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri-demo-package-maintenance`, use the source-declared public interfaces (`ScriptedMaintenanceModel`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri-demo-package-maintenance` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/docs/examples/package-maintenance/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri-demo-package-maintenance`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/docs/examples/package-maintenance/src/swarmauri_package_maintenance_demo/__init__.py). The `swarmauri-demo-package-maintenance` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri-demo-package-maintenance` declares Python `>=3.12,<3.13`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri-demo-package-maintenance` package directory for the maintained example source checks (Python compilation and non-Python file presence). Behavioral tests may live in the repository’s shared suites; the new README syntax test is not presented as runtime coverage for a runnable Swarmauri demo for streaming Docker checks and resuming approvals.

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri-demo-package-maintenance` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/docs/examples/package-maintenance/src/swarmauri_package_maintenance_demo/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri-demo-package-maintenance` provides a runnable Swarmauri demo for streaming Docker checks and resuming approvals; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri-demo-package-maintenance`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/docs/examples/package-maintenance/src/swarmauri_package_maintenance_demo/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri-demo-package-maintenance` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/docs/examples/package-maintenance/src/swarmauri_package_maintenance_demo/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/docs/examples/package-maintenance/pyproject.toml) provide the supporting context for `swarmauri-demo-package-maintenance`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_agent_package_maintenance](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_agent_package_maintenance/README.md): Compose human input, skills, and container checks for SDK maintenance.
- [swarmauri_agent_runner](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_agent_runner/README.md): Run model tool calls and resume checkpointed human interactions.
- [swarmauri_runstore_sqlite](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_runstore_sqlite/README.md): SQLite checkpoint storage for resumable Swarmauri agent runs.
- [swarmauri_toolkit_containertoolkit](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_toolkit_containertoolkit/README.md): Toolkit bundling container management tools.
- [swarmauri_standard](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/30-standard-kernel/swarmauri_standard/README.md): First-party Swarmauri standard components for agents, tools, parsers, vectors, model adapters, and composable intelligence workflows.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri-demo-package-maintenance](https://pypi.org/project/swarmauri-demo-package-maintenance/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri-demo-package-maintenance`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `docs/examples/package-maintenance` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

**Install and start**

Use Python 3.12, `uv`, and a running Docker engine in Linux container mode.
From the repository root, run:

```sh
cd docs/examples/package-maintenance
uv sync
uv run python -m swarmauri_package_maintenance_demo start
```

The Python demo builds the image from its packaged Dockerfile and fixture,
starts a disposable container, and runs the checks through the SDK's Docker
backend. The build downloads its dependencies. The running container uses
its installed tools offline and has no host mounts.

The agent calls `RunPackageChecks` with `fix=false`. Ruff streams a
`Would reformat` message and exits with code 1. The agent proposes the same
tool with `fix=true`. The SDK policy asks for approval, and the runner saves
the invocation and its approval ID in `.state/runs.sqlite3`.
The terminal shows the run ID, approval ID, tool arguments, and Docker scope.
Enter `a` to approve or `d` to deny. The demo submits your answer and the
approval ID to the runner. Enter `e` or press Enter to exit and decide later.
Closing input or pressing Ctrl+C at the prompt also leaves the request
pending. Save the run ID. The demo keeps the container running while it waits
for your decision.

**Resume in a new process**

Use the run ID to reopen the same approval prompt:

```sh
run_id='paste-run-id'
uv run python -m swarmauri_package_maintenance_demo resume "$run_id"
```

If you restart your terminal, return to the same working directory. If you
set `--db` before the `start` subcommand, pass the same path before `resume`.

The new agent constructs a fresh runner, recovers the Docker container ID
from SQLite, and verifies the approval against that container and the saved
tool arguments. It streams Ruff formatting, lint, and pytest output to the
terminal. Pytest prints `Checking fixture addition...` and then
`Fixture addition passed.` before the final `completed: Package checks passed.`
The read-only check from the first command has already finished and is not
replayed.

The demo stops and removes the container after approval or denial completes.
Each `start` creates a fresh workspace. Restart recovery applies at the saved
approval checkpoint.

When standard input is redirected, `start` and `resume` print the pending
request and exit. For a decision without a prompt, use the exact approval ID
shown in the request and choose `approve` or `deny`:

```sh
approval_id='paste-approval-id'
uv run python -m swarmauri_package_maintenance_demo decide "$run_id" "$approval_id" approve
```

**Build the Python distributable**

```sh
uv build
```

The `swarmauri-demo-package-maintenance` wheel and source distribution include
the Dockerfile and fixture.
The installed module uses those files when it builds the workspace, so the
wheel can run independently of the SDK checkout.

The CLI uses `swarmauri_runstore_sqlite.SqliteRunStore` for checkpoints. To test
restart, leave a request pending, exit the CLI, then reopen it with
`resume <run_id>` using the same database.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri-demo-package-maintenance` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/docs/examples/package-maintenance/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri-demo-package-maintenance` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri-demo-package-maintenance` source version is `0.1.1`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/docs/examples/package-maintenance/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/docs/examples/package-maintenance/NOTICE) for attribution.
<!-- readme-standards:end notices -->
