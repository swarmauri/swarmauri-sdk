![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_tool_jupyterstartkernel/">
        <img src="https://static.pepy.tech/badge/swarmauri_tool_jupyterstartkernel/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterstartkernel/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterstartkernel.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterstartkernel/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterstartkernel/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_jupyterstartkernel" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterstartkernel/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_jupyterstartkernel?label=swarmauri_tool_jupyterstartkernel&color=green" alt="PyPI - swarmauri_tool_jupyterstartkernel"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Tool Jupyter Start Kernel

`swarmauri_tool_jupyterstartkernel` is a Swarmauri notebook-orchestration tool
for starting a Jupyter kernel programmatically through `jupyter_client`. It is
useful for notebook automation, code-execution workflows, agent-controlled
kernel sessions, and CI flows that need a fresh kernel before running cells.

## Why Use Swarmauri Tool Jupyter Start Kernel

- Start isolated Jupyter kernels inside Swarmauri workflows.
- Acquire a kernel ID programmatically for downstream notebook tooling.
- Prepare execution environments for cell-running and notebook-conversion tools.
- Keep kernel lifecycle control behind a reusable Swarmauri tool interface.

## FAQ

> **What inputs does the tool accept?**  
> `kernel_name` and an optional `kernel_spec` dictionary.

> **What does the tool return on success?**  
> A dictionary containing `kernel_name` and `kernel_id`.

> **Does the tool expose the running `KernelManager`?**  
> Yes. The instance stores the active manager and exposes it through
> `get_kernel_manager()`.

> **How are startup failures reported?**  
> The tool returns `{"error": ...}` if the kernel cannot be started.

## Features

- Swarmauri `ToolBase` implementation registered as `JupyterStartKernelTool`.
- Starts Jupyter kernels by kernel name, defaulting to `python3`.
- Stores the active `KernelManager` for follow-on interactions.
- Returns simple, orchestration-friendly kernel identity metadata.
- Supports Python 3.10, 3.11, 3.12, 3.13, and 3.14.

## Installation

```bash
uv add swarmauri_tool_jupyterstartkernel
```

```bash
pip install swarmauri_tool_jupyterstartkernel
```

## Usage

```python
from swarmauri_tool_jupyterstartkernel import JupyterStartKernelTool

tool = JupyterStartKernelTool()
result = tool(kernel_name="python3")

print(result)
```

## Examples

### Start a default Python kernel

```python
from swarmauri_tool_jupyterstartkernel import JupyterStartKernelTool

tool = JupyterStartKernelTool()
result = tool()

print(result["kernel_id"])
```

### Start a kernel and keep the manager reference

```python
from swarmauri_tool_jupyterstartkernel import JupyterStartKernelTool

tool = JupyterStartKernelTool()
result = tool("python3")
manager = tool.get_kernel_manager()

print(result, manager)
```

### Register the tool in a Swarmauri collection

```python
from swarmauri_standard.tools.ToolCollection import ToolCollection
from swarmauri_tool_jupyterstartkernel import JupyterStartKernelTool

tools = ToolCollection(tools=[JupyterStartKernelTool()])
print(tools)
```

## Related Packages

- [swarmauri_tool_jupytershutdownkernel](https://pypi.org/project/swarmauri_tool_jupytershutdownkernel/)
- [swarmauri_tool_jupyterexecutecell](https://pypi.org/project/swarmauri_tool_jupyterexecutecell/)
- [swarmauri_tool_jupyterruncell](https://pypi.org/project/swarmauri_tool_jupyterruncell/)
- [swarmauri_tool_jupyterclearoutput](https://pypi.org/project/swarmauri_tool_jupyterclearoutput/)

## Swarmauri Foundations

- [swarmauri](https://pypi.org/project/swarmauri/)
- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)

## More Documentation

- [jupyter_client documentation](https://jupyter-client.readthedocs.io/)
- [IPython kernel documentation](https://ipython.readthedocs.io/)
- [Swarmauri SDK repository](https://github.com/swarmauri/swarmauri-sdk)

## Best Practices

- Ensure the requested kernelspec exists before starting automation flows.
- Shut down kernels explicitly after use to avoid orphaned processes.
- Keep per-task kernels isolated when multiple workflows run concurrently.
- Store the returned kernel ID if other tools need to interact with the same
  session later.

## License

This project is licensed under the Apache-2.0 License.
