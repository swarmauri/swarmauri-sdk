
![Swamauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexportlatex/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_jupyterexportlatex" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterexportlatex/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterexportlatex.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexportlatex/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_jupyterexportlatex" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexportlatex/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_jupyterexportlatex" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexportlatex/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_jupyterexportlatex?label=swarmauri_tool_jupyterexportlatex&color=green" alt="PyPI - swarmauri_tool_jupyterexportlatex"/></a>
</p>

---

# Swarmauri Tool Jupyterexportlatex

A tool that exports a Jupyter Notebook to LaTeX format using nbconvert’s LatexExporter. This tool can optionally convert the produced LaTeX into PDF form, making it easy to prepare high-quality, publication-ready documents.

## Installation

This package requires Python 3.10 or above.

• To install from PyPI using pip:
  
  pip install swarmauri_tool_jupyterexportlatex

• Ensure that nbconvert is installed (it will be automatically installed with this package if you are using pip).

• This package also relies on the swarmauri_core and swarmauri_base packages, which are automatically installed when you install swarmauri_tool_jupyterexportlatex from PyPI.

Once installed, you will have access to the JupyterExportLatexTool class, which provides a straightforward way to convert your NotebookNode objects into LaTeX or PDF.

## Usage

1. Import the tool into your Python script or Jupyter notebook:
   
   from swarmauri_tool_jupyterexportlatex import JupyterExportLatexTool

2. Construct an instance of the tool:
   
   tool = JupyterExportLatexTool()

3. Provide a valid nbformat.NotebookNode object alongside optional parameters:
   
   output = tool(
       notebook_node,
       use_custom_template=False,
       template_path=None,
       to_pdf=True
   )

   Here:
   • notebook_node: a valid nbformat.NotebookNode object representing your Jupyter notebook.
   • use_custom_template (bool): set to True if you have a custom LaTeX template file.
   • template_path (str): an optional custom LaTeX template path if use_custom_template is True.
   • to_pdf (bool): set to True if you want to generate a PDF in addition to the LaTeX output.

4. Handling the return structure:
   
   The method returns a dictionary which may contain:
   • "latex_content": The LaTeX output string.
   • "pdf_file_path": A temporary path to the generated PDF if to_pdf=True.
   • "error": An error message if any exception occurred during export.

### Example

Suppose you already have a loaded NotebookNode object named my_notebook:

from nbformat import read
import io

# Pretend we have notebook data in 'notebook_str'
notebook_str = """{ "cells": [], "metadata": {}, "nbformat": 4, "nbformat_minor": 5 }"""
my_notebook = read(io.StringIO(notebook_str), as_version=4)

tool = JupyterExportLatexTool()
export_result = tool(my_notebook, to_pdf=True)

if "error" in export_result:
    print("Error:", export_result["error"])
else:
    latex_content = export_result.get("latex_content", "")
    print("LaTeX content:\n", latex_content)
    pdf_path = export_result.get("pdf_file_path")
    if pdf_path:
        print("PDF was successfully generated at:", pdf_path)

---

## Dependencies

Below are the main files that comprise this package:

### pkgs/swarmauri_tool_jupyterexportlatex/swarmauri_tool_jupyterexportlatex/JupyterExportLatexTool.py
```
"""
JupyterExportLatexTool.py

This module defines the JupyterExportLatexTool, a component that converts Jupyter notebooks
(NotebookNode objects) into LaTeX format. It supports custom LaTeX templates, logs the export
process, handles conversion errors, and can optionally produce a PDF. This tool is designed
to meet academic publication standards.
"""

from typing import List, Literal, Dict, Any, Optional
from pydantic import Field
from nbformat import NotebookNode
from nbconvert import LatexExporter, PDFExporter
from nbconvert.writers import FilesWriter
import os
import tempfile

from swarmauri_standard.tools.Parameter import Parameter
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_core.ComponentBase import ComponentBase


@ComponentBase.register_type(ToolBase, 'JupyterExportLatexTool')
class JupyterExportLatexTool(ToolBase):
    """
    JupyterExportLatexTool is responsible for converting a Jupyter Notebook (NotebookNode)
    into a LaTeX document. It supports using a custom LaTeX template, can log and handle
    conversion errors, and optionally convert the generated LaTeX to PDF.

    Attributes:
        version (str): The version of the JupyterExportLatexTool.
        parameters (List[Parameter]): A list of parameters required to perform the export.
        name (str): The name of the tool.
        description (str): A brief description of the tool's functionality.
        type (Literal["JupyterExportLatexTool"]): The type identifier for the tool.
    """
    version: str = "0.1.0"
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="notebook_node",
                type="object",
                description="A nbformat.NotebookNode object representing a Jupyter notebook.",
                required=True
            ),
            Parameter(
                name="use_custom_template",
                type="boolean",
                description="Whether or not to use a custom LaTeX template.",
                required=False
            ),
            Parameter(
                name="template_path",
                type="string",
                description="Path to a custom LaTeX template if use_custom_template is True.",
                required=False
            ),
            Parameter(
                name="to_pdf",
                type="boolean",
                description="If True, also convert the LaTeX output to PDF.",
                required=False
            ),
        ]
    )
    name: str = "JupyterExportLatexTool"
    description: str = "Converts Jupyter notebooks to LaTeX and optionally to PDF for academic publication."
    type: Literal["JupyterExportLatexTool"] = "JupyterExportLatexTool"

    def __call__(
        self,
        notebook_node: NotebookNode,
        use_custom_template: bool = False,
        template_path: Optional[str] = None,
        to_pdf: bool = False
    ) -> Dict[str, Any]:
        """
        Converts a Jupyter notebook (NotebookNode) into LaTeX format, optionally using a
        custom template, and returns the resulting LaTeX content. This method can also
        generate a PDF version if requested.

        Args:
            notebook_node (NotebookNode): The Jupyter NotebookNode to convert.
            use_custom_template (bool, optional): Whether to apply a custom LaTeX template.
            template_path (str, optional): Custom template path if use_custom_template is True.
            to_pdf (bool, optional): If True, the method will also convert the LaTeX to a PDF file.

        Returns:
            Dict[str, Any]: A dictionary containing:
                - "latex_content": The generated LaTeX content as a string.
                - "pdf_file_path": The file path to the generated PDF if to_pdf is True.
                - "error": An error message if any exception occurred.

        Example:
            >>> tool = JupyterExportLatexTool()
            >>> latex_output = tool(notebook_node, False, None, False)
            >>> print(latex_output["latex_content"])
        """
        try:
            # Create the LaTeX exporter
            latex_exporter = LatexExporter()
            if use_custom_template and template_path:
                latex_exporter.template_file = template_path

            # Convert the notebook to LaTeX
            body, _ = latex_exporter.from_notebook_node(notebook_node)

            result: Dict[str, Any] = {"latex_content": body}

            # If user requested PDF export, attempt to convert the LaTeX to PDF
            if to_pdf:
                pdf_exporter = PDFExporter()
                if use_custom_template and template_path:
                    pdf_exporter.template_file = template_path

                # Use a temporary directory for PDF conversion
                with tempfile.TemporaryDirectory() as temp_dir:
                    pdf_exporter.output_filename = "converted_notebook.pdf"
                    pdf_data, _ = pdf_exporter.from_notebook_node(notebook_node)

                    # Write the PDF file to disk
                    writer = FilesWriter(build_directory=temp_dir)
                    writer.write(pdf_data, pdf_exporter.output_filename)

                    pdf_path = os.path.join(temp_dir, pdf_exporter.output_filename)

                    result["pdf_file_path"] = pdf_path

            return result
        except Exception as e:
            return {"error": f"An error occurred during LaTeX export: {str(e)}"}

```

### pkgs/swarmauri_tool_jupyterexportlatex/swarmauri_tool_jupyterexportlatex/__init__.py
```
from swarmauri_tool_jupyterexportlatex.JupyterExportLatexTool import JupyterExportLatexTool


__all__ = [ "JupyterExportLatexTool" ]

try:
    # For Python 3.8 and newer
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    # For older Python versions, use the backport
    from importlib_metadata import version, PackageNotFoundError

try:
    __version__ = version("swarmauri_tool_jupyterexportlatex")
except PackageNotFoundError:
    # If the package is not installed (for example, during development)
    __version__ = "0.0.0"

```

### pkgs/swarmauri_tool_jupyterexportlatex/pyproject.toml
```
[tool.poetry]
name = "swarmauri_tool_jupyterexportlatex"
version = "0.6.1.dev7"
description = "A tool that exports a Jupyter Notebook to LaTeX format using nbconvert’s LatexExporter, enabling further conversion to PDF."
authors = ["Jacob Stewart <jacob@swarmauri.com>"]
license = "Apache-2.0"
readme = "README.md"
repository = "https://github.com/swarmauri/swarmauri-sdk/tree/mono/dev/pkgs/swarmauri_tool_jupyterexportlatex/"
classifiers = [
    "License :: OSI Approved :: Apache Software License",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13"
]

[tool.poetry.dependencies]
python = ">=3.10,<3.13"

# Swarmauri repositories
swarmauri_core = { git = "https://github.com/swarmauri/swarmauri-sdk.git", branch = "mono/dev", subdirectory = "pkgs/core" }
swarmauri_base = { git = "https://github.com/swarmauri/swarmauri-sdk.git", branch = "mono/dev", subdirectory = "pkgs/base" }
swarmauri_standard = { git = "https://github.com/swarmauri/swarmauri-sdk.git", branch = "mono/dev", subdirectory = "pkgs/swarmauri_standard" }

# Dependencies
nbconvert = "*"

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
jupyterexportlatextool = "swarmauri_tool_jupyterexportlatex:JupyterExportLatexTool"

```

## License

Apache 2.0

---

Feel free to explore the provided examples and code to see how you can tailor the export of your Jupyter notebooks for academic publications, internal documentation, or any other use case that requires a clean LaTeX output.
