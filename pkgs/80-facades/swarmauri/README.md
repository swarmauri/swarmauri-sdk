# swarmauri

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/swarmauri/swarmauri-sdk"><img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"></a></p>
<p align="center"><strong>swarmauri</strong></p>
<p align="center">Swarmauri namespace microkernel for registry-backed imports, plugin discovery, and composable intelligence infrastructure components.</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri/"><img alt="pypi: swarmauri" src="https://img.shields.io/pypi/v/swarmauri?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/80-facades/swarmauri/pyproject.toml"><img alt="Source version: 0.11.0.dev12" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.11.0.dev12&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/80-facades/swarmauri/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/80-facades/swarmauri/pyproject.toml"><img alt="Layer: swarmauri" src="https://img.shields.io/static/v1?label=Layer&amp;message=swarmauri&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/80-facades/swarmauri/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/80-facades/swarmauri/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/80-facades/swarmauri/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/swarmauri/"><img alt="Monthly PyPI downloads: swarmauri" src="https://img.shields.io/pypi/dm/swarmauri?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/80-facades/swarmauri/README.md"><img alt="README hits: swarmauri" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/pkgs/80-facades/swarmauri/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/80-facades/swarmauri/tests/unit/test_readme_sources.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/80-facades/swarmauri/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

Swarmauri is the namespace package for the Swarmauri SDK. It installs the lightweight import microkernel that lets applications use stable `swarmauri.<component_kind>.<ClassName>` import paths while concrete implementations live in separate first-party, community, plugin, or experimental distributions.

### Why This Package

Swarmauri gives applications one stable Python namespace for a large and growing set of independently packaged SDK components. Instead of hard-coding every implementation package into application imports, the namespace importer resolves registered component paths through interface and citizenship registries.

### When to Use

Use `swarmauri` when you want the stable SDK namespace and plugin discovery behavior. Use the implementation package directly when you want to depend on only one specific component and do not need namespace routing.

### Features

- Stable `swarmauri.*` namespace imports for installed SDK components.
- Registry-backed component discovery through first-class, second-class, and third-class citizenship mappings.
- Entry-point scanning for installed plugins and community packages.
- Interface-aware resource kinds for agents, chains, chunkers, conversations, embeddings, LLMs, parsers, tools, vector stores, signing, crypto, key providers, transports, middleware, and more.
- Optional dependency groups for curated component families, including `default`, `full`, and `llms`.
- Pydantic-based typed component workflows through `swarmauri_base` and concrete packages.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

### Non-Goals

`swarmauri` owns swarmauri namespace microkernel for registry-backed imports, plugin discovery, and composable intelligence infrastructure components. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/80-facades/swarmauri/pyproject.toml) declares runtime dependencies including `toml`, `httpx`, `pydantic`, `typing-extensions`, `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. Read the example’s inputs and service requirements before execution.

### Installation

Install the namespace package with `uv`:

```bash
uv add swarmauri
```

Or install it with `pip`:

```bash
pip install swarmauri
```

Install optional LLM integrations when you want the curated LLM package set:

```bash
uv add "swarmauri[llms]"
```

For the broader curated component bundle:

```bash
uv add "swarmauri[full]"
```

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add swarmauri
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install swarmauri
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add swarmauri
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/80-facades/swarmauri/docs/readme/quick_start.py).

```python
import swarmauri

from swarmauri.interface_registry import InterfaceRegistry
from swarmauri.plugin_citizenship_registry import PluginCitizenshipRegistry

namespaces = InterfaceRegistry.list_registered_namespaces()
registered = PluginCitizenshipRegistry.total_registry()

print("known namespaces", len(namespaces))
print("known component mappings", len(registered))
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `swarmauri` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/80-facades/swarmauri/docs/readme/usage.py).

```python
import swarmauri

from swarmauri.interface_registry import InterfaceRegistry
from swarmauri.plugin_citizenship_registry import PluginCitizenshipRegistry

namespaces = InterfaceRegistry.list_registered_namespaces()
registered = PluginCitizenshipRegistry.total_registry()

print("known namespaces", len(namespaces))
print("known component mappings", len(registered))
```
<!-- readme-standards:end example.usage -->

Importing `swarmauri` activates the namespace importer and plugin discovery:


Resolve a component through a stable namespace path after the implementation package is installed:

```python
import swarmauri

from swarmauri.signings.Ed25519EnvelopeSigner import Ed25519EnvelopeSigner

signer = Ed25519EnvelopeSigner()
print(signer.type)
```

The implementation still comes from the signer package, but application code can use the Swarmauri public namespace.

List known public namespaces:

```python
from swarmauri.interface_registry import InterfaceRegistry

for namespace in InterfaceRegistry.list_registered_namespaces():
    print(namespace)
```

