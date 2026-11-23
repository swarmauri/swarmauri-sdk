# swarmauri_tool_subprocess

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_tool_subprocess</strong></p>
<p align="center">Run subprocesses with argument lists, timeouts, and structured results.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_tool_subprocess/"><img alt="pypi: swarmauri_tool_subprocess" src="https://img.shields.io/pypi/v/swarmauri_tool_subprocess?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tool_subprocess/pyproject.toml"><img alt="Source version: 0.11.0.dev4" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev4&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tool_subprocess/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tool_subprocess/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tool_subprocess/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tool_subprocess/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tool_subprocess/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_tool_subprocess/"><img alt="Monthly PyPI downloads: swarmauri_tool_subprocess" src="https://img.shields.io/pypi/dm/swarmauri_tool_subprocess?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tool_subprocess/README.md"><img alt="README hits: swarmauri_tool_subprocess" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/40-standards/swarmauri_tool_subprocess/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tool_subprocess/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tool_subprocess/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

Execute subprocess commands and capture output, timeouts, and exit codes.

### Why This Package

`swarmauri_tool_subprocess` isolates this responsibility: Run subprocesses with argument lists, timeouts, and structured results. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tool_subprocess/swarmauri_tool_subprocess/SubprocessTool.py) exposes `SubprocessTool`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_tool_subprocess` when your integration needs run subprocesses with argument lists, timeouts, and structured results. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Execute argument vectors without shell expansion by default.
- Capture stdout, stderr, and integer exit codes, including nonzero codes.
- Distinguish completed commands, missing executables, timeouts, and errors.
- Select a child working directory and an explicit replacement environment.
- Discover the component through the `swarmauri.tools` entry point and facade.
- Preserve the original standard import through a lazy compatibility adapter.
- Share execution with the standard kernel, which can run the legacy tool by itself.

### Non-Goals

`swarmauri_tool_subprocess` owns run subprocesses with argument lists, timeouts, and structured results. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tool_subprocess/pyproject.toml) declares runtime dependencies including `swarmauri-core`, `swarmauri-base`, `swarmauri-process-subprocess`. Read the example’s inputs and service requirements before execution.

### Installation

```bash
uv add swarmauri_tool_subprocess
pip install swarmauri_tool_subprocess
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_tool_subprocess
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_tool_subprocess
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_tool_subprocess
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tool_subprocess/docs/readme/quick_start.py).

```python
import sys
from swarmauri_tool_subprocess import SubprocessTool

tool = SubprocessTool()
result = tool([sys.executable, "-c", "print('hello')"], timeout=5)
assert result["stdout"].strip() == "hello"
assert result["exit_code"] == 0
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_tool_subprocess` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tool_subprocess/docs/readme/usage.py).

```python
import sys
from swarmauri_tool_subprocess import SubprocessTool

tool = SubprocessTool()
result = tool([sys.executable, "-c", "print('hello')"], timeout=5)
assert result["stdout"].strip() == "hello"
assert result["exit_code"] == 0
```
<!-- readme-standards:end example.usage -->

Use argument vectors for commands containing paths or arguments with spaces,
particularly on Windows. With `shell=False`, string commands use POSIX
`shlex.split` quoting; they are not parsed by the Windows command processor.

Shell mode accepts strings only and executes arbitrary syntax through the
platform shell (`/bin/sh` on POSIX or the configured Windows command processor):

```python
result = tool("echo first && echo second", shell=True, timeout=5)
```

Only trusted callers should choose shell commands, executables, working
directories, and environment values. Windows native mode (`shell=False`)
resolves the executable from the parent search environment and requires a
native `.exe` or `.com`. Use a trusted absolute executable path for deterministic
selection. To invoke trusted batch syntax, use explicit shell mode. Windows
may otherwise parse batch arguments through its command interpreter.

`cwd=None` inherits the parent's working directory. `env=None` deliberately
inherits the parent's environment for compatibility. Pass `env={...}` to supply
the complete child environment; it is not merged with the parent. Include any
platform-required variables (such as `SystemRoot` on Windows) and an appropriate
`PATH` when needed, or use an absolute executable path. Avoid forwarding secrets
the child does not need.

