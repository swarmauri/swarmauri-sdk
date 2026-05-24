![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_tool_jupyterexecutecell/">
        <img src="https://static.pepy.tech/badge/swarmauri_tool_jupyterexecutecell/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterexecutecell/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tool_jupyterexecutecell.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexecutecell/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexecutecell/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_jupyterexecutecell" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_jupyterexecutecell/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_jupyterexecutecell?label=swarmauri_tool_jupyterexecutecell&color=green" alt="PyPI - swarmauri_tool_jupyterexecutecell"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Tool Jupyter Execute Cell

`swarmauri_tool_jupyterexecutecell` is a Swarmauri code-execution tool for
running a single code cell inside the active IPython or Jupyter environment and
capturing stdout, stderr, and error information. It is useful for notebook
automation, agent-directed code execution, validation workflows, and interactive
runtime tooling.

## Why Use Swarmauri Tool Jupyter Execute Cell

- Execute code snippets from Swarmauri workflows in a live notebook context.
- Capture stdout, stderr, and tracebacks in a structured response.
- Apply timeouts to code execution to avoid hanging runs.
- Reuse the same callable surface across automation, agents, and testing flows.

## FAQ

> **What inputs does the tool accept?**  
> A code string plus an optional timeout in seconds.

> **What does the tool return?**  
> A dictionary containing `stdout`, `stderr`, and `error`.

> **What happens when no active IPython kernel is available?**  
> The tool returns an error payload indicating the kernel could not be found.

> **Does the tool execute asynchronously?**  
> No. It executes synchronously and uses a thread-backed timeout guard.

## Features

- Swarmauri `ToolBase` implementation registered as `JupyterExecuteCellTool`.
- Runs code in the active IPython/Jupyter environment.
- Captures stdout, stderr, and traceback information.
- Supports timeout-based interruption of long-running tasks.
- Supports Python 3.10, 3.11, 3.12, 3.13, and 3.14.

## Installation

```bash
uv add swarmauri_tool_jupyterexecutecell
```

```bash
pip install swarmauri_tool_jupyterexecutecell
```

## Usage

```python
from swarmauri_tool_jupyterexecutecell import JupyterExecuteCellTool

tool = JupyterExecuteCellTool()
result = tool("print('Hello from Swarmauri')", timeout=30)

print(result)
```

## Examples

### Execute a quick print statement

```python
from swarmauri_tool_jupyterexecutecell import JupyterExecuteCellTool

tool = JupyterExecuteCellTool()
result = tool("print(2 + 2)")

print(result["stdout"])
```

### Capture a runtime error

```python
from swarmauri_tool_jupyterexecutecell import JupyterExecuteCellTool

tool = JupyterExecuteCellTool()
result = tool("raise ValueError('bad input')")

print(result["error"])
```

### Register the tool in a Swarmauri collection

```python
from swarmauri_standard.tools.ToolCollection import ToolCollection
from swarmauri_tool_jupyterexecutecell import JupyterExecuteCellTool

tools = ToolCollection(tools=[JupyterExecuteCellTool()])
print(tools)
```

## Related Packages

- [swarmauri_tool_jupyterruncell](https://pypi.org/project/swarmauri_tool_jupyterruncell/)
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
- [Jupyter messaging and kernels](https://jupyter-client.readthedocs.io/)
- [Swarmauri SDK repository](https://github.com/swarmauri/swarmauri-sdk)

## Best Practices

- Keep executed code small and purposeful when running inside agents.
- Use timeouts for untrusted or potentially long-running cells.
- Inspect both `stderr` and `error` before assuming success.
- Prefer explicit kernel lifecycle management in multi-step notebook workflows.

## License

This project is licensed under the Apache-2.0 License.
