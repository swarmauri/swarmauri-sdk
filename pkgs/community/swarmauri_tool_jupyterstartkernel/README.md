
![Swamauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_jupyterstartkernel/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_jupyterstartkernel" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterstartkernel/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterstartkernel.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterstartkernel/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_jupyterstartkernel" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterstartkernel/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_jupyterstartkernel" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterstartkernel/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_jupyterstartkernel?label=swarmauri_tool_jupyterstartkernel&color=green" alt="PyPI - swarmauri_tool_jupyterstartkernel"/></a>
</p>

---

# Swarmauri Tool Jupyter Start Kernel

## Overview
The swarmauri_tool_jupyterstartkernel package provides a tool that programmatically starts a Jupyter kernel using jupyter_client. It integrates seamlessly with the Swarmauri framework to offer flexible kernel initialization, monitoring, and error handling.

This tool can be particularly useful for dynamic, programmatic execution of notebook cells, automated testing of notebook-based workflows, or other situations where a Python (or alternative language) kernel instance is needed on-demand.

---

## Installation
You can install this package from the Python Package Index (PyPI). Make sure your Python version is between 3.10 and 3.12 (inclusive of 3.10 and exclusive of 3.13):

    pip install swarmauri_tool_jupyterstartkernel

If your environment uses Poetry, you can add this line to your pyproject.toml under [tool.poetry.dependencies]:

    swarmauri_tool_jupyterstartkernel = "*"

Note that the tool depends on:
• swarmauri_core  
• swarmauri_base  
• jupyter_client  

These will be installed automatically when using pip or Poetry.

---

## Usage
Once installed, you can import and create an instance of the JupyterStartKernelTool in your Python code. Below is a simple example showing how to start a kernel and capture the resulting kernel name and ID.

```python
from swarmauri_tool_jupyterstartkernel import JupyterStartKernelTool

# Create an instance of the JupyterStartKernelTool
tool = JupyterStartKernelTool()

# Start a default python3 kernel
results = tool()
print("Default Kernel Results:", results)

# Start a different kernel by specifying 'kernel_name'
custom_results = tool(kernel_name="python3")
print("Custom Kernel Results:", custom_results)
```

### Advanced Usage
You can optionally provide a kernel specification dictionary to configure more complex settings (e.g., environment variables, resource limits, custom arguments). This example shows how you might pass a simple configuration dictionary:

```python
config_spec = {
    "env": {
        "MY_CUSTOM_ENV_VAR": "test_value"
    }
}

# Start a kernel with custom specification
results_with_spec = tool(kernel_name="python3", kernel_spec=config_spec)
print("Advanced Kernel Results with Spec:", results_with_spec)
```

If a kernel fails to start, the tool returns an error message in the dictionary:

```python
error_results = tool(kernel_name="non_existent_kernel")
if "error" in error_results:
    print("Error starting kernel:", error_results["error"])
```

### Retrieving the Kernel Manager
The JupyterStartKernelTool class stores the KernelManager instance internally for access after a successful start. You can retrieve it at any time using:

```python
km = tool.get_kernel_manager()
if km:
    print("Kernel Manager is available for further operations.")
```

---

## Dependencies
• swarmauri_core: Provides the base classes and architecture for Swarmauri-type components.  
• swarmauri_base: Contains the general ToolBase class and other internal utilities.  
• jupyter_client: Manages Jupyter kernel operations, allowing this tool to start and monitor kernels.  

---

## License
swarmauri_tool_jupyterstartkernel is distributed under the Apache-2.0 License.  
© 2023 Swarmauri. All Rights Reserved.

For additional support, feel free to open an issue or contact our team for guidance on leveraging this tool within your Swarmauri-based deployments.
