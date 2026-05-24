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

# Swarmauri SDK

Swarmauri is a composable intelligence infrastructure SDK for building typed, pluggable Python systems. The repository contains the public `swarmauri` namespace package, interface contracts, reusable base classes, standard components, community integrations, plugin packages, and package-level documentation for independently installable Swarmauri distributions.

## Why Swarmauri?

Swarmauri separates component contracts from implementations so applications can compose agents, tools, models, parsers, vector stores, signing components, key providers, transports, middleware, billing providers, and storage adapters without locking every workflow to one provider package. The namespace package gives users stable imports while individual packages keep dependencies focused.

## FAQ

### Q: What is the main package to install?

A: Install [swarmauri](https://pypi.org/project/swarmauri/) when you want the public namespace, plugin discovery, and curated optional dependency groups.

### Q: Which package should component authors start with?

A: Start with [swarmauri_core](https://pypi.org/project/swarmauri_core/) for interfaces, then use [swarmauri_base](https://pypi.org/project/swarmauri_base/) when the implementation needs serialization, component registration, and reusable base behavior.

### Q: Where are ready-to-use components?

A: Use [swarmauri_standard](https://pypi.org/project/swarmauri_standard/) for first-party standard components, or install a focused community, plugin, or standards package for a specific provider or component kind.

### Q: Does this repository support modern Python versions?

A: Swarmauri package metadata and badges target Python 3.10, 3.11, 3.12, 3.13, and 3.14.

## Features

- Stable `swarmauri.*` namespace imports through the namespace package.
- Interface-first package architecture through `swarmauri_core`.
- Pydantic-backed base classes, serialization helpers, and dynamic component registration through `swarmauri_base`.
- First-party standard components through `swarmauri_standard`.
- Independently installable community, plugin, experimental, and standards packages.
- Component families for agents, chains, conversations, documents, embeddings, LLMs, parsers, prompts, schema converters, tools, toolkits, vector stores, signing, crypto, key providers, transports, middleware, storage, XMP, billing, and more.
- Python 3.10, 3.11, 3.12, 3.13, and 3.14 support.

## Installation

Install the namespace package with `uv`:

```bash
uv add swarmauri
```

Install it with `pip`:

```bash
pip install swarmauri
```

Install the broader curated component bundle:

```bash
uv add "swarmauri[full]"
pip install "swarmauri[full]"
```

Install only foundational packages when building components:

```bash
uv add swarmauri_core swarmauri_base
pip install swarmauri_core swarmauri_base
```

Install focused packages when you only need one component family:

```bash
uv add swarmauri_vectorstore_pinecone
uv add swarmauri_tool_jupyterexportlatex
uv add swarmauri_signing_ed25519
```

## Usage

Importing `swarmauri` activates namespace discovery for installed components:

```python
import swarmauri

from swarmauri.interface_registry import InterfaceRegistry
from swarmauri.plugin_citizenship_registry import PluginCitizenshipRegistry

print(len(InterfaceRegistry.list_registered_namespaces()))
print(len(PluginCitizenshipRegistry.total_registry()))
```

Use the namespace package for stable public imports after the implementation package is installed:

```python
import swarmauri

from swarmauri.signings.Ed25519EnvelopeSigner import Ed25519EnvelopeSigner

signer = Ed25519EnvelopeSigner()
print(signer.type)
```

Use direct package imports when you want the narrowest dependency surface:

```python
from swarmauri_standard.documents import Document
from swarmauri_standard.tools import AdditionTool

doc = Document(content="Direct package import")
tool = AdditionTool()

print(doc.type)
print(tool("2+2"))
```

## Examples

Discover registered component mappings:

```python
from swarmauri.plugin_citizenship_registry import PluginCitizenshipRegistry

for public_path, module_path in list(PluginCitizenshipRegistry.total_registry().items())[:10]:
    print(public_path, "->", module_path)
```

Use dynamic component serialization from `swarmauri_base`:

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

## Package Structure

Foundational packages:

- [swarmauri](https://pypi.org/project/swarmauri/) provides the namespace importer and plugin discovery layer.
- [swarmauri_core](https://pypi.org/project/swarmauri_core/) provides interface contracts and shared types.
- [swarmauri_base](https://pypi.org/project/swarmauri_base/) provides reusable base classes, serialization helpers, and component registration behavior.
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/) provides first-party standard components.
- [swarmauri_typing](https://pypi.org/project/swarmauri_typing/) provides dynamic typing utilities used by Swarmauri base classes.

Repository package areas:

- `pkgs/core`, `pkgs/base`, `pkgs/typing`, and `pkgs/swarmauri` contain foundational packages.
- `pkgs/swarmauri_standard` contains first-party standard components.
- `pkgs/community` contains community-maintained packages and provider integrations.
- `pkgs/plugins` contains plugin packages.
- `pkgs/standards` contains standard-interface and standards-oriented packages.
- `pkgs/experimental` contains early-stage packages.

Common package families:

- `swarmauri_vectorstore_*` packages provide vector database integrations.
- `swarmauri_embedding_*` packages provide embedding model integrations.
- `swarmauri_tool_*` packages provide task-specific tools.
- `swarmauri_parser_*` packages provide parsing utilities.
- `swarmauri_signing_*` packages provide signing implementations.
- `swarmauri_keyprovider_*` packages provide key-management implementations.
- `swarmauri_billing_*` packages provide billing provider implementations and stubs.

## Related Packages

Security and signing packages:

- [swarmauri_signing_ed25519](https://pypi.org/project/swarmauri_signing_ed25519/)
- [swarmauri_signing_jws](https://pypi.org/project/swarmauri_signing_jws/)
- [swarmauri_crypto_composite](https://pypi.org/project/swarmauri_crypto_composite/)
- [swarmauri_keyprovider_inmemory](https://pypi.org/project/swarmauri_keyprovider_inmemory/)

Runtime and infrastructure packages:

- [swarmauri_transport_stdio](https://pypi.org/project/swarmauri_transport_stdio/)
- [swarmauri_middleware_jsonrpc](https://pypi.org/project/swarmauri_middleware_jsonrpc/)
- [swarmauri_storage_memory](https://pypi.org/project/swarmauri_storage_memory/)

Billing provider packages:

- [swarmauri_billing_adyen](https://pypi.org/project/swarmauri_billing_adyen/)
- [swarmauri_billing_authorize_net](https://pypi.org/project/swarmauri_billing_authorize_net/)
- [swarmauri_billing_braintree](https://pypi.org/project/swarmauri_billing_braintree/)
- [swarmauri_billing_paypal](https://pypi.org/project/swarmauri_billing_paypal/)
- [swarmauri_billing_stripe](https://pypi.org/project/swarmauri_billing_stripe/)

## Documentation

- [Dynamic schemas guide](infra/docs/swarmauri-sdk/docs/guide/dynamic_schemas.md)
- [Swarmauri namespace call flow](pkgs/swarmauri/docs/callflow.md)
- [Swarmauri citizenship notes](pkgs/swarmauri/docs/citizenship.md)
- [Contribution guide](CONTRIBUTING.md)
- [Style guide](STYLE_GUIDE.md)
- [Package index](pkgs/)

## For Contributors

Create component packages with direct instantiation in mind. Plugins should expose clear package-level imports, use the relevant `swarmauri_core` interface and `swarmauri_base` base class, document installation and usage, and register entry points where namespace discovery is expected.

```toml
[project.entry-points.'swarmauri.vectorstores']
YourVectorStore = "swarmauri_vectorstore_yourplugin:YourVectorStore"
```

```python
from typing import Literal

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.vector_stores.VectorStoreBase import VectorStoreBase


@ComponentBase.register_type(VectorStoreBase, "YourVectorStore")
class YourVectorStore(VectorStoreBase):
    type: Literal["YourVectorStore"] = "YourVectorStore"
```

## License

The Swarmauri SDK is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.



