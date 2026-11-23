# swarmauri_toolkit_runtime

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri_toolkit_runtime</strong></p>
<p align="center">Runtime toolkit for explicit-parameter registration, inspection, replacement, listing, and removal of Swarmauri tools during agent execution.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_toolkit_runtime/"><img alt="pypi: swarmauri_toolkit_runtime" src="https://img.shields.io/pypi/v/swarmauri_toolkit_runtime?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_toolkit_runtime/pyproject.toml"><img alt="Source version: 0.11.0.dev4" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev4&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_toolkit_runtime/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_toolkit_runtime/pyproject.toml"><img alt="Layer: standards" src="https://img.shields.io/static/v1?label=Layer&amp;message=standards&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_toolkit_runtime/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_toolkit_runtime/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_toolkit_runtime/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri_toolkit_runtime/"><img alt="Monthly PyPI downloads: swarmauri_toolkit_runtime" src="https://img.shields.io/pypi/dm/swarmauri_toolkit_runtime?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_toolkit_runtime/README.md"><img alt="README hits: swarmauri_toolkit_runtime" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/40-standards/swarmauri_toolkit_runtime/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_toolkit_runtime/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_toolkit_runtime/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`RuntimeToolkit` is a Swarmauri runtime-management toolkit for agents that need to register, inspect, list, replace, and remove tools during execution. It keeps tool mutation inside the active toolkit instance and requires both explicit parameter declarations and an explicit `__call__` implementation when a new runtime tool is introduced.

### Why This Package

`swarmauri_toolkit_runtime` isolates this responsibility: Runtime toolkit for explicit-parameter registration, inspection, replacement, listing, and removal of Swarmauri tools during agent execution. Its [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_toolkit_runtime/swarmauri_toolkit_runtime/__init__.py) exposes `InspectRuntimeTool`, `ListRuntimeTools`, `RegisterRuntimeTool`, `ReplaceRuntimeTool`, `RuntimeToolkit`, `UnregisterRuntimeTool`, allowing consumers to select this package without treating adjacent packages as part of its public contract.

### When to Use

Choose `swarmauri_toolkit_runtime` when your integration needs runtime toolkit for explicit-parameter registration, inspection, replacement, listing, and removal of Swarmauri tools during agent execution. Match the imports below to your application boundary and install its declared dependencies before using the example.

### Features

- Bundles agent-callable CRUD operations for toolkit members.
- Accepts serialized runtime tool specs with `type`, `parameters`, and `__call__` fields.
- Enforces a non-empty declared `parameters` list and a non-empty `__call__` body for runtime tool registration and replacement.
- Evaluates runtime `__call__` bodies through a restricted expression rail rather than unrestricted Python execution.
- Returns agent-friendly dictionaries for reads, lists, and mutation results.
- Protects the toolkit's own management tools from accidental overwrite or removal.
- Supports Python 3.10 through 3.14.

### Non-Goals

`swarmauri_toolkit_runtime` owns runtime toolkit for explicit-parameter registration, inspection, replacement, listing, and removal of Swarmauri tools during agent execution. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_toolkit_runtime/pyproject.toml) declares runtime dependencies including `swarmauri-tool-registerruntimetool`, `swarmauri-tool-inspectruntimetool`, `swarmauri-tool-listruntimetools`, `swarmauri-tool-replaceruntimetool`, `swarmauri-tool-unregisterruntimetool`, `pydantic`, `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. Read the example’s inputs and service requirements before execution.

### Installation

**uv**

```bash
uv add swarmauri_toolkit_runtime
```

**pip**

```bash
pip install swarmauri_toolkit_runtime
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri_toolkit_runtime
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri_toolkit_runtime
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri_toolkit_runtime
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_toolkit_runtime/docs/readme/quick_start.py).

```python
from swarmauri_toolkit_runtime import RuntimeToolkit

toolkit = RuntimeToolkit()

toolkit.get_tool_by_name("RegisterRuntimeTool")(
    {
        "type": "RuntimeAdditionTool",
        "name": "RuntimeAdditionTool",
        "description": "Adds two integers during the active agent session.",
        "parameters": [
            {
                "name": "x",
                "input_type": "integer",
                "description": "The left operand",
                "required": True,
            },
            {
                "name": "y",
                "input_type": "integer",
                "description": "The right operand",
                "required": True,
            },
        ],
        "__call__": '{"sum": str(x + y)}',
    }
)

result = toolkit.get_tool_by_name("RuntimeAdditionTool")(2, 3)
print(result)
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri_toolkit_runtime` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_toolkit_runtime/docs/readme/usage.py).

