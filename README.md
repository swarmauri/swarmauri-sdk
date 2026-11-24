# Swarmauri SDK

<p align="center">
    <a href="https://github.com/swarmauri/swarmauri-sdk">
        <img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg" alt="Swarmauri SDK" width="300"/></a>
</p>

<p align="center">
    <a href="https://pepy.tech/project/swarmauri/">
        <img src="https://static.pepy.tech/badge/swarmauri/month" alt="PyPI - Downloads"/></a>
    <a href="https://github.com/swarmauri/swarmauri-sdk/blob/master/README.md">
        <img alt="Repository README hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/README.md.svg?label=README%20hits"/></a>
    <a href="https://pypi.org/project/swarmauri/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri/">
        <img src="https://img.shields.io/pypi/l/swarmauri" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri/">
        <img src="https://img.shields.io/pypi/v/swarmauri?label=swarmauri&color=green" alt="PyPI - swarmauri"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

<p align="center">
    <a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a>
</p>

---

## Overview

### Summary

Swarmauri is a composable intelligence infrastructure SDK for building typed, pluggable Python systems. The repository contains the public `swarmauri` namespace package, interface contracts, reusable base classes, standard components, community integrations, plugin packages, and package-level documentation for independently installable Swarmauri distributions.

### Why This Package

Swarmauri separates component contracts from implementations so applications can compose agents, tools, models, parsers, vector stores, signing components, key providers, transports, middleware, billing providers, and storage adapters without locking every workflow to one provider package. The namespace package gives users stable imports while individual packages keep dependencies focused.

### When to Use

Use the namespace package when composing installed components through stable public imports. Use the foundational packages when writing a component, or install a focused distribution for a specific provider or component kind.

### Features

- Stable `swarmauri.*` namespace imports through the namespace package.
- Interface-first package architecture through `swarmauri_core`.
- Pydantic-backed base classes, serialization helpers, and dynamic component registration through `swarmauri_base`.
- First-party standard components through `swarmauri_standard`.
- Independently installable community, plugin, experimental, and standards packages.
- Component families for agents, chains, conversations, documents, embeddings, LLMs, parsers, prompts, schema converters, tools, toolkits, vector stores, signing, crypto, key providers, transports, middleware, storage, XMP, billing, and more.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

### Non-Goals

Application code owns provider selection, credentials, and deployment. The SDK supplies interfaces, reusable implementations, and discovery for the components installed in the application environment.

---

## Getting Started

### Prerequisites

Use Python 3.10 through 3.14 for the workflows below. Check each implementation package for its own Python requirements and any provider credentials or services it needs.

### Installation

Install `swarmauri` for the public namespace and plugin discovery. The `full` extra adds the broader curated component bundle. Install `swarmauri_core` and `swarmauri_base` to develop components against the foundational packages.

#### uv

```bash
uv add swarmauri
```

```bash
uv add "swarmauri[full]"
```

```bash
uv add swarmauri_core swarmauri_base
```

Choose a focused package when you only need one component family.

```bash
uv add swarmauri_vectorstore_pinecone
uv add swarmauri_tool_jupyterexportlatex
uv add swarmauri_signing_ed25519
```

#### pip

```bash
pip install swarmauri
```

```bash
pip install "swarmauri[full]"
```

```bash
pip install swarmauri_core swarmauri_base
```

```bash
pip install swarmauri_vectorstore_pinecone
pip install swarmauri_tool_jupyterexportlatex
pip install swarmauri_signing_ed25519
```

#### Poetry

```bash
poetry add swarmauri
```

### Quick Start

#### Example

Importing `swarmauri` activates namespace discovery for installed components.

```python
import swarmauri

from swarmauri.interface_registry import InterfaceRegistry
from swarmauri.plugin_citizenship_registry import PluginCitizenshipRegistry

print(len(InterfaceRegistry.list_registered_namespaces()))
print(len(PluginCitizenshipRegistry.total_registry()))
```

#### Expected Result

