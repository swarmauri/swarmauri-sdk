![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

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

# Swarmauri Tool · Jupyter Shutdown Kernel

A Swarmauri-compatible utility that performs graceful or forced shutdowns of running Jupyter kernels. It is ideal for automated resource clean-up, CI workflows that recycle kernels between test suites, and agents that need to reclaim compute when a conversation finishes.

- Supports graceful and forced shutdown paths with configurable timeouts.
- Returns structured status payloads suitable for orchestration pipelines.
- Builds on `swarmauri_base`/`swarmauri_standard` abstractions so it can be registered like any other tool inside a Swarmauri agent graph.

## Requirements

- Python 3.10 – 3.13.
- Local access to the target kernel's connection file (typically lives in Jupyter's runtime directory on the same host).
- Dependencies (`jupyter_client`, `swarmauri_base`, `swarmauri_standard`, `pydantic`) install automatically with the package.

## Installation

Install the package with the workflow that matches your environment. All commands below resolve transitive dependencies.

**pip**

```bash
pip install swarmauri_tool_jupytershutdownkernel
```

**Poetry**

```bash
poetry add swarmauri_tool_jupytershutdownkernel
```

**uv**

```bash
# Add to the current project and lockfile
uv add swarmauri_tool_jupytershutdownkernel

# or install into the active environment without editing pyproject.toml
uv pip install swarmauri_tool_jupytershutdownkernel
```

> Tip: When using uv inside this repository, run commands from the repository root so `uv` can discover the consolidated `pyproject.toml`.

## Quick Start

The tool exposes a callable interface. Instantiate it and provide the kernel identifier along with an optional timeout (seconds). The identifier should match the `kernel_id` used by Jupyter when the connection file `kernel-<kernel_id>.json` is created.

```python
from jupyter_client import KernelManager
from swarmauri_tool_jupytershutdownkernel import JupyterShutdownKernelTool

# 1. Launch a kernel (acts as stand-in for an existing notebook kernel).
km = KernelManager(kernel_name="python3")
km.start_kernel()

# 2. Capture the kernel identifier Jupyter assigned (UUID-style string).
kernel_identifier = km.kernel_id or km.connection_file.split("kernel-")[-1].split(".json")[0]
print(f"Kernel identifier: {kernel_identifier}")

# 3. Shut the kernel down with the Swarmauri tool.
shutdown_tool = JupyterShutdownKernelTool()
response = shutdown_tool(kernel_id=kernel_identifier, shutdown_timeout=10)
print(response)
```

The returned dictionary always contains `kernel_id`, `status`, and `message`. A `status` of `error` indicates the tool attempted a forced shutdown or encountered an issue loading the connection file.

## Usage Scenarios

### Automate Notebook Clean-up After Batch Execution

```python
import json
from pathlib import Path
from swarmauri_tool_jupytershutdownkernel import JupyterShutdownKernelTool

runtime_dir = Path.home() / ".local" / "share" / "jupyter" / "runtime"
shutdown_tool = JupyterShutdownKernelTool()

for connection_file in runtime_dir.glob("kernel-*.json"):
    kernel_id = connection_file.stem.replace("kernel-", "")
    result = shutdown_tool(kernel_id=kernel_id, shutdown_timeout=5)
    print(json.dumps(result, indent=2))
```

This script discovers every live kernel connection file on the current host and attempts to close it gracefully. It is useful for CI jobs that leave stray kernels active between notebook test suites.

### Shut Down Kernels Started Via `MultiKernelManager`

```python
from jupyter_client import MultiKernelManager
from swarmauri_tool_jupytershutdownkernel import JupyterShutdownKernelTool

multi = MultiKernelManager()

# Start a new kernel for an integration test and capture its UUID.
kernel_id = multi.start_kernel(kernel_name="python3")
print(f"Started kernel with id={kernel_id}")

# Run your test suite against the kernel ...

# When finished, shut it down through the Swarmauri tool.
shutdown_tool = JupyterShutdownKernelTool()
result = shutdown_tool(kernel_id=kernel_id, shutdown_timeout=8)
print(result)
```

Because `MultiKernelManager` stores connection files under the standard `kernel-<kernel_id>.json` naming pattern, the shutdown tool can resolve the same kernel and close it without needing direct access to the `MultiKernelManager` instance that launched it.

## Troubleshooting

- **`No such kernel`** – The tool could not locate a matching connection file. Make sure the process has read access to Jupyter's runtime directory and that you pass the raw identifier (for example, `03c7d8f9-ec4d-4a8a-8a90-cdb35ff9e6c9`).
- **`Connection file not found`** – The connection file was deleted or the kernel lives on a different machine. Run the shutdown tool on the same host where the kernel was started.
- **Forced shutdowns** – If the kernel remains alive after the timeout expires, the tool switches to a forced shutdown. You can increase `shutdown_timeout` to give busy kernels more time to finish.
- **Sandboxed environments** – Some containerized or restricted environments may block the network ports that Jupyter kernels use. In those cases, start kernels with appropriate permissions before attempting to shut them down programmatically.

## License

`swarmauri_tool_jupytershutdownkernel` is released under the Apache 2.0 License. See `LICENSE` for details.
