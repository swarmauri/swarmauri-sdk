
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_light_mg8cmd.png">
  <source media="(prefers-color-scheme: light)" srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
  <!-- Fallback below (see #2) -->
  <img alt="Swarmauri Logo" src="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
</picture>

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexecuteandconvert/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_jupyterexecuteandconvert" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterexecuteandconvert/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterexecuteandconvert.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexecuteandconvert/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_jupyterexecuteandconvert" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexecuteandconvert/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_jupyterexecuteandconvert" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexecuteandconvert/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_jupyterexecuteandconvert?label=swarmauri_tool_jupyterexecuteandconvert&color=green" alt="PyPI - swarmauri_tool_jupyterexecuteandconvert"/></a>
</p>

---

# Swarmauri Tool Jupyterexecuteandconvert

This package provides functionality to programmatically execute a Jupyter Notebook and convert it to a variety of output formats using nbconvert, enabling automated workflows within the Swarmauri framework.

---

## Installation

swarmauri_tool_jupyterexecuteandconvert supports Python 3.10 to 3.13. To install from PyPI, use:

pip install swarmauri_tool_jupyterexecuteandconvert

Once installed, the JupyterExecuteAndConvertTool becomes available, offering notebook execution and conversion features via the nbconvert CLI.

---

## Usage

Below is a detailed example of how to utilize the JupyterExecuteAndConvertTool in your environment. The tool exposes a callable class that you can directly instantiate and use in your Python code.

1. Import the tool into your code:
   
   from swarmauri_tool_jupyterexecuteandconvert import JupyterExecuteAndConvertTool

2. Create an instance of the tool:
   
   notebook_tool = JupyterExecuteAndConvertTool()

3. Invoke the tool to execute and convert a notebook:
   
   result = notebook_tool(
       notebook_path="path/to/your_notebook.ipynb",
       output_format="pdf",         # can also be "html"
       execution_timeout=600        # optional, defaults to 600 seconds
   )

4. Process the returned dictionary:
   
   if "status" in result and result["status"] == "success":
       print(f"Successfully converted notebook to: {result['converted_file']}")
   else:
       print(f"Error: {result.get('error')} - {result.get('message')}")

The result dictionary can contain:
• "converted_file": A string representing the output file name.  
• "status": "success" if execution and conversion succeeded.  
• "error" and "message": In the event of any errors during execution or conversion.  

Here is a short illustration:

---------------------------------------------------------------------------------------
from swarmauri_tool_jupyterexecuteandconvert import JupyterExecuteAndConvertTool

# Create the tool instance
tool = JupyterExecuteAndConvertTool()

# Execute and convert a Jupyter notebook to PDF with a 5-minute timeout
response = tool(
    notebook_path="analysis.ipynb",
    output_format="pdf",
    execution_timeout=300
)

if response.get("status") == "success":
    print(f"Notebook converted: {response['converted_file']}")
else:
    print(f"Error type: {response.get('error')}")
    print(f"Error message: {response.get('message')}")
---------------------------------------------------------------------------------------

---

## Dependencies

• nbconvert: Used for executing and converting Jupyter notebooks to the desired output format.  
• swarmauri_core, swarmauri_base: Required dependencies from the Swarmauri framework, providing essential base classes and utilities.  
• Python 3.10 or above.  

The tool automatically integrates into the Swarmauri ecosystem by inheriting from ToolBase and registering itself with ComponentBase.

---

### About JupyterExecuteAndConvertTool

The JupyterExecuteAndConvertTool is defined in JupyterExecuteAndConvertTool.py. It inherits from ToolBase and uses the @ComponentBase.register_type decorator, making it seamlessly integrable as a Swarmauri tool. It logs notebook execution progress and handles any errors or timeouts. Once the notebook is executed, nbconvert is used again to convert the resultant executed notebook to the specified format (HTML or PDF).

Key attributes within the tool:
• version: A string indicating the current version of the tool.  
• parameters: A list of Parameter objects describing inputs such as notebook_path, output_format, and execution_timeout.  
• __call__: A method accepting notebook_path, output_format, and execution_timeout, returning a dictionary with information about the process result or any encountered errors.  

---

## Contributing

Thank you for your interest in swarmauri_tool_jupyterexecuteandconvert. Pull requests and bug reports are welcome. Please see our issue tracker for existing requests and open issues.

---

© 2023 Swarmauri – Licensed under the Apache License, Version 2.0.  
Happy notebook converting!
