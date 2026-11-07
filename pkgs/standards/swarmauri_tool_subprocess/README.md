![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tool_subprocess/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tool_subprocess" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tool_subprocess/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_tool_subprocess.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_subprocess/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tool_subprocess" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_subprocess/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tool_subprocess" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tool_subprocess/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tool_subprocess?label=swarmauri_tool_subprocess&color=green" alt="PyPI - swarmauri_tool_subprocess"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Tool Subprocess

Execute subprocess commands and capture output, timeouts, and exit codes.

## Features

- Execute argument vectors without shell expansion by default.
- Capture stdout, stderr, and integer exit codes, including nonzero codes.
- Distinguish completed commands, missing executables, timeouts, and errors.
- Select a child working directory and an explicit replacement environment.
- Discover the component through the `swarmauri.tools` entry point and facade.
- Preserve the original standard import through a lazy compatibility adapter.
- Share execution with the standard kernel, which can run the legacy tool by itself.

## Installation

```bash
uv add swarmauri_tool_subprocess
pip install swarmauri_tool_subprocess
```

## Usage

```python
import sys
from swarmauri_tool_subprocess import SubprocessTool

tool = SubprocessTool()
result = tool([sys.executable, "-c", "print('hello')"], timeout=5)
assert result["stdout"].strip() == "hello"
assert result["exit_code"] == 0
```

Use argument vectors for commands containing paths or arguments with spaces,
particularly on Windows. With `shell=False`, string commands use POSIX
`shlex.split` quoting; they are not parsed by the Windows command processor.

Shell mode accepts strings only and executes arbitrary syntax through the
platform shell (`/bin/sh` on POSIX or the configured Windows command processor):

```python
result = tool("echo first && echo second", shell=True, timeout=5)
```

Only trusted callers should choose shell commands, executables, working
directories, and environment values. Windows native mode (`shell=False`)
resolves the executable from the parent search environment and requires a
native `.exe` or `.com`. Use a trusted absolute executable path for deterministic
selection. To invoke trusted batch syntax, use explicit shell mode. Windows
may otherwise parse batch arguments through its command interpreter.

`cwd=None` inherits the parent's working directory. `env=None` deliberately
inherits the parent's environment for compatibility. Pass `env={...}` to supply
the complete child environment; it is not merged with the parent. Include any
platform-required variables (such as `SystemRoot` on Windows) and an appropriate
`PATH` when needed, or use an absolute executable path. Avoid forwarding secrets
the child does not need.

`timeout=None` imposes no timeout. A supplied timeout applies to the direct
child after process creation. Timed Windows calls capture output in temporary
files, so inherited output handles cannot make the timeout wait for pipe EOF.
On success, capture is a snapshot taken after the direct child exits.
Descendants can continue running and retain inherited temporary handles until
they exit. Keep subprocess execution under the service's trust policy.

## Results and migration

The standalone API returns `status`, `stdout`, `stderr`, and `exit_code`:

| Status | Meaning | Exit code |
|---|---|---|
| `success` | Process completed, including nonzero exit codes | Integer |
| `timeout` | Process exceeded the timeout | `None` |
| `not_found` | Executable or requested working directory was not found | `127` |
| `runtime_error` | Invalid arguments or another execution failure | `None` |

`success` describes process completion, not application success; check
`exit_code == 0` before treating a command as successful. Passing an argument
list with `shell=True`, an empty command, or malformed quoting returns
`runtime_error` without starting a child.

Existing code can continue to use the original case-sensitive import:

```python
from swarmauri_standard.tools.SubprocessTool import SubprocessTool

result = SubprocessTool()("echo hello", shell=True)
assert result["exit_code"] == "0"
```

The compatibility adapter emits a `DeprecationWarning` and retains the original
three-key result and string exit codes: numeric strings for completed commands,
`"timeout"` for timeouts, and `"error"` for execution failures. Import from the
standalone package when adopting the richer typed results and `cwd`/`env`
options. Importing the compatibility module alone does not load the standalone
package.
The lowercase module spelling introduced in the PR is also accepted as an
import alias. Both spellings share the same module and legacy result contract.
