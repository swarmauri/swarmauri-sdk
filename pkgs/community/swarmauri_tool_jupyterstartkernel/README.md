![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

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

# Swarmauri Tool · Jupyter Start Kernel

A Swarmauri orchestration tool that spins up Jupyter kernels on demand using `jupyter_client`. The helper wraps connection-file management, kernel specification, and timeout handling so automation pipelines, notebook CI, or Swarmauri agents can acquire fresh kernels with one function call.

- Launches kernels with configurable names and kernel-spec overrides.
- Surfaces ready-to-use connection metadata for downstream orchestration.
- Keeps a reference to the underlying `KernelManager` so you can interact with the kernel lifecycle after launch.

## Requirements

- Python 3.10 – 3.13.
- The environment must have Jupyter kernel specs installed (for example the default `python3`).
- Dependencies (`jupyter_client`, `swarmauri_base`, `swarmauri_standard`, `pydantic`) install automatically.

## Installation

Install via the packaging tool that matches your workflow. Each command fetches transitive dependencies.

**pip**

```bash
pip install swarmauri_tool_jupyterstartkernel
```

**Poetry**

```bash
poetry add swarmauri_tool_jupyterstartkernel
```

**uv**

```bash
# Add to the current project and update uv.lock
uv add swarmauri_tool_jupyterstartkernel

# or install into the active environment without touching pyproject.toml
uv pip install swarmauri_tool_jupyterstartkernel
```

> Tip: When using uv inside this repository, run commands from the repository root so `uv` can resolve the shared `pyproject.toml`.

## Quick Start

The tool behaves like a callable. Instantiate it and optionally pass a `kernel_name`, timeout, or kernel spec.

```python
from swarmauri_tool_jupyterstartkernel import JupyterStartKernelTool

start_kernel = JupyterStartKernelTool()
result = start_kernel()  # defaults to python3

print(result)
# {
#   'status': 'success',
#   'kernel_id': '03c7d8f9-ec4d-4a8a-8a90-cdb35ff9e6c9',
#   'kernel_name': 'python3',
#   'connection_file': '/Users/.../jupyter/runtime/kernel-03c7d8f9.json'
# }
```

A non-success status signals the kernel failed to spawn (missing kernelspec, permission issue, etc.).

## Usage Scenarios

### Launch With Custom Specification

```python
from swarmauri_tool_jupyterstartkernel import JupyterStartKernelTool

start_kernel = JupyterStartKernelTool()
config = {
    "env": {"EXPERIMENT_FLAG": "1"},
    "resource_limits": {"memory": "1G"}
}

custom = start_kernel(kernel_name="python3", kernel_spec=config, startup_timeout=20)

if custom["status"] == "success":
    print(f"Kernel ready at {custom['connection_file']}")
else:
    raise RuntimeError(custom["message"])
```

Pass a `kernel_spec` dict to tweak environment variables or other launch parameters that the underlying `KernelManager` accepts.

### Pair With the Shutdown Tool in an Automated Flow

```python
from swarmauri_tool_jupyterstartkernel import JupyterStartKernelTool
from swarmauri_tool_jupytershutdownkernel import JupyterShutdownKernelTool

start_kernel = JupyterStartKernelTool()
shutdown_kernel = JupyterShutdownKernelTool()

launch = start_kernel(kernel_name="python3")
if launch["status"] != "success":
    raise RuntimeError(launch["message"])

kernel_id = launch["kernel_id"]
print(f"Kernel started: {kernel_id}")

# ... run your notebook execution workflow ...

cleanup = shutdown_kernel(kernel_id=kernel_id, shutdown_timeout=10)
print(cleanup)
```

Use this pairing in CI pipelines or agent flows that must guarantee kernels are torn down after execution.

### Integrate Inside a Swarmauri Agent

```python
from swarmauri_core.agent.Agent import Agent
from swarmauri_core.messages.HumanMessage import HumanMessage
from swarmauri_standard.tools.registry import ToolRegistry
from swarmauri_tool_jupyterstartkernel import JupyterStartKernelTool

registry = ToolRegistry()
registry.register(JupyterStartKernelTool())

agent = Agent(tool_registry=registry)
message = HumanMessage(content="start a python3 kernel for my notebook batch job")
response = agent.run(message)
print(response)
```

The agent resolves the registered tool, starts a kernel, and returns the connection metadata to the conversation context.

## Troubleshooting

- **`No such kernel`** – The requested `kernel_name` is not installed. Check `jupyter kernelspec list`.
- **`Kernel start timeout exceeded`** – Increase `startup_timeout` for slow environments or pre-warm interpreters.
- **Permission errors** – Ensure the process can create files inside Jupyter's runtime directory (usually `~/.local/share/jupyter/runtime`).

## License

`swarmauri_tool_jupyterstartkernel` is released under the Apache 2.0 License. See `LICENSE` for details.
