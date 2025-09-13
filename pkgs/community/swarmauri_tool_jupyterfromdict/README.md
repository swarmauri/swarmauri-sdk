
![Swamauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_jupyterfromdict/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_jupyterfromdict" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterfromdict/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterfromdict.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterfromdict/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_jupyterfromdict" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterfromdict/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_jupyterfromdict" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterfromdict/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_jupyterfromdict?label=swarmauri_tool_jupyterfromdict&color=green" alt="PyPI - swarmauri_tool_jupyterfromdict"/></a>
</p>

---

# Swarmauri Tool Jupyter From Dict

swarmauri_tool_jupyterfromdict provides a straightforward way to convert a Python dictionary into a validated Jupyter NotebookNode using nbformat. This allows programmatic creation and manipulation of notebook structures within the Swarmauri framework or your own applications.

## Installation

To install swarmauri_tool_jupyterfromdict, simply use pip:

    pip install swarmauri_tool_jupyterfromdict

You may also use Poetry by adding the following to your pyproject.toml:

    [tool.poetry.dependencies]
    swarmauri_tool_jupyterfromdict = "*"

Once installed, you can import and use JupyterFromDictTool in your Python code.

## Usage

Below is an example demonstrating how you might use JupyterFromDictTool to convert a Python dictionary into a valid notebook object. This can be especially useful for dynamically generating Jupyter notebooks in automated pipelines, educational material generation, or data science workflows.

Example usage in a Python script or notebook:

```python
from swarmauri_tool_jupyterfromdict import JupyterFromDictTool

# Create an instance of the tool
jupyter_tool = JupyterFromDictTool()

# Define a dictionary representing a very basic Jupyter notebook
notebook_dict = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {},
    "cells": [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["# Hello World\n", "This is a sample notebook created from a dictionary."]
        }
    ]
}

# Invoke the tool to convert the dictionary to a NotebookNode
result = jupyter_tool(notebook_dict)

if "notebook_node" in result:
    notebook_node = result["notebook_node"]
    # Do something with notebook_node, such as writing it to disk or processing further
    print("NotebookNode created successfully:", notebook_node)
else:
    # If there's an error, the dictionary will contain an 'error' key
    print("An error occurred:", result["error"])
```

The result can then be further manipulated using nbformat’s capabilities or saved as a .ipynb file.

---

### Dependencies

Below are the key source files in this package with their complete implementations.

#### `pkgs/swarmauri_tool_jupyterfromdict/swarmauri_tool_jupyterfromdict/JupyterFromDictTool.py`
```python
"""
JupyterFromDictTool.py

This module defines the JupyterFromDictTool, a component that takes a dictionary representing
a Jupyter notebook structure and converts it into a validated NotebookNode. It provides logging
throughout the conversion process and gracefully handles errors.
"""

import logging
from typing import List, Dict, Union, Literal
from pydantic import Field
from nbformat import from_dict, validate, NotebookNode, ValidationError

from swarmauri_standard.tools.Parameter import Parameter
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_core.ComponentBase import ComponentBase

logger = logging.getLogger(__name__)

@ComponentBase.register_type(ToolBase, "JupyterFromDictTool")
class JupyterFromDictTool(ToolBase):
    """
    JupyterFromDictTool is a tool that converts a dictionary representing a Jupyter notebook
    into a validated NotebookNode object. It inherits from ToolBase and integrates with the
    swarmauri framework, allowing the conversion process to be easily reused within the system.

    Attributes:
        version (str): The version of the JupyterFromDictTool.
        parameters (List[Parameter]): A list of parameters required for tool invocation.
        name (str): The name of the tool.
        description (str): A brief description of the tool's functionality.
        type (Literal["JupyterFromDictTool"]): The type identifier for the tool.
    """
    version: str = "1.0.0"
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="notebook_dict",
                type="object",
                description="The dictionary representing the notebook structure.",
                required=True,
            )
        ]
    )
    name: str = "JupyterFromDictTool"
    description: str = "Converts a dictionary into a validated Jupyter NotebookNode."
    type: Literal["JupyterFromDictTool"] = "JupyterFromDictTool"

    def __call__(self, notebook_dict: Dict) -> Dict[str, Union[str, NotebookNode]]:
        """
        Converts the provided dictionary into a NotebookNode, validates it against the nbformat
        schema, and returns the resulting NotebookNode in a dictionary response.

        Args:
            notebook_dict (Dict): The dictionary containing notebook structure.

        Returns:
            Dict[str, Union[str, NotebookNode]]: A dictionary containing either the validated
            NotebookNode or an error message indicating what went wrong during the conversion.

        Example:
            >>> jupyter_tool = JupyterFromDictTool()
            >>> notebook_example = {
            ...     "nbformat": 4,
            ...     "nbformat_minor": 5,
            ...     "cells": [],
            ...     "metadata": {}
            ... }
            >>> result = jupyter_tool(notebook_example)
            {
              'notebook_node': NotebookNode(nbformat=4, nbformat_minor=5, cells=[], metadata={})
            }
        """
        try:
            logger.info("Starting conversion from dictionary to NotebookNode.")
            notebook_node: NotebookNode = from_dict(notebook_dict)
            logger.info("NotebookNode created. Validating NotebookNode.")
            validate(notebook_node)
            logger.info("NotebookNode validation successful.")
            return {"notebook_node": notebook_node}
        except ValidationError as ve:
            logger.error(f"NotebookNode validation error: {ve}")
            return {"error": f"NotebookNode validation error: {str(ve)}"}
        except Exception as e:
            logger.error(f"Failed to convert dictionary to NotebookNode: {e}")
            return {"error": f"An error occurred: {str(e)}"}
```

#### `pkgs/swarmauri_tool_jupyterfromdict/swarmauri_tool_jupyterfromdict/__init__.py`
```python
from swarmauri_tool_jupyterfromdict.JupyterFromDictTool import JupyterFromDictTool


__all__ = [ "JupyterFromDictTool" ]

try:
    # For Python 3.8 and newer
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    # For older Python versions, use the backport
    from importlib_metadata import version, PackageNotFoundError

try:
    __version__ = version("swarmauri_tool_jupyterfromdict")
except PackageNotFoundError:
    # If the package is not installed (for example, during development)
    __version__ = "0.0.0"
```

#### `pkgs/swarmauri_tool_jupyterfromdict/pyproject.toml`
```toml
[tool.poetry]
name = "swarmauri_tool_jupyterfromdict"
version = "0.6.1.dev7"
description = "A tool that converts a plain dictionary into a NotebookNode object using nbformat, facilitating programmatic notebook creation."
authors = ["Jacob Stewart <jacob@swarmauri.com>"]
license = "Apache-2.0"
readme = "README.md"
repository = "http://github.com/swarmauri/swarmauri-sdk/pkgs/community/swarmauri_tool_jupyterfromdict/"
classifiers = [
    "License :: OSI Approved :: Apache Software License",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13"
]

[tool.poetry.dependencies]
python = ">=3.10,<3.13"

# Swarmauri
swarmauri_core = { git = "https://github.com/swarmauri/swarmauri-sdk.git", branch = "mono/dev", subdirectory = "pkgs/core"}
swarmauri_base = { git = "https://github.com/swarmauri/swarmauri-sdk.git", branch = "mono/dev", subdirectory = "pkgs/base"}
swarmauri_standard = { git = "https://github.com/swarmauri/swarmauri-sdk.git", branch = "mono/dev", subdirectory = "pkgs/swarmauri_standard" }

# Dependencies
nbformat = "*"

[tool.poetry.group.dev.dependencies]
flake8 = "^7.0"
pytest = "^8.0"
pytest-asyncio = ">=0.24.0"
pytest-xdist = "^3.6.1"
pytest-json-report = "^1.5.0"
python-dotenv = "*"
requests = "^2.32.3"

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"

[tool.pytest.ini_options]
markers = [
    "test: standard test",
    "unit: Unit tests",
    "i9n: Integration tests",
    "acceptance: Acceptance tests",
    "experimental: Experimental tests"
]
log_cli = true
log_cli_level = "INFO"
log_cli_format = "%(asctime)s [%(levelname)s] %(message)s"
log_cli_date_format = "%Y-%m-%d %H:%M:%S"
asyncio_default_fixture_loop_scope = "function"

[tool.poetry.plugins."swarmauri.tools"]
jupyterfromdicttool = "swarmauri_tool_jupyterfromdict:JupyterFromDictTool"
```

---

We hope you find swarmauri_tool_jupyterfromdict useful in your pipeline. If you have any questions or issues, please file a report or reach out to your Swarmauri representative. Thank you for using Swarmauri to power your notebook automation!