The example prints the number of registered namespaces and then the number of registered component mappings. The counts depend on the installed distributions.

---

## Usage

### Common Workflows

**Use a stable namespace import.** Install `swarmauri` and `swarmauri_signing_ed25519` to resolve the signer through the public namespace.

```python
import swarmauri

from swarmauri.signings.Ed25519EnvelopeSigner import Ed25519EnvelopeSigner

signer = Ed25519EnvelopeSigner()
print(signer.type)
```

**Import an implementation directly.** Install `swarmauri_standard` to use its document and tool classes through their package imports.

```python
from swarmauri_standard.documents.Document import Document
from swarmauri_standard.tools.AdditionTool import AdditionTool

doc = Document(content="Direct package import")
tool = AdditionTool()

print(doc.type)
print(tool(2, 2))
```

**Inspect component mappings.** Print up to ten public import paths alongside their implementation modules.

```python
from swarmauri.plugin_citizenship_registry import PluginCitizenshipRegistry

for public_path, module_path in list(PluginCitizenshipRegistry.total_registry().items())[:10]:
    print(public_path, "->", module_path)
```

**Deserialize a registered component.** Use the base package to deserialize a typed component as part of a Pydantic model.

```python
from typing import Literal

from pydantic import BaseModel
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.DynamicBase import SubclassUnion


@ComponentBase.register_model()
class ConnectorBase(ComponentBase):
    type: Literal["ConnectorBase"] = "ConnectorBase"
    label: str


@ComponentBase.register_type(ConnectorBase, "ApiConnector")
class ApiConnector(ConnectorBase):
    type: Literal["ApiConnector"] = "ApiConnector"
    endpoint: str


class ConnectorSpec(BaseModel):
    connector: SubclassUnion[ConnectorBase]


spec = ConnectorSpec.model_validate_json(
    '{"connector":{"type":"ApiConnector","label":"primary","endpoint":"https://api.example.test"}}'
)

assert isinstance(spec.connector, ApiConnector)
```

### Configuration

Select optional dependency groups and implementation distributions at install time. Configure provider credentials and component options where the application constructs the selected implementation.

### Error Handling

If a public import fails, check whether the implementation package is installed and inspect the registry mappings to see which module owns the requested path. If Pydantic rejects serialized component data, check the discriminator and the fields required by the registered type.

### Best Practices

Instantiate components directly. Use a public namespace import where you want registry-backed resolution, or import from the implementation package to keep dependencies focused.

---

## Package Boundary

### What It Owns

The repository contains separately installable distributions with distinct responsibilities.

**Foundational packages**