`timeout=None` imposes no timeout. A supplied timeout applies to the direct
child after process creation. Timed Windows calls capture output in temporary
files, so inherited output handles cannot make the timeout wait for pipe EOF.
On success, capture is a snapshot taken after the direct child exits.
Descendants can continue running and retain inherited temporary handles until
they exit. Keep subprocess execution under the service's trust policy.

### Configuration

Configure `swarmauri_tool_subprocess` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tool_subprocess/swarmauri_tool_subprocess/SubprocessTool.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tool_subprocess/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_tool_subprocess` source does not establish a package-wide exception hierarchy. Preserve errors from its declared dependencies and validate inputs using the specific public contract in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tool_subprocess/swarmauri_tool_subprocess/SubprocessTool.py).

### Best Practices

Use the explicit `swarmauri_tool_subprocess` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `SubprocessTool`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_tool_subprocess` is located in `standards` and owns run subprocesses with argument lists, timeouts, and structured results. Source-declared APIs include `SubprocessTool`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tool_subprocess/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_tool_subprocess`.

Source-declared exports or types: `SubprocessTool`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tool_subprocess/swarmauri_tool_subprocess/SubprocessTool.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.tools` → `SubprocessTool` → `swarmauri_tool_subprocess:SubprocessTool`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_tool_subprocess` are `swarmauri-core`, `swarmauri-base`, `swarmauri-process-subprocess`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tool_subprocess/swarmauri_tool_subprocess/SubprocessTool.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri_tool_subprocess` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri_tool_subprocess`, use the source-declared public interfaces (`SubprocessTool`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_tool_subprocess` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tool_subprocess/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_tool_subprocess`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tool_subprocess/swarmauri_tool_subprocess/SubprocessTool.py). The `swarmauri_tool_subprocess` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_tool_subprocess` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_tool_subprocess` package directory for the maintained example source checks (Python compilation and non-Python file presence). Behavioral tests may live in the repository’s shared suites; the new README syntax test is not presented as runtime coverage for run subprocesses with argument lists, timeouts, and structured results.

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_tool_subprocess` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tool_subprocess/swarmauri_tool_subprocess/SubprocessTool.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_tool_subprocess` provides run subprocesses with argument lists, timeouts, and structured results; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_tool_subprocess`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tool_subprocess/swarmauri_tool_subprocess/SubprocessTool.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_tool_subprocess` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tool_subprocess/swarmauri_tool_subprocess/SubprocessTool.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tool_subprocess/pyproject.toml) provide the supporting context for `swarmauri_tool_subprocess`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.
- [swarmauri_process_subprocess](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_process_subprocess/README.md): Stream and control commands running on the local host.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_tool_subprocess](https://pypi.org/project/swarmauri_tool_subprocess/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_tool_subprocess`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/40-standards/swarmauri_tool_subprocess` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

**Results and migration**

The standalone API returns `status`, `stdout`, `stderr`, and `exit_code`:

| Status | Meaning | Exit code |
|---|---|---|
| `success` | Process completed, including nonzero exit codes | Integer |
| `timeout` | Process exceeded the timeout | `None` |
| `not_found` | Executable or requested working directory was not found | `127` |
| `runtime_error` | Invalid arguments or another execution failure | `None` |

`success` describes process completion, not application success; check
`exit_code == 0` before treating a command as successful. Passing an argument
list with `shell=True`, an empty command, or malformed quoting returns
`runtime_error` without starting a child.

Existing code can continue to use the original case-sensitive import:

```python
from swarmauri_standard.tools.SubprocessTool import SubprocessTool

result = SubprocessTool()("echo hello", shell=True)
assert result["exit_code"] == "0"
```

The compatibility adapter emits a `DeprecationWarning` and retains the original
three-key result and string exit codes: numeric strings for completed commands,
`"timeout"` for timeouts, and `"error"` for execution failures. Import from the
standalone package when adopting the richer typed results and `cwd`/`env`
options. Importing the compatibility module alone does not load the standalone
package.
The lowercase module spelling introduced in the PR is also accepted as an
import alias. Both spellings share the same module and legacy result contract.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_tool_subprocess` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tool_subprocess/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_tool_subprocess` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_tool_subprocess` source version is `0.11.0.dev4`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tool_subprocess/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tool_subprocess/NOTICE) for attribution.
<!-- readme-standards:end notices -->
