
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_light_mg8cmd.png">
  <source media="(prefers-color-scheme: light)" srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
  <!-- Fallback below (see #2) -->
  <img alt="Swarmauri Logo" src="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
</picture>

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexecutenotebookwithparameters/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_jupyterexecutenotebookwithparameters" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterexecutenotebookwithparameters/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterexecutenotebookwithparameters.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexecutenotebookwithparameters/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_jupyterexecutenotebookwithparameters" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexecutenotebookwithparameters/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_jupyterexecutenotebookwithparameters" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexecutenotebookwithparameters/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_jupyterexecutenotebookwithparameters?label=swarmauri_tool_jupyterexecutenotebookwithparameters&color=green" alt="PyPI - swarmauri_tool_jupyterexecutenotebookwithparameters"/></a>
</p>

---

# Swarmauri Tool Jupyterexecutenotebookwithparameters

## Overview

This package provides a tool for executing Jupyter notebooks with custom parameters, leveraging the power of papermill. With the incorporated parameter injection, you can modify variables and data sources without manually editing your notebooks.

## Installation

This package is published on the Python Package Index (PyPI). You can install it with:

    pip install swarmauri_tool_jupyterexecutenotebookwithparameters

### Dependencies

• papermill  
• swarmauri_core >= 0.6.0.dev1  
• swarmauri_base >= 0.6.0.dev1  

These dependencies will be automatically installed when you install this package from PyPI.

## Usage

After installing, import the tool in your Python project:

    from swarmauri_tool_jupyterexecutenotebookwithparameters import JupyterExecuteNotebookWithParametersTool

### Basic Example

Create an instance of the tool and call it with the required arguments:

    # Example usage in a script or notebook

    # Instantiate the tool
    tool_instance = JupyterExecuteNotebookWithParametersTool()

    # Execute a Jupyter notebook
    result = tool_instance(
        notebook_path="example_notebook.ipynb",
        output_notebook_path="example_output.ipynb",
        params={
            "input_data_path": "data/input.csv",
            "run_mode": "production"
        }
    )

    # Check for success or error
    if "executed_notebook" in result:
        print(f"Notebook executed successfully. Output saved at: {result['executed_notebook']}")
    else:
        print(f"Error executing notebook: {result['error']}")

In this example:
• notebook_path points to the original .ipynb file.  
• output_notebook_path is the output file that papermill writes after parameter injection and execution.  
• params contains key-value pairs injected into the notebook as variables.

### Advanced Usage

• Catching Exceptions: The tool automatically returns a dictionary containing "error" if any exceptions occur during execution, allowing for programmatic error handling in CI/CD pipelines or other automated processes.  

• Parameter Injection: You can pass in any number of parameters to the params dictionary. For instance, toggling debug flags or updating dataset paths dynamically is straightforward with this mechanism.  

• Integration: This tool is designed to be used standalone or within the Swarmauri framework. When integrated into a pipeline, different notebooks can share the same or overridden parameter sets for consistent processing across multiple steps.  

---

## Further Development

This tool follows PEP 8 style guidelines, includes docstrings for all classes and methods, and utilizes type hints for better readability and maintainability. It’s designed to fit seamlessly into your Python projects, enabling powerful, parameterized notebook executions with minimal boilerplate.
