
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_light_mg8cmd.png">
  <source media="(prefers-color-scheme: light)" srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
  <!-- Fallback below (see #2) -->
  <img alt="Swarmauri Logo" src="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
</picture>

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexportpython/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_jupyterexportpython" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterexportpython/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterexportpython.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexportpython/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_jupyterexportpython" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexportpython/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_jupyterexportpython" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexportpython/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_jupyterexportpython?label=swarmauri_tool_jupyterexportpython&color=green" alt="PyPI - swarmauri_tool_jupyterexportpython"/></a>
</p>

---

# Swarmauri Tool Jupyter Export Python

A Python package that provides an easy way to export Jupyter Notebook files to Python scripts using the nbconvert library. This tool smoothly integrates with the Swarmauri tool architecture, enabling consistent logging, error handling, and flexible usage options.

## Installation

swarmauri_tool_jupyterexportpython requires Python 3.10 or higher, along with nbconvert. The easiest way to install it is via PyPI:

1. Make sure you have Python 3.10 or newer.
2. Install the package using pip:

    pip install swarmauri_tool_jupyterexportpython

Or, if you’re using Poetry for your project:

    poetry add swarmauri_tool_jupyterexportpython

This will automatically install the required dependencies, including nbconvert. Because swarmauri_tool_jupyterexportpython is part of the Swarmauri ecosystem, you may also want to ensure you have a compatible version of the “swarmauri_base” and “swarmauri_core” libraries installed.

Once installed, you will have access to the JupyterExportPythonTool class, which can export your notebooks to Python scripts with optional custom templates.

## Usage

Below is a description of how to use the JupyterExportPythonTool in your Python code. For example, you can create an instance of the tool, then call it with your Jupyter notebook object (NotebookNode) and optional template path.

### Simple Example

----------------------------------
from nbformat import read, NO_CONVERT
from swarmauri_tool_jupyterexportpython import JupyterExportPythonTool

# Suppose you've loaded a Jupyter notebook file.

def load_notebook(file_path: str):
    """
    Helper function to load a local .ipynb file into a NotebookNode object.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        notebook_node = read(f, NO_CONVERT)
    return notebook_node

def main():
    # Instantiate an instance of the JupyterExportPythonTool
    export_tool = JupyterExportPythonTool()

    # Load a notebook from file
    nb_node = load_notebook("example_notebook.ipynb")

    # Call the tool to export the notebook to a Python script
    result = export_tool(nb_node)

    if 'exported_script' in result:
        # Write the exported Python script to a file or process it as required
        with open("output_script.py", "w", encoding="utf-8") as file_out:
            file_out.write(result['exported_script'])
        print("Notebook was successfully exported to output_script.py!")
    else:
        # If there's an error, it's included in result['error']
        print(f"Failed to export notebook: {result['error']}")

if __name__ == "__main__":
    main()
----------------------------------

### Advanced Example (Using a Custom Template)

----------------------------------
from nbformat import read, NO_CONVERT
from swarmauri_tool_jupyterexportpython import JupyterExportPythonTool

def load_notebook(file_path: str):
    """
    Helper function to load a local .ipynb file into a NotebookNode object.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        notebook_node = read(f, NO_CONVERT)
    return notebook_node

def main():
    # Instantiate the export tool
    export_tool = JupyterExportPythonTool()

    # Load a notebook from file
    nb_node = load_notebook("example_with_template.ipynb")

    # Specify a custom template to control the structure of the exported script
    custom_template_path = "templates/my_python_export_template.tpl"

    # Call the tool with the custom template
    result = export_tool(nb_node, template_file=custom_template_path)

    if 'exported_script' in result:
        # Write to a file
        with open("custom_export_script.py", "w", encoding="utf-8") as script_file:
            script_file.write(result['exported_script'])
        print("Notebook exported using a custom template!")
    else:
        print(f"Failed to export notebook with template: {result['error']}")

if __name__ == "__main__":
    main()
----------------------------------

In both examples above, JupyterExportPythonTool converts the notebook to a string containing valid Python source code. You can do additional processing on this code before writing it to a file.

## Dependencies

This package has the following primary dependencies:

• nbconvert: used for converting Jupyter Notebook files to Python scripts  
• swarmauri_core: provides shared base classes and decorators in the Swarmauri ecosystem  
• swarmauri_base: provides additional helpful classes and structures required by tools  

You must have Python ≥3.10,<3.13 installed to ensure compatibility with these libraries.

## Contributing

We welcome improvements and suggestions via normal development workflows. While this README is focused on helping you get the tools running smoothly, feel free to explore the code and contribute to its development. We recommend using a consistent code style and testing any modifications thoroughly prior to deployment.

---

© 2023 Swarmauri Inc. All rights reserved. Licensed under the Apache License, Version 2.0.  
For more information and usage examples, explore our official documentation or see our other Swarmauri packages.
