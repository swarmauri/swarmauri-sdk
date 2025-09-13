
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_light_mg8cmd.png">
  <source media="(prefers-color-scheme: light)" srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
  <!-- Fallback below (see #2) -->
  <img alt="Swarmauri Logo" src="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
</picture>

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexecutecell/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_jupyterexecutecell" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterexecutecell/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterexecutecell.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexecutecell/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_jupyterexecutecell" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexecutecell/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_jupyterexecutecell" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexecutecell/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_jupyterexecutecell?label=swarmauri_tool_jupyterexecutecell&color=green" alt="PyPI - swarmauri_tool_jupyterexecutecell"/></a>
</p>

---

# Swarmauri Tool Jupyter Execute Cell

The "swarmauri_tool_jupyterexecutecell" package provides a tool that allows you to execute code cells in an active Jupyter kernel, capturing all standard output, errors, and any exceptions that may occur. This makes it useful for programmatically running snippets of Python code within Jupyter environments, such as notebooks or other interactive contexts.

This package comes with fully functional, well-documented Python modules, following PEP 8 style guidelines and featuring type hints throughout. Each function, method, and class includes explanatory docstrings, helping users to quickly get started and integrate this tool into their own workflows.

---

## Installation

To install the package from PyPI with all its dependencies, run:

• Using pip:  
  pip install swarmauri_tool_jupyterexecutecell

• Supported Python versions:  
  - Python 3.10  
  - Python 3.11  
  - Python 3.12  
  - Python 3.13  

Make sure that Jupyter-related tools (e.g., IPython) are installed for the cell execution functionality to work as expected. If your environment does not already include Jupyter or IPython, you can install them alongside this package (for example, pip install jupyter ipython).

---

## Usage

After installation, you can import and use the JupyterExecuteCellTool to execute small code snippets within a running Jupyter session:

from swarmauri_tool_jupyterexecutecell import JupyterExecuteCellTool

# Instantiate the tool
tool = JupyterExecuteCellTool()

# Provide some code to execute
code_to_run = "print('Hello from swarmauri!')"

# Execute the code in the Jupyter kernel
result = tool(code_to_run)

# The 'result' dictionary contains three keys: 'stdout', 'stderr', and 'error'.
print("Captured standard output:")
print(result["stdout"])

print("Captured standard error (if any):")
print(result["stderr"])

print("Captured error messages (if any):")
print(result["error"])

If the execution times out (default is 30 seconds), the returned dictionary’s "error" key will contain a timeout message. You can override the default timeout by passing a second argument:

result = tool(code_to_run, timeout=60)  # 60-second timeout

## Examples

1. Executing Basic Python Statements:

   code_to_run = "a = 10\nb = 20\nprint(a + b)"
   result = tool(code_to_run)
   # result["stdout"] will contain '30'
   # result["stderr"] and result["error"] should be empty if everything worked correctly.

2. Handling Exceptions:

   code_with_error = "print(1/0)"  # Division by zero
   result = tool(code_with_error)
   # result["stdout"] should be empty
   # result["stderr"] or result["error"] will contain information about the ZeroDivisionError.

3. Complex Operations Requiring More Time:

   code_with_long_process = '''
import time
time.sleep(10)
print("Long operation finished!")
'''
   result = tool(code_with_long_process, timeout=15)
   # Will complete successfully if it finishes under 15 seconds.
   # If it exceeds the specified timeout, the "error" key will note the timeout event.

---

## Dependencies

• swarmauri_core for core support.  
• swarmauri_base for base tool classes.  
• jupyter_client (and typically IPython) for Jupyter interaction.  

Consult the pyproject.toml for additional dev/test dependencies.  

---

## Additional Notes

• The package is designed to work seamlessly in Jupyter-based environments but also includes robust error handling and logging.  
• All user-facing methods and classes are fully implemented with docstrings and type hints, ensuring clarity and strong typing.  
• The JupyterExecuteCellTool inherits from the ToolBase class and is registered via the ComponentBase for easy integration into the broader Swarmauri ecosystem.  

We hope you find this tool helpful in automating or simplifying code execution within Jupyter kernels. Enjoy effortless cell execution and output management with swarmauri_tool_jupyterexecutecell!
