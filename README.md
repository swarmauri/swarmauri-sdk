![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri/">
        <img src="https://img.shields.io/pypi/dm/swarmauri" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/swarmauri/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/swarmauri.svg"/></a>
    <a href="https://pypi.org/project/swarmauri/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri/">
        <img src="https://img.shields.io/pypi/l/swarmauri" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri/">
        <img src="https://img.shields.io/pypi/v/swarmauri?label=swarmauri&color=green" alt="PyPI - swarmauri"/></a>
</p>

---

# Swarmauri SDK

The Swarmauri SDK provides a powerful, extensible framework for building AI-powered applications. This repository includes core interfaces, standard abstract base classes, and concrete reference implementations.

## Installation Options

Swarmauri offers multiple installation options to suit different needs:

### Option 1: Complete SDK Installation

For a full-featured experience with all standard components:

```bash
# Install the main namespace package with standard components
pip install swarmauri

# Install the main namespace package with extra standard components
pip install "swarmauri[full]"

# Or with uv for faster installation
uv pip install swarmauri
uv pip install "swarmauri[full]"
```

### Option 2: Core Only
For a minimal installation with just the core interfaces:

```bash
# Install only the core components
pip install swarmauri_core

# Or with uv for faster installation
uv pip install swarmauri_core
```

### Option 3: Standalone Packages

Install specific packages for targeted functionality:

```bash
# Install only the vector store implementations you need
pip install swarmauri_vectorstore_pinecone
pip install swarmauri_vectorstore_annoy

# Install specific tools
pip install swarmauri_tool_jupyterexportlatex

# Or with uv for faster installation
uv pip install swarmauri_vectorstore_pinecone
uv pip install swarmauri_vectorstore_annoy
uv pip install swarmauri_tool_jupyterexportlatex
```

### Development Installation

For contributors or those wanting the latest features:
```bash
# Clone the repository
git clone https://github.com/swarmauri/swarmauri-sdk.git
cd swarmauri-sdk

# Install in development mode
pip install -e .

# Or with UV for faster installation
pip install uv
uv pip install -e .
```

## Using Swarmauri Components

### Method 1: Use the namespace package (recommended)

The `swarmauri` package acts as a namespace microkernel. Importing `swarmauri`
registers a custom importer that resolves classes from installed first-party and
community plugins.

```python
import swarmauri

# import concrete implementations through the unified namespace
from swarmauri.documents import Document
from swarmauri.tools import AdditionTool
from swarmauri.messages import HumanMessage

doc = Document(content="Hello from the namespace package")
tool = AdditionTool()
msg = HumanMessage(content="Run a quick tool check")

print(doc.type)
print(tool("2+2"))
print(msg.content)
```

### Method 2: Use the index to discover what is available

Use the plugin citizenship registry as an index of resource paths to concrete
module locations.

```python
from swarmauri.plugin_citizenship_registry import PluginCitizenshipRegistry

# Full index across first-, second-, and third-class plugins
index = PluginCitizenshipRegistry.total_registry()
print(f"Indexed resources: {len(index)}")

# Example: inspect a few tool entries
tool_rows = sorted(
    (resource, module)
    for resource, module in index.items()
    if resource.startswith("swarmauri.tools.")
)
for resource, module in tool_rows[:5]:
    print(f"{resource} -> {module}")

# Optional: inspect by citizenship class
first_class_only = PluginCitizenshipRegistry.list_registry("first")
print(f"First-class resources: {len(first_class_only)}")
```

### Method 3: Direct package imports

For explicit dependency control, import classes directly from their package.

```python
from swarmauri_standard.documents import Document
from swarmauri_standard.tools import AdditionTool

doc = Document(content="Direct package import")
tool = AdditionTool()
```

## Package Structure
The Swarmauri SDK is organized into several key packages:

- `swarmauri_core`: Core interfaces and constants
- `swarmauri_base`: Abstract base classes for extensibility
- `swarmauri_standard`: Standard implementations of common components
- `swarmauri`: Main namespace package that unifies all components
- `pkgs/community`: Community-maintained packages and integrations
- `pkgs/deprecated`: Retired packages that remain for historical reference

Individual components follow these naming conventions:

- `swarmauri_vectorstore_`*: Vector database integrations
- `swarmauri_embedding_`*: Embedding model implementations
- `swarmauri_tool_`*: Task-specific tools
- `swarmauri_parser_`*: Text parsing utilities
- `swarmauri_distance_`*: Distance calculation methods


## For Contributors
If you want to contribute to the Swarmauri SDK, please read our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md) and [style guide](https://github.com/swarmauri/swarmauri-sdk/blob/master/STYLE_GUIDE.md) to get started.

### Creating a New Plugin
Swarmauri uses Python's entry point system for plugin discovery. Here's how to register your component:

```python
# In your pyproject.toml
[project.entry-points.'swarmauri.vectorstores']
YourVectorStore = "swarmauri_vectorstore_yourplugin:YourVectorStore"

# In your implementation file
@ComponentBase.register_type(VectorStoreBase, "YourVectorStore")
class YourVectorStore(VectorStoreBase):
    # Your implementation
```

## License
The Swarmauri SDK is licensed under the Apache License 2.0. See the [LICENSE](https://github.com/swarmauri/swarmauri-sdk/blob/master/LICENSE) file for details.
