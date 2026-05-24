![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_tool_jupyterruncell/">
        <img src="https://static.pepy.tech/badge/swarmauri_tool_jupyterruncell/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterruncell/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterruncell.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterruncell/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterruncell/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_jupyterruncell" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterruncell/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_jupyterruncell?label=swarmauri_tool_jupyterruncell&color=green" alt="PyPI - swarmauri_tool_jupyterruncell"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Tool Jupyter Run Cell

`swarmauri_tool_jupyterruncell` is a Swarmauri IPython-execution tool for
running code inside the active interactive shell and capturing cell output,
error output, and success state. It is useful for notebook-style automation,
interactive assistants, teaching flows, and environments that already host an
IPython shell.

## Why Use Swarmauri Tool Jupyter Run Cell

- Execute code directly inside the active IPython shell.
- Capture both successful output and exception traces in a consistent shape.
- Apply optional signal-based timeouts to interactive cell execution.
- Reuse an execution primitive across notebook and agent workflows.

## FAQ

> **What inputs does the tool accept?**  
> A code string and an optional timeout.

> **What does the tool return?**  
> A dictionary with `cell_output`, `error_output`, and `success`.

> **What happens if no IPython shell is active?**  
> The tool returns a failed result with an explanatory error message.

> **How is this different from `jupyterexecutecell`?**  
> This tool is explicitly oriented around an already-running interactive
> IPython shell and returns a `success` flag plus separated output fields.

## Features

- Swarmauri `ToolBase` implementation registered as `JupyterRunCellTool`.
- Executes Python code in the active IPython shell.
- Captures stdout and stderr-like error output into separate fields.
- Supports optional timeout-based interruption.
- Supports Python 3.10, 3.11, 3.12, 3.13, and 3.14.

## Installation

```bash
uv add swarmauri_tool_jupyterruncell
```

```bash
pip install swarmauri_tool_jupyterruncell
```

## Usage

```python
from swarmauri_tool_jupyterruncell import JupyterRunCellTool

tool = JupyterRunCellTool()
result = tool(code="print('hello')", timeout=5)

print(result)
```

## Examples

### Run a simple expression

```python
from swarmauri_tool_jupyterruncell import JupyterRunCellTool

tool = JupyterRunCellTool()
result = tool("print(3 * 7)")

print(result["cell_output"])
```

### Capture an exception

```python
from swarmauri_tool_jupyterruncell import JupyterRunCellTool

tool = JupyterRunCellTool()
result = tool("1 / 0")

print(result["success"], result["error_output"])
```

### Register the tool in a Swarmauri collection

```python
from swarmauri_standard.tools.ToolCollection import ToolCollection
from swarmauri_tool_jupyterruncell import JupyterRunCellTool

tools = ToolCollection(tools=[JupyterRunCellTool()])
print(tools)
```

## Related Packages

- [swarmauri_tool_jupyterexecutecell](https://pypi.org/project/swarmauri_tool_jupyterexecutecell/)
- [swarmauri_tool_jupyterstartkernel](https://pypi.org/project/swarmauri_tool_jupyterstartkernel/)
- [swarmauri_tool_jupytershutdownkernel](https://pypi.org/project/swarmauri_tool_jupytershutdownkernel/)
- [swarmauri_tool_jupyterclearoutput](https://pypi.org/project/swarmauri_tool_jupyterclearoutput/)

## Swarmauri Foundations

- [swarmauri](https://pypi.org/project/swarmauri/)
- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)

## More Documentation

- [IPython documentation](https://ipython.readthedocs.io/)
- [Python `signal` documentation](https://docs.python.org/3/library/signal.html)
- [Swarmauri SDK repository](https://github.com/swarmauri/swarmauri-sdk)

## Best Practices

- Use short timeouts only for code you expect to complete quickly.
- Inspect `success` before trusting `cell_output`.
- Prefer controlled code snippets when exposing this tool to agents.
- Use this tool when you already have an active IPython shell rather than a
  separately managed Jupyter kernel session.

## License

This project is licensed under the Apache-2.0 License.
