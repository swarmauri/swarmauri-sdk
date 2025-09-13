
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_light_mg8cmd.png">
  <source media="(prefers-color-scheme: light)" srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
  <!-- Fallback below (see #2) -->
  <img alt="Swarmauri Logo" src="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
</picture>

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexporthtml/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_jupyterexporthtml" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterexporthtml/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterexporthtml.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexporthtml/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_jupyterexporthtml" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexporthtml/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_jupyterexporthtml" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexporthtml/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_jupyterexporthtml?label=swarmauri_tool_jupyterexporthtml&color=green" alt="PyPI - swarmauri_tool_jupyterexporthtml"/></a>
</p>

---

# Swarmauri Tool Jupyter Export Html

The purpose of this package is to provide a flexible tool for converting Jupyter Notebook content into HTML format using nbconvert’s HTMLExporter. This enables easy presentation, sharing, or embedding of Jupyter Notebook content into various workflows or web applications.

## Installation

Since this package is published for Python 3.10 to 3.13, you will need a recent version of Python. To install:

1. Ensure you have the required dependencies, including nbconvert, installed.  
2. Run the following command in your preferred Python environment to install from PyPI:

   pip install swarmauri_tool_jupyterexporthtml

3. You’re ready to begin using the JupyterExportHTMLTool in your projects.

### Dependencies
• nbconvert (for converting Notebook content into HTML)  
• swarmauri_core, swarmauri_base (for Swarmauri framework integration)

These are automatically installed when you install this package.

## Usage 

Below is a short guide showing how to import and use the tool in your own Python code. The JupyterExportHTMLTool accepts a JSON-formatted string representing the notebook data, plus optional template, CSS, and JavaScript parameters.

Example usage:

--------------------------------------------------------------------------------

from swarmauri_tool_jupyterexporthtml import JupyterExportHTMLTool

# Example Notebook JSON (this would typically be read from a file or other source)
notebook_json_str = '''
{
    "cells": [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# Hello World\\n",
                "This is a sample notebook cell."
            ]
        }
    ],
    "metadata": {},
    "nbformat": 4,
    "nbformat_minor": 5
}
'''

# Create an instance of the exporter
exporter = JupyterExportHTMLTool()

# Call the exporter with optional parameters
result = exporter(
    notebook_json=notebook_json_str,
    template_file=None,  # or specify a path to a custom template
    extra_css="body { font-family: Arial, sans-serif; }",
    extra_js="console.log('HTML Export Ready!');"
)

# Check for success
if "exported_html" in result:
    # Save or process the HTML output
    html_content = result["exported_html"]
    print("Notebook conversion to HTML was successful. Length of output:", len(html_content))
else:
    # Handle any error messages
    print("Error during export:", result.get("error"))

--------------------------------------------------------------------------------

### Method Summary

The JupyterExportHTMLTool class implements a callable interface, expecting parameters such as:  
• notebook_json (required): A string containing Jupyter Notebook data in valid JSON format.  
• template_file (optional): Path to an nbconvert-compatible template.  
• extra_css (optional): Inline styles you wish to embed into the resulting HTML.  
• extra_js (optional): Inline JavaScript you wish to embed before the closing body tag.  

It returns a dictionary containing either “exported_html” with the final HTML string or “error” with a message describing any failure.

## Advanced Usage

Use a custom template to further influence how the notebook is rendered. For instance, with an nbconvert template:

result = exporter(
    notebook_json=notebook_json_str,
    template_file="custom_template.tpl",
    extra_css="header { color: blue; }",
    extra_js="alert('Notebook Conversion Complete!');"
)

The extra_css parameter is injected inside a <style> tag, and extra_js is injected in a <script> tag at the end of the file. This allows you to easily tailor styling or behavior without manually editing the exported HTML.

--------------------------------------------------------------------------------

For further details, please refer to the code docstrings in JupyterExportHTMLTool.py. This README should be enough to get you started with installation, configuration, and usage in your own environment.

Happy exporting!