- [swarmauri](https://pypi.org/project/swarmauri/) provides the namespace importer and plugin discovery layer.
- [swarmauri_core](https://pypi.org/project/swarmauri_core/) provides interface contracts and shared types.
- [swarmauri_base](https://pypi.org/project/swarmauri_base/) provides reusable base classes, serialization helpers, and component registration behavior.
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/) provides first-party standard components.
- [swarmauri_typing](https://pypi.org/project/swarmauri_typing/) provides dynamic typing utilities used by Swarmauri base classes.

**Repository package areas**

- `pkgs/10-interfaces/swarmauri_core`, `pkgs/20-bases/swarmauri_base`, `pkgs/00-typing/swarmauri_typing`, and `pkgs/80-facades/swarmauri` contain foundational packages.
- `pkgs/30-standard-kernel/swarmauri_standard` contains first-party standard components.
- `pkgs/50-community` contains community-maintained packages and provider integrations.
- `pkgs/60-plugins` contains plugin packages.
- `pkgs/40-standards` contains standard-interface and standards-oriented packages.
- `pkgs/70-experimental` contains early-stage packages.

**Common package families**

- `swarmauri_vectorstore_*` packages provide vector database integrations.
- `swarmauri_embedding_*` packages provide embedding model integrations.
- `swarmauri_tool_*` packages provide task-specific tools.
- `swarmauri_parser_*` packages provide parsing utilities.
- `swarmauri_signing_*` packages provide signing implementations.
- `swarmauri_keyprovider_*` packages provide key-management implementations.
- `swarmauri_billing_*` packages provide billing provider implementations and stubs.

### Public API and Import Surfaces

Applications can import registered classes through `swarmauri.*` or import directly from package paths such as `swarmauri_standard.documents` and `swarmauri_standard.tools`. Component authors use the contracts and base classes from `swarmauri_core` and `swarmauri_base`.

### Entry Points

Packages that participate in namespace discovery declare their mappings in `pyproject.toml`. For example, a vector store plugin can declare this entry point.

```toml
[project.entry-points.'swarmauri.vectorstores']
YourVectorStore = "swarmauri_vectorstore_yourplugin:YourVectorStore"
```

### Injected Dependencies

Applications supply the concrete components and provider settings they need. Each distribution declares its own install dependencies, and the namespace resolves implementations from the installed environment.

### Protocol Consumers

Applications consume the component contracts from `swarmauri_core`. The namespace importer consumes interface and citizenship registry mappings to resolve public import paths. The related package catalog includes stdio transport and JSON-RPC middleware implementations.

### Extensions

Create component packages with direct instantiation in mind. Plugins should expose clear package-level imports, use the relevant `swarmauri_core` interface and `swarmauri_base` base class, document installation and usage, and register entry points where namespace discovery is expected.

```python
from typing import Literal

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.vector_stores.VectorStoreBase import VectorStoreBase


@ComponentBase.register_type(VectorStoreBase, "YourVectorStore")
class YourVectorStore(VectorStoreBase):
    type: Literal["YourVectorStore"] = "YourVectorStore"
```

---

## Operations and Readiness

### Operational Requirements

Install the implementation packages in the same Python environment as the application. Provider-backed components may also require credentials, network access, or a running backend as documented by the selected package.

### Health and Observability

Use the registry inspection workflow to confirm which imports are available in the environment. For backend connectivity and runtime health, use the checks documented by the selected component.

### Security and Resource Limits

Keep provider secrets in the application’s configuration and review each component’s documented permissions, limits, and failure behavior before using it with a backend.

### Compatibility

The namespace package documents Python 3.10, 3.11, 3.12, 3.13, and 3.14 support. Consult the individual distribution’s metadata for its Python and dependency constraints.

---

## Verification

### Tests

Run tests for the package you changed from the `pkgs/` workspace.

```bash
uv run --directory pkgs/80-facades/swarmauri --package swarmauri pytest
```

### Certification Status

The repository’s checks provide package-level test and compatibility evidence. See each distribution’s README for any certification it claims.

### Evidence

Use the package test suite to verify behavior in a source checkout. Distribution metadata and releases are available on PyPI, and repository workflow runs record automated checks. [Swarmauri on PyPI](https://pypi.org/project/swarmauri/) · [Repository workflows](https://github.com/swarmauri/swarmauri-sdk/actions)

---

## FAQ

### Why

**Why install the main package?** Install `swarmauri` when you want the public namespace, plugin discovery, and curated optional dependency groups. [Swarmauri on PyPI](https://pypi.org/project/swarmauri/)

### How

**How do I start writing a component?** Start with `swarmauri_core` for interfaces. Use `swarmauri_base` when the implementation needs serialization, component registration, or reusable base behavior. [Core on PyPI](https://pypi.org/project/swarmauri_core/) · [Base on PyPI](https://pypi.org/project/swarmauri_base/)

### When

**When should I install a component package?** Use `swarmauri_standard` for ready-to-use first-party components, or choose a focused community, plugin, or standards package for a specific provider or component kind. [Standard components on PyPI](https://pypi.org/project/swarmauri_standard/)

**Which Python versions can I use?** The documented range for the SDK workflows above is Python 3.10 through 3.14. See [Compatibility](#compatibility) for package-level constraints.

---

## Documentation and Related Packages

### More Documentation

- [Dynamic schemas guide](https://github.com/swarmauri/swarmauri-sdk/blob/b5fa8bbf1904b59f170f774f50936e728c69fb93/infra/docs/swarmauri-sdk/docs/guide/dynamic_schemas.md)
- [Swarmauri namespace call flow](pkgs/80-facades/swarmauri/docs/callflow.md)
- [Swarmauri citizenship notes](pkgs/80-facades/swarmauri/docs/citizenship.md)
- [Contribution guide](CONTRIBUTING.md)
- [Style guide](STYLE_GUIDE.md)
- [Package index](pkgs/PACKAGE_INDEX.md)

### Related Packages

**Security and signing packages**

- [swarmauri_signing_ed25519](https://pypi.org/project/swarmauri_signing_ed25519/)
- [swarmauri_signing_jws](https://pypi.org/project/swarmauri_signing_jws/)
- [swarmauri_crypto_composite](https://pypi.org/project/swarmauri_crypto_composite/)
- [swarmauri_keyprovider_inmemory](https://pypi.org/project/swarmauri_keyprovider_inmemory/)

**Runtime and infrastructure packages**

- [swarmauri_transport_stdio](https://pypi.org/project/swarmauri_transport_stdio/)
- [swarmauri_middleware_jsonrpc](https://pypi.org/project/swarmauri_middleware_jsonrpc/)
- [swarmauri_storage_memory](https://pypi.org/project/swarmauri_storage_memory/)

**Billing provider packages**

- [swarmauri_billing_adyen](https://pypi.org/project/swarmauri_billing_adyen/)
- [swarmauri_billing_authorize_net](https://pypi.org/project/swarmauri_billing_authorize_net/)
- [swarmauri_billing_braintree](https://pypi.org/project/swarmauri_billing_braintree/)
- [swarmauri_billing_paypal](https://pypi.org/project/swarmauri_billing_paypal/)
- [swarmauri_billing_stripe](https://pypi.org/project/swarmauri_billing_stripe/)

### Project Links

- [Source repository](https://github.com/swarmauri/swarmauri-sdk)
- [Issue tracker](https://github.com/swarmauri/swarmauri-sdk/issues)
- [Documentation site](https://docs.swarmauri.com/)
- [Discord](https://discord.gg/N4UpBuQv8T)

---

## Contributing

### How to Contribute

Open an issue for a bug or proposal. Include the affected distribution and a minimal example when reporting a bug. Follow the repository’s pull request guidance. [Contribution guide](CONTRIBUTING.md)

### Development Setup

Run formatting, linting, and tests for the affected workspace member. For example, to work on the namespace package, run these commands from the repository root.

```bash
uv run --directory pkgs/80-facades/swarmauri --package swarmauri ruff format .
uv run --directory pkgs/80-facades/swarmauri --package swarmauri ruff check . --fix
uv run --directory pkgs/80-facades/swarmauri --package swarmauri pytest
```

### Notes for Maintainers

Keep a component’s distribution metadata, installation instructions, usage examples, and entry point declarations aligned. When adding a workspace member, update the workspace configuration. [SDK Style Guide](STYLE_GUIDE.md)

---

## Governance

### Ownership and Decision Making

Repository code owners review changes through GitHub pull requests targeting `master`. [CODEOWNERS](.github/CODEOWNERS)

### Standards and Policies

Use the repository contribution guide and SDK style guide for code, tests, and packaging. The package README policy defines the required outline and checks for distributions. [Contribution guide](CONTRIBUTING.md) · [SDK Style Guide](STYLE_GUIDE.md) · [Package README policy](tools/readme/POLICY.md)

### Lifecycle and Migration

The package index distinguishes foundational packages, standard components, community integrations, plugins, standards-oriented implementations, and early-stage projects. Consult the relevant package README and release history for lifecycle and migration guidance. [Package index](pkgs/PACKAGE_INDEX.md)

---

## License and Attribution

### License

The Swarmauri SDK is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.

### Notices

See the license and attribution files shipped with each distribution for package-specific notices. [Repository license](LICENSE)
