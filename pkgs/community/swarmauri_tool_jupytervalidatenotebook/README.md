
![Swamauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_jupytervalidatenotebook/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_jupytervalidatenotebook" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupytervalidatenotebook/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupytervalidatenotebook.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupytervalidatenotebook/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_jupytervalidatenotebook" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupytervalidatenotebook/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_jupytervalidatenotebook" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupytervalidatenotebook/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_jupytervalidatenotebook?label=swarmauri_tool_jupytervalidatenotebook&color=green" alt="PyPI - swarmauri_tool_jupytervalidatenotebook"/></a>
</p>

---

# Swarmauri Tool Jupyter Validate Notebook

## Overview
This package provides a tool that validates a Jupyter notebook (NotebookNode) against its JSON schema using nbformat. It is useful for ensuring that your notebooks follow the correct structural and metadata standards required for processing or distribution. The tool can easily be integrated into automated workflows for CI/CD or general code validation processes.

## Installation

To install this package using pip:

    pip install swarmauri_tool_jupytervalidatenotebook

If you are using Poetry, you may add the following line to your pyproject.toml under [tool.poetry.dependencies]:

    swarmauri_tool_jupytervalidatenotebook = "*"

Then run:

    poetry install

Make sure that you have a supported version of Python (3.10+), together with the required dependencies as defined in the pyproject.toml (including nbformat, pydantic, typing_extensions, etc.).

## Usage

Below is a basic example of how to use the JupyterValidateNotebookTool to validate a notebook:

-------------------------------------------------------------------

import logging
import nbformat
from swarmauri_tool_jupytervalidatenotebook import JupyterValidateNotebookTool

def main():
    # Configure logging to see validation messages:
    logging.basicConfig(level=logging.INFO)

    # Create an instance of the validation tool
    validator = JupyterValidateNotebookTool()

    # Load a notebook for validation. Make sure the notebook is in the correct format (v4 typically).
    notebook = nbformat.read("my_notebook.ipynb", as_version=4)

    # Invoke the validator by calling the tool with the notebook object
    validation_result = validator(notebook)

    # Check the outcome
    if validation_result["valid"] == "True":
        print("Success:", validation_result["report"])
    else:
        print("Failure:", validation_result["report"])

if __name__ == "__main__":
    main()

-------------------------------------------------------------------

In this example:
• We import nbformat to read the notebook file into a NotebookNode object.  
• We instantiate JupyterValidateNotebookTool.  
• We pass our notebook to the tool, which will return a dictionary with "valid" and "report" keys.  
• We then inspect those keys to display the results of the validation procedure.

## Advanced Usage

You can further customize log handling or implement additional processing of the validation results to suit your workflow. For instance, you might collect statistics, filter notebooks based on validation success, or integrate the tool into multi-step pipelines.

Logging is handled by the Python logging library. For more production-focused scenarios, configure logging as needed to capture validation details, such as warnings or errors in your notebooks.  

Example with expanded logging:

-------------------------------------------------------------------

import logging
import nbformat
from swarmauri_tool_jupytervalidatenotebook import JupyterValidateNotebookTool

def validate_notebooks(notebook_paths):
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)
    validator = JupyterValidateNotebookTool()

    for path in notebook_paths:
        try:
            notebook = nbformat.read(path, as_version=4)
            result = validator(notebook)
            if result["valid"] == "True":
                logger.info(f"{path} passed validation. Details: {result['report']}")
            else:
                logger.warning(f"{path} failed validation. Error: {result['report']}")
        except FileNotFoundError:
            logger.error(f"Notebook file not found: {path}")

if __name__ == "__main__":
    notebooks_to_check = ["notebook1.ipynb", "notebook2.ipynb"]
    validate_notebooks(notebooks_to_check)

-------------------------------------------------------------------

The above approach allows you to queue multiple notebooks for validation, with clear logs about success/failure.  

## Dependencies

Key libraries and versions:
• Python >= 3.10,<3.13  
• nbformat  
• pydantic  
• typing_extensions  

For development, additional libraries such as pytest, flake8, and others may be included for testing and linting.  

## Versioning
The underlying version of this tool is managed by its own distribution metadata. You can retrieve the tool's version by referencing the __version__ attribute in the package (if installed from PyPI) or by checking the version field in the pyproject.toml file.

-------------------------------------------------------------------

For any issues, please consult the nbformat documentation to ensure your notebooks are well-formed. This tool primarily serves to confirm schema compliance, which is an essential first step in verifying proper notebook functionality in the broader Jupyter ecosystem.

Happy validating!
