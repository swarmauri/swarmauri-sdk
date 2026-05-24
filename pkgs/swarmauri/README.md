![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri/">
        <img src="https://static.pepy.tech/badge/swarmauri/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/swarmauri/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/swarmauri.svg"/></a>
    <a href="https://pypi.org/project/swarmauri/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri/">
        <img src="https://img.shields.io/pypi/l/swarmauri" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri/">
        <img src="https://img.shields.io/pypi/v/swarmauri?label=swarmauri&color=green" alt="PyPI - swarmauri"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri

Swarmauri is the namespace package for the Swarmauri SDK. It installs the lightweight import microkernel that lets applications use stable `swarmauri.<component_kind>.<ClassName>` import paths while concrete implementations live in separate first-party, community, plugin, or experimental distributions.

## What Is Swarmauri?

Swarmauri is a composable intelligence infrastructure SDK for building typed, pluggable Python systems. The `swarmauri` distribution is the package users install when they want the public namespace, plugin discovery, registry-backed component resolution, and curated optional dependency groups for common component families.

## Why Swarmauri?

Swarmauri gives applications one stable Python namespace for a large and growing set of independently packaged SDK components. Instead of hard-coding every implementation package into application imports, the namespace importer resolves registered component paths through interface and citizenship registries.

## FAQ

### Q: What does the `swarmauri` package install?

A: It installs the public Swarmauri namespace, the namespace importer, interface registry access, plugin citizenship registry access, and entry-point discovery hooks.

### Q: Does `swarmauri` contain every component implementation?

A: No. It routes to installed implementation packages. Foundational packages such as `swarmauri_core`, `swarmauri_base`, and `swarmauri_standard` provide contracts, base behavior, and standard components.

### Q: When should I import from `swarmauri` instead of a concrete package?

A: Use `swarmauri` imports when you want stable public namespace paths. Import a concrete package directly when you want the narrowest dependency surface for one implementation.

This package is best for:

- AI application developers who want stable imports for agents, tools, models, parsers, vector stores, signing components, key providers, middleware, transports, and related SDK components.
- Platform engineers who need registry-driven plugin discovery without hard-coding every implementation package into application code.
- Component authors who want their packages to participate in the Swarmauri namespace through entry points and citizenship mappings.
- Operators who need a small runtime package that can load installed Swarmauri components on demand.

## How The Namespace Works

When `import swarmauri` runs, the package registers `SwarmauriImporter` on `sys.meta_path` and discovers installed plugins. The importer consults two registries:

- `InterfaceRegistry` maps resource namespaces such as `swarmauri.llms`, `swarmauri.tools`, and `swarmauri.signings` to their validation interfaces.
- `PluginCitizenshipRegistry` maps public namespace paths to implementation modules and classifies components as first-class, second-class, or third-class citizens.

The result is a stable public namespace over independently versioned packages. For example, `swarmauri.signings.Ed25519EnvelopeSigner` can resolve to the implementation package that provides the signer, while application code keeps the Swarmauri namespace import.

## Features

- Stable `swarmauri.*` namespace imports for installed SDK components.
- Registry-backed component discovery through first-class, second-class, and third-class citizenship mappings.
- Entry-point scanning for installed plugins and community packages.
- Interface-aware resource kinds for agents, chains, chunkers, conversations, embeddings, LLMs, parsers, tools, vector stores, signing, crypto, key providers, transports, middleware, and more.
- Optional dependency groups for curated component families, including `default`, `full`, and `llms`.
- Pydantic-based typed component workflows through `swarmauri_base` and concrete packages.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

## Installation

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

## Usage

Importing `swarmauri` activates the namespace importer and plugin discovery:

```python
import swarmauri

from swarmauri.interface_registry import InterfaceRegistry
from swarmauri.plugin_citizenship_registry import PluginCitizenshipRegistry

namespaces = InterfaceRegistry.list_registered_namespaces()
registered = PluginCitizenshipRegistry.total_registry()

print("known namespaces", len(namespaces))
print("known component mappings", len(registered))
```

Resolve a component through a stable namespace path after the implementation package is installed:

```python
import swarmauri

from swarmauri.signings.Ed25519EnvelopeSigner import Ed25519EnvelopeSigner

signer = Ed25519EnvelopeSigner()
print(signer.type)
```

The implementation still comes from the signer package, but application code can use the Swarmauri public namespace.

## Component Author Workflow

To make a component available through the Swarmauri namespace:

1. Implement the concrete class in its own package.
2. Ensure the class satisfies the relevant interface from `swarmauri_core` and base behavior from `swarmauri_base`.
3. Expose the component through a `swarmauri.<kind>` entry point or a citizenship registry mapping.
4. Import `swarmauri` in the consuming environment so the namespace importer and plugin discovery run.
5. Validate the public namespace path in tests.

## Examples

List known public namespaces:

```python
from swarmauri.interface_registry import InterfaceRegistry

for namespace in InterfaceRegistry.list_registered_namespaces():
    print(namespace)
```

Inspect registered first-party and discovered component paths:

```python
from swarmauri.plugin_citizenship_registry import PluginCitizenshipRegistry

for public_path, module_path in PluginCitizenshipRegistry.total_registry().items():
    print(public_path, "->", module_path)
```

Invalidate plugin entry-point cache after changing the Python environment at runtime:

```python
from swarmauri.plugin_manager import invalidate_entry_point_cache

invalidate_entry_point_cache()
```

## Related Packages

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

## Documentation

- [Namespace import call flow](docs/callflow.md)
- [Citizenship registry notes](docs/citizenship.md)
- [Outcome notes](docs/outcomes.md)
- [Swarmauri SDK repository](https://github.com/swarmauri/swarmauri-sdk)

## When To Use This Package

Use `swarmauri` when you want the stable SDK namespace and plugin discovery behavior. Use the implementation package directly when you want to depend on only one specific component and do not need namespace routing.

## License

Apache-2.0

## Contributing

Contributions are welcome. Before adding a new public namespace path, update the interface and citizenship registries, add package-level tests for import resolution, and follow the [Swarmauri SDK contribution guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md).


