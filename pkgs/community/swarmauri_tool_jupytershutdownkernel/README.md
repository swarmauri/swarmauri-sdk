
![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_jupytershutdownkernel/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_jupytershutdownkernel" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupytershutdownkernel/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupytershutdownkernel.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupytershutdownkernel/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_jupytershutdownkernel" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupytershutdownkernel/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_jupytershutdownkernel" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupytershutdownkernel/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_jupytershutdownkernel?label=swarmauri_tool_jupytershutdownkernel&color=green" alt="PyPI - swarmauri_tool_jupytershutdownkernel"/></a>
</p>

---

# Swarmauri Tool Jupyter Shutdown Kernel

The swarmauri_tool_jupytershutdownkernel package provides a straightforward solution to shut down a running Jupyter kernel programmatically. It uses jupyter_client under the hood and is integrated into the Swarmauri framework ecosystem. This tool can be useful for automated resource management, testing scenarios that require repeated kernel restarts, or any workflow that programmatically terminates Jupyter kernels.

## Installation

You can install this module directly via PyPI using pip:

  pip install swarmauri_tool_jupytershutdownkernel

This will install the package and its dependencies, including jupyter_client and the Swarmauri libraries required by JupyterShutdownKernelTool.

Ensure you are running a Python version between 3.10 and 3.13, and that you have the appropriate Swarmauri core/base packages installed. Typically, pip will handle these dependencies automatically.

## Usage

After installation, you can use the JupyterShutdownKernelTool to shut down a running Jupyter kernel by referencing it within your Python scripts or tools.

Here’s a quick example of how to import and use JupyterShutdownKernelTool:

--------------------------------------------------------------------------------
Example:

from swarmauri_tool_jupytershutdownkernel import JupyterShutdownKernelTool

def shutdown_kernel_example(kernel_identifier: str):
    """
    Demonstrates shutting down a Jupyter kernel using the JupyterShutdownKernelTool.
    """
    # Instantiate the tool
    shutdown_tool = JupyterShutdownKernelTool()

    # Perform kernel shutdown
    response = shutdown_tool(kernel_id=kernel_identifier, shutdown_timeout=5)

    # Print the result
    print(response)
--------------------------------------------------------------------------------

1. Create an instance of JupyterShutdownKernelTool.  
2. Invoke it like a function, passing the kernel_id (the unique identifier for your kernel) and an optional shutdown_timeout in seconds.  
3. The method returns a dictionary with the key-value pairs indicating whether the shutdown was successful or if an error occurred.

### Detailed Usage Instructions

• Ensure the kernel you want to shut down is running and that its connection file is accessible.  
• Pass the kernel's ID or name to the tool.  
• Optionally configure the shutdown_timeout parameter (default is 5s) to give the tool more or less time to perform a graceful shutdown.  
• Check the returned dictionary to confirm a successful shutdown or to see an error message for troubleshooting.

### Dependencies

• jupyter_client – Underlies the kernel shutdown implementation.  
• swarmauri_core / swarmauri_base – Provide the foundational classes (ComponentBase and ToolBase).  
• pydantic – Used internally for type validation in Swarmauri parameters.  

Below is a reference to the core files where the functionality resides:

1. JupyterShutdownKernelTool.py  
2. __init__.py  
3. pyproject.toml  

In particular, JupyterShutdownKernelTool.py includes the main logic for stopping a Jupyter kernel and handles creditable outcomes like missing kernels, missing connection files, or forced terminations if the kernel does not shut down gracefully within the allotted time.

We hope this tool helps you manage Jupyter kernels more effectively, freeing you to focus on other aspects of your workflows!
