![Swarmauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri/">
        <img src="https://img.shields.io/pypi/dm/swarmauri" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/"><img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk.svg"/></a>
    <a href="https://github.com/swarmauri/swarmauri-sdk">
        <img src="https://img.shields.io/github/repo-size/swarmauri/swarmauri-sdk" alt="GitHub Repo Size"/></a>
    <a href="https://pypi.org/project/swarmauri/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri/">
        <img src="https://img.shields.io/pypi/l/swarmauri" alt="PyPI - License"/></a>
    <br />
    <a href="https://pypi.org/project/swarmauri/">
        <img src="https://img.shields.io/pypi/v/swarmauri?label=swarmauri_core&color=green" alt="PyPI - swarmauri_core"/></a>
    <a href="https://pypi.org/project/swarmauri/">
        <img src="https://img.shields.io/pypi/v/swarmauri?label=swarmauri&color=green" alt="PyPI - swarmauri"/></a>
    <a href="https://pypi.org/project/swarmauri/">
        <img src="https://img.shields.io/pypi/v/swarmauri?label=swarmauri_community&color=yellow" alt="PyPI - swarmauri_community"/></a>
    <a href="https://pypi.org/project/swarmauri/">
        <img src="https://img.shields.io/pypi/v/swarmauri?label=swarmauri_experimental&color=yellow" alt="PyPI - swarmauri_experimental"/></a>
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
pip install swarmauri[full]
```

### Option 2: Core Only
For a minimal installation with just the core interfaces:

```bash
# Install only the core components
pip install swarmauri_core
```

### Option 3: Experimental Components

Add additional experimental components:
```bash

# Add experimental features (optional)
pip install swarmauri_experimental
```

### Option 4: Standalone Packages

Install specific packages for targeted functionality:

```bash
# Install only the vector store implementations you need
pip install swarmauri_vectorstore_pinecone
pip install swarmauri_vectorstore_annoy

# Install specific tools
pip install swarmauri_tool_jupyterexportlatex
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

### Method 1: Access via Namespace (Recommended)

The namespace approach provides a clean, unified interface to all components:
```python
# Import through the swarmauri namespace
from swarmauri.vectorstores import PineconeVectorStore, AnnoyVectorStore
from swarmauri.documents import Document
from swarmauri.tools import JupyterExportLatexTool

# Create a vector store
vector_store = PineconeVectorStore(
    api_key="your-api-key",
    environment="your-environment",
    index_name="your-index"
)

# Create a document
document = Document(
    content="Sample text content",
    metadata={"source": "example"}
)

# Add document to vector store
vector_store.add_document(document)

# Retrieve similar documents
results = vector_store.retrieve("query text", top_k=5)
```
### Method 2: Direct Package Access
For more explicit imports or when working with specific packages:

```python
# Import directly from individual packages
from swarmauri_vectorstore_pinecone import PineconeVectorStore
from swarmauri_standard.documents import Document
from swarmauri_tool_jupyterexportlatex import JupyterExportLatexTool

# Use components as before
vector_store = PineconeVectorStore(...)
```

## Package Structure
The Swarmauri SDK is organized into several key packages:

- `swarmauri_core`: Core interfaces and constants
- `swarmauri_base`: Abstract base classes for extensibility
- `swarmauri_standard`: Standard implementations of common components
- `swarmauri`: Main namespace package that unifies all components
- `swarmauri_experimental`: Experimental features under development

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


