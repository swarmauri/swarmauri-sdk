
![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_jupyterwritenotebook/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_jupyterwritenotebook" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterwritenotebook/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterwritenotebook.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterwritenotebook/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_jupyterwritenotebook" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterwritenotebook/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_jupyterwritenotebook" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterwritenotebook/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_jupyterwritenotebook?label=swarmauri_tool_jupyterwritenotebook&color=green" alt="PyPI - swarmauri_tool_jupyterwritenotebook"/></a>
</p>

---

# Swarmauri Tool Jupyter Write NoteBook

The "swarmauri_tool_jupyterwritenotebook" package provides a tool that writes a Jupyter NotebookNode (or a dictionary structured like a NotebookNode) to a file in JSON format, preserving notebook structure. It comes as a fully functional component ready for integration in Python projects requiring automated notebook generation or manipulation.

## Installation

To install this package, make sure you have Python 3.10 or higher, then run:

• Using pip:  
  pip install swarmauri_tool_jupyterwritenotebook

• Using Poetry:  
  poetry add swarmauri_tool_jupyterwritenotebook

Once installation is complete, you can import and use the tool directly in your Python code.  

## Usage

Below is a step-by-step example showing how to use JupyterWriteNotebookTool to write a notebook to disk:

1. Import the required class:
   --------------------------------------------------------------------------------
   from swarmauri_tool_jupyterwritenotebook import JupyterWriteNotebookTool  

2. Initialize the tool:
   --------------------------------------------------------------------------------
   tool = JupyterWriteNotebookTool()

3. Prepare the notebook data as a dictionary. This can be a valid NotebookNode (like what nbformat produces) or a similarly structured Python dict:
   --------------------------------------------------------------------------------
   sample_notebook = {
       "cells": [
           {
               "cell_type": "markdown",
               "metadata": {},
               "source": [
                   "# Hello, Swarmauri!\n",
                   "This is a sample notebook cell."
               ]
           }
       ],
       "metadata": {
           "kernelspec": {
               "display_name": "Python 3",
               "language": "python",
               "name": "python3"
           },
           "language_info": {
               "name": "python"
           }
       },
       "nbformat": 4,
       "nbformat_minor": 5
   }

4. Call the tool by providing the dictionary (or NotebookNode) and the output file path:
   --------------------------------------------------------------------------------
   result = tool(
       notebook_data=sample_notebook,
       output_file="output_notebook.ipynb",
       encoding="utf-8"
   )
   print(result)

If the operation succeeds, "output_notebook.ipynb" will be created and populated with valid notebook JSON content. The returned dictionary may look like:
{
  "message": "Notebook written successfully",
  "file_path": "output_notebook.ipynb"
}

## Comprehensive Examples

• Basic Notebook Creation:  
  - You can create a minimal notebook dict with a single Markdown cell and save it.  
  - The returned information indicates whether the write was successful.

• Error Handling:  
  - If an error occurs (e.g., lack of file permissions, invalid notebook data), the tool returns a dictionary containing an "error" key with a descriptive message.

• Read-Back Verification:  
  - The tool attempts to reload the created file to ensure it was written correctly. If the read-back fails (e.g., empty or corrupted file), it returns a dictionary with an "error" key.

## Dependencies

The primary dependencies for "swarmauri_tool_jupyterwritenotebook" include:

• Python 3.10 or newer  
• nbformat for handling notebook structures  
• swarmauri_core and swarmauri_base for core functionality and base class definitions  

You will need these installed in your environment to use this package effectively. Other dev dependencies (such as pytest) are only necessary if you plan to run or extend the existing test suite.

---

© 2023 Swarmauri. Licensed under the Apache-2.0 License.