```python
from swarmauri_toolkit_runtime import RuntimeToolkit

toolkit = RuntimeToolkit()

toolkit.get_tool_by_name("RegisterRuntimeTool")(
    {
        "type": "RuntimeAdditionTool",
        "name": "RuntimeAdditionTool",
        "description": "Adds two integers during the active agent session.",
        "parameters": [
            {
                "name": "x",
                "input_type": "integer",
                "description": "The left operand",
                "required": True,
            },
            {
                "name": "y",
                "input_type": "integer",
                "description": "The right operand",
                "required": True,
            },
        ],
        "__call__": '{"sum": str(x + y)}',
    }
)

result = toolkit.get_tool_by_name("RuntimeAdditionTool")(2, 3)
print(result)
```
<!-- readme-standards:end example.usage -->

Use `RuntimeToolkit` when an agent needs to mutate its own tool surface safely at runtime. The expected workflow is:

1. Start with the management toolkit.
2. Register a runtime tool using an explicit parameter contract and explicit callable body.
3. Inspect or list the available runtime tools.
4. Execute the registered tool.
5. Replace or unregister the tool when the runtime surface changes.

Instantiate the toolkit and hand it to an agent or tool-capable model. The toolkit starts with only its management tools, then grows as the agent adds tools.

### Configuration

Configure `swarmauri_toolkit_runtime` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_toolkit_runtime/swarmauri_toolkit_runtime/__init__.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_toolkit_runtime/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri_toolkit_runtime` source raises `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri_toolkit_runtime` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `InspectRuntimeTool`, `ListRuntimeTools`, `RegisterRuntimeTool`, `ReplaceRuntimeTool`, `RuntimeToolkit`, `UnregisterRuntimeTool`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri_toolkit_runtime` is located in `standards` and owns runtime toolkit for explicit-parameter registration, inspection, replacement, listing, and removal of Swarmauri tools during agent execution. Source-declared APIs include `InspectRuntimeTool`, `ListRuntimeTools`, `RegisterRuntimeTool`, `ReplaceRuntimeTool`, `RuntimeToolkit`, `UnregisterRuntimeTool`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_toolkit_runtime/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri_toolkit_runtime`.

Source-declared exports or types: `InspectRuntimeTool`, `ListRuntimeTools`, `RegisterRuntimeTool`, `ReplaceRuntimeTool`, `RuntimeToolkit`, `UnregisterRuntimeTool`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_toolkit_runtime/swarmauri_toolkit_runtime/__init__.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `swarmauri.toolkits` → `RuntimeToolkit` → `swarmauri_toolkit_runtime:RuntimeToolkit`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri_toolkit_runtime` are `swarmauri-tool-registerruntimetool`, `swarmauri-tool-inspectruntimetool`, `swarmauri-tool-listruntimetools`, `swarmauri-tool-replaceruntimetool`, `swarmauri-tool-unregisterruntimetool`, `pydantic`, `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_toolkit_runtime/swarmauri_toolkit_runtime/__init__.py).

### Protocol Consumers

Direct consumers in this checkout’s package manifests include `swarmauri_agent_package_maintenance`. These edges describe declared dependencies, not protocol-conformance evidence.

### Extensions

For `swarmauri_toolkit_runtime`, use the source-declared public interfaces (`InspectRuntimeTool`, `ListRuntimeTools`, `RegisterRuntimeTool`, `ReplaceRuntimeTool`, `RuntimeToolkit`, `UnregisterRuntimeTool`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri_toolkit_runtime` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_toolkit_runtime/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri_toolkit_runtime`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_toolkit_runtime/swarmauri_toolkit_runtime/__init__.py). The `swarmauri_toolkit_runtime` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri_toolkit_runtime` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri_toolkit_runtime` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/unit/test_RuntimeToolkit.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_toolkit_runtime/tests/unit/test_RuntimeToolkit.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri_toolkit_runtime` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_toolkit_runtime/swarmauri_toolkit_runtime/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `swarmauri_toolkit_runtime` provides runtime toolkit for explicit-parameter registration, inspection, replacement, listing, and removal of Swarmauri tools during agent execution; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri_toolkit_runtime`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_toolkit_runtime/swarmauri_toolkit_runtime/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `swarmauri_toolkit_runtime` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

The [repository contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md), [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_toolkit_runtime/swarmauri_toolkit_runtime/__init__.py), and [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_toolkit_runtime/pyproject.toml) provide the supporting context for `swarmauri_toolkit_runtime`. The [README policy](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md) defines the common document structure.

### Related Packages

- [swarmauri_base](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/20-bases/swarmauri_base/README.md): Reusable Swarmauri base classes, mixins, and dynamic Pydantic component models for composable intelligence infrastructure.
- [swarmauri_core](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/10-interfaces/swarmauri_core/README.md): Core interface contracts and shared types for Swarmauri composable intelligence infrastructure components.
- [swarmauri_tool_inspectruntimetool](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tool_inspectruntimetool/README.md): Inspect a runtime tool and its declared inputs.
- [swarmauri_tool_listruntimetools](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tool_listruntimetools/README.md): List the tools in a runtime toolkit.
- [swarmauri_tool_registerruntimetool](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tool_registerruntimetool/README.md): Register a tool in a runtime toolkit.
- [swarmauri_tool_replaceruntimetool](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tool_replaceruntimetool/README.md): Replace a tool in a runtime toolkit.
- [swarmauri_tool_unregisterruntimetool](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_tool_unregisterruntimetool/README.md): Remove a tool from a runtime toolkit.
- [swarmauri_standard](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/30-standard-kernel/swarmauri_standard/README.md): First-party Swarmauri standard components for agents, tools, parsers, vectors, model adapters, and composable intelligence workflows.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri_toolkit_runtime](https://pypi.org/project/swarmauri_toolkit_runtime/)
<!-- readme-standards:end project-links -->

- Python `3.10`
- Python `3.11`
- Python `3.12`

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `swarmauri_toolkit_runtime`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/40-standards/swarmauri_toolkit_runtime` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