Inspect registered first-party and discovered component paths:

```python
from swarmauri.plugin_citizenship_registry import PluginCitizenshipRegistry

for (
    public_path,
    module_path,
) in PluginCitizenshipRegistry.total_registry().items():
    print(public_path, "->", module_path)
```

Invalidate plugin entry-point cache after changing the Python environment at runtime:

```python
from swarmauri.plugin_manager import invalidate_entry_point_cache

invalidate_entry_point_cache()
```

### Configuration

Configure `swarmauri` through the APIs in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/80-facades/swarmauri/swarmauri/interface_registry.py); its [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/80-facades/swarmauri/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `swarmauri` source raises `ImportError`, `KeyError`, `PluginLoadError`, `PluginValidationError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `swarmauri` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `SwarmauriImporter`, `discover_and_register_plugins`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`swarmauri` is located in `swarmauri` and owns swarmauri namespace microkernel for registry-backed imports, plugin discovery, and composable intelligence infrastructure components. Source-declared APIs include `SwarmauriImporter`, `discover_and_register_plugins`. The [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/80-facades/swarmauri/pyproject.toml) records its direct dependency boundary.

### Public API and Import Surfaces

Import namespace: `swarmauri`.

Source-declared exports or types: `SwarmauriImporter`, `discover_and_register_plugins`.

Inspect [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/80-facades/swarmauri/swarmauri/interface_registry.py) for exact signatures; this inventory does not designate every internal module as stable.

### Entry Points

<!-- readme-standards:begin entry-points -->
This package declares no command-line, GUI, or plugin entry points in its manifest.
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `swarmauri` are `toml`, `httpx`, `pydantic`, `typing-extensions`, `swarmauri-core`, `swarmauri-base`, `swarmauri-standard`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/80-facades/swarmauri/swarmauri/interface_registry.py).

### Protocol Consumers

No direct package-manifest dependency on `swarmauri` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `swarmauri`, use the source-declared public interfaces (`SwarmauriImporter`, `discover_and_register_plugins`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `swarmauri` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/80-facades/swarmauri/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `swarmauri`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/80-facades/swarmauri/swarmauri/interface_registry.py). The `swarmauri` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `swarmauri` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest tests/unit/test_readme_sources.py` from the `swarmauri` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_assert_truth.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/80-facades/swarmauri/tests/test_assert_truth.py)
- [tests/test_performance.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/80-facades/swarmauri/tests/test_performance.py)
- [tests/test_random_registration_performance.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/80-facades/swarmauri/tests/test_random_registration_performance.py)
- [tests/performance/test_namespace_performance.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/80-facades/swarmauri/tests/performance/test_namespace_performance.py)
- [tests/performance/test_plugin_discovery_benchmark.py](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/80-facades/swarmauri/tests/performance/test_plugin_discovery_benchmark.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No external certification is asserted for `swarmauri` by this documentation migration. README conformance, example syntax, runtime tests, and protocol or security certification are distinct evidence scopes.

### Evidence

The [README standards CI](https://github.com/swarmauri/swarmauri-sdk/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/80-facades/swarmauri/swarmauri/interface_registry.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Q: What does the swarmauri package install?**

A: It installs the public Swarmauri namespace, the namespace importer, interface registry access, plugin citizenship registry access, and entry-point discovery hooks.

**Q: Does swarmauri contain every component implementation?**

A: No. It routes to installed implementation packages. Foundational packages such as `swarmauri_core`, `swarmauri_base`, and `swarmauri_standard` provide contracts, base behavior, and standard components.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `swarmauri`, and consult [package source](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/80-facades/swarmauri/swarmauri/interface_registry.py) for the exact types and signatures involved.

### When

**Q: When should I import from swarmauri instead of a concrete package?**

A: Use `swarmauri` imports when you want stable public namespace paths. Import a concrete package directly when you want the narrowest dependency surface for one implementation.

This package is best for:

- AI application developers who want stable imports for agents, tools, models, parsers, vector stores, signing components, key providers, middleware, transports, and related SDK components.
- Platform engineers who need registry-driven plugin discovery without hard-coding every implementation package into application code.
- Component authors who want their packages to participate in the Swarmauri namespace through entry points and citizenship mappings.
- Operators who need a small runtime package that can load installed Swarmauri components on demand.

---

## Documentation and Related Packages

### More Documentation

- [Namespace import call flow](docs/callflow.md)
- [Citizenship registry notes](docs/citizenship.md)
- [Outcome notes](docs/outcomes.md)
- [Swarmauri SDK repository](https://github.com/swarmauri/swarmauri-sdk)

### Related Packages

Core Swarmauri packages:

- [swarmauri_core](https://pypi.org/project/swarmauri_core/) provides interface contracts used by component packages.
- [swarmauri_base](https://pypi.org/project/swarmauri_base/) provides reusable base classes, serialization helpers, and component registration behavior.
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/) provides first-party standard components across agents, tools, parsers, prompts, metrics, similarities, deprecated distance compatibility shims, and other common resource kinds.

Related component kinds:

- [swarmauri_signing_ed25519](https://pypi.org/project/swarmauri_signing_ed25519/) for Ed25519 envelope signing.
- [swarmauri_signing_jws](https://pypi.org/project/swarmauri_signing_jws/) for JWS signing and verification.
- [swarmauri_keyprovider_inmemory](https://pypi.org/project/swarmauri_keyprovider_inmemory/) for in-memory key management.
- [swarmauri_storage_memory](https://pypi.org/project/swarmauri_storage_memory/) for memory-backed storage adapters.
- [swarmauri_middleware_jsonrpc](https://pypi.org/project/swarmauri_middleware_jsonrpc/) for JSON-RPC middleware.
- [swarmauri_transport_stdio](https://pypi.org/project/swarmauri_transport_stdio/) for stdio transport integrations.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: swarmauri](https://pypi.org/project/swarmauri/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Contributions are welcome. Before adding a new public namespace path, update the interface and citizenship registries, add package-level tests for import resolution, and follow the [Swarmauri SDK contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md).

### Development Setup

Work from the `pkgs/80-facades/swarmauri` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest tests/unit/test_readme_sources.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

**What Is Swarmauri?**

Swarmauri is a composable intelligence infrastructure SDK for building typed, pluggable Python systems. The `swarmauri` distribution is the package users install when they want the public namespace, plugin discovery, registry-backed component resolution, and curated optional dependency groups for common component families.

**How The Namespace Works**

When `import swarmauri` runs, the package registers `SwarmauriImporter` on `sys.meta_path` and discovers installed plugins. The importer consults two registries:

- `InterfaceRegistry` maps resource namespaces such as `swarmauri.llms`, `swarmauri.tools`, and `swarmauri.signings` to their validation interfaces.
- `PluginCitizenshipRegistry` maps public namespace paths to implementation modules and classifies components as first-class, second-class, or third-class citizens.

The result is a stable public namespace over independently versioned packages. For example, `swarmauri.signings.Ed25519EnvelopeSigner` can resolve to the implementation package that provides the signer, while application code keeps the Swarmauri namespace import.

**Component Author Workflow**

To make a component available through the Swarmauri namespace:

1. Implement the concrete class in its own package.
2. Ensure the class satisfies the relevant interface from `swarmauri_core` and base behavior from `swarmauri_base`.
3. Expose the component through a `swarmauri.<kind>` entry point or a citizenship registry mapping.
4. Import `swarmauri` in the consuming environment so the namespace importer and plugin discovery run.
5. Validate the public namespace path in tests.

**Alpha TTS providers**

The `tts` extra installs separate OpenAI, DeepInfra, Together, Cartesia,
ElevenLabs, Deepgram, Gemini, Amazon Polly and Azure Speech TTS packages, plus native DeepInfra Kokoro/Qwen3/
voice-design, ElevenLabs dialogue and Gemini dialogue packages.
Install with `uv add --prerelease allow "swarmauri[tts]"` or
`pip install --pre "swarmauri[tts]"` after the candidate releases are published.
Use `from swarmauri.tts.OpenaiTTS import OpenaiTTS`, or the corresponding
`DeepInfraTTS`, `TogetherTTS`, `CartesiaTTS`, `ElevenLabsTTS`, `DeepgramTTS`
`GeminiTTS`, `PollyTTS`, `AzureTTS`, `DeepInfraKokoroTTS`,
`DeepInfraQwen3TTS`, `DeepInfraQwen3VoiceDesignTTS`, `ElevenLabsDialogueTTS`
and `GeminiDialogueTTS`
facade modules. Provider packages remain alpha
and their live verification issues are listed in
[the verification guide](../../../docs/verification/tts-providers.md).

---

## Governance

### Ownership and Decision Making

Changes to `swarmauri` follow the maintainer review process of [swarmauri/swarmauri-sdk](https://github.com/swarmauri/swarmauri-sdk) and its contribution guide. Author attribution remains in the [manifest](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/80-facades/swarmauri/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`swarmauri` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

The `swarmauri` source version is `0.11.0.dev12`. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/80-facades/swarmauri/LICENSE).
<!-- readme-standards:end license -->

Apache-2.0

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/swarmauri/swarmauri-sdk/blob/master/pkgs/80-facades/swarmauri/NOTICE) for attribution.
<!-- readme-standards:end notices -->