**Agent Workflow**

1. Call `ListRuntimeTools` to inspect the current runtime surface.
2. Call `RegisterRuntimeTool` with a tool spec to extend the toolkit.
3. Call `InspectRuntimeTool` to inspect the hydrated tool metadata.
4. Call `ReplaceRuntimeTool` when the agent needs to replace a tool with a revised spec.
5. Call `UnregisterRuntimeTool` when a runtime tool should no longer be available.

**Tool Spec Contract**

Mutation tools accept a serialized tool specification. At minimum, provide:

- a non-empty `type` field that names the runtime tool surface
- a non-empty `parameters` list that explicitly declares the runtime callable contract
- a non-empty `__call__` string that evaluates as a safe Python expression over the declared parameters and approved builtins

The runtime evaluator permits only a constrained expression subset and approved builtins such as `str`, `int`, `float`, `len`, `sum`, `min`, `max`, and `abs`. Imports, attribute traversal, and arbitrary function calls are rejected.

```python
{
    "type": "RuntimeAdditionTool",
    "name": "RuntimeAdditionTool",
    "description": "Adds two integers.",
    "parameters": [
        {
            "name": "x",
            "input_type": "integer",
            "description": "The left operand",
            "required": True,
        },
        {
            "name": "y",
            "input_type": "integer",
            "description": "The right operand",
            "required": True,
        },
    ],
    "__call__": '{"sum": str(x + y)}',
}
```

The `__call__` value is evaluated against the declared parameter names. A body such as `{"sum": str(x + y)}` is valid. A body that tries to import modules, access attributes, or reference undeclared names is rejected.

**Failure Modes**

- Registration fails when the tool spec omits `parameters`.
- Registration fails when the tool spec omits `__call__`.
- Registration fails when the `__call__` body uses unsafe syntax or disallowed names.
- Registration fails when the tool name collides with a protected management tool.
- Execution failures inside an accepted runtime tool return a structured error payload instead of propagating a hard exception or terminating the host process.
- Replacement fails when the target tool is missing, reserved, or renamed to an existing tool.
- Unregistration fails when the target is reserved or absent.

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri_toolkit_runtime` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_toolkit_runtime/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri_toolkit_runtime` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri_toolkit_runtime` source version is `0.11.0.dev4`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_toolkit_runtime/LICENSE).
<!-- readme-standards:end license -->

`swarmauri_toolkit_runtime` is released under the Apache 2.0 License. See `LICENSE` for details.

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/40-standards/swarmauri_toolkit_runtime/NOTICE) for attribution.
<!-- readme-standards:end notices -->
