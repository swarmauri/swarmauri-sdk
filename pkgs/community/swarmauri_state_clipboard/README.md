![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_state_clipboard/">
        <img src="https://static.pepy.tech/badge/swarmauri_state_clipboard/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_state_clipboard/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_state_clipboard.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_state_clipboard/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_state_clipboard/">
        <img src="https://img.shields.io/pypi/l/swarmauri_state_clipboard" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_state_clipboard/">
        <img src="https://img.shields.io/pypi/v/swarmauri_state_clipboard?label=swarmauri_state_clipboard&color=green" alt="PyPI - swarmauri_state_clipboard"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri State Clipboard

`swarmauri_state_clipboard` provides a Swarmauri `StateBase` implementation
that stores state in the system clipboard. It is useful for desktop
prototyping, local demos, quick workflow handoffs, and lightweight
human-in-the-loop tooling where a full database or cache would be unnecessary.

## Why Use Swarmauri State Clipboard

- Persist small state payloads without adding external infrastructure.
- Bridge state between local tools, notebooks, shells, and GUI apps.
- Prototype Swarmauri stateful flows quickly on Windows, macOS, or Linux.
- Keep local development loops simple when you only need transient state.

## FAQ

> **What does this package store?**  
> It stores dictionary-shaped data by serializing it to the system clipboard.

> **Which platforms are supported?**  
> Windows uses `clip` and PowerShell `Get-Clipboard`, macOS uses `pbcopy` and
> `pbpaste`, and Linux uses `xclip`.

> **Is this suitable for production workloads?**  
> Usually no. The clipboard is global, user-facing, and not designed for
> secure or concurrent application state.

> **How is clipboard data parsed when reading?**  
> The package uses `ast.literal_eval` to parse string content into Python
> literals.

## Features

- Swarmauri `StateBase` implementation registered as `ClipboardState`.
- Cross-platform clipboard access through built-in OS utilities.
- Read, write, update, reset, and deep-copy state helpers.
- No third-party runtime dependency beyond core Swarmauri packages.
- Supports Python 3.10, 3.11, 3.12, 3.13, and 3.14.

## Installation

```bash
uv add swarmauri_state_clipboard
```

```bash
pip install swarmauri_state_clipboard
```

## Usage

```python
from swarmauri_state_clipboard import ClipboardState

state = ClipboardState()
state.write({"session": "abc123", "step": 1})

print(state.read())

state.update({"step": 2})
print(state.read())
```

## Examples

### Use clipboard state in a local prototype

```python
from swarmauri_state_clipboard import ClipboardState

state = ClipboardState()
state.write({"draft": "ready", "owner": "local-user"})

print(state.read())
```

### Reset state after a task completes

```python
from swarmauri_state_clipboard import ClipboardState

state = ClipboardState()
state.write({"job": "complete"})
state.reset()

print(state.read())  # {}
```

### Clone the current state for a second workflow branch

```python
from swarmauri_state_clipboard import ClipboardState

state = ClipboardState()
state.write({"request_id": "req-001", "status": "queued"})

forked_state = state.deep_copy()
forked_state.update({"status": "processed"})

print(state.read())
print(forked_state.read())
```

## Related Packages

- [swarmauri](https://pypi.org/project/swarmauri/)
- [swarmauri_standard](https://pypi.org/project/swarmauri_standard/)
- [swarmauri_workflow_statedriven](https://pypi.org/project/swarmauri_workflow_statedriven/)

## Swarmauri Foundations

- [swarmauri_core](https://pypi.org/project/swarmauri_core/)
- [swarmauri_base](https://pypi.org/project/swarmauri_base/)

## More Documentation

- [Swarmauri SDK repository](https://github.com/swarmauri/swarmauri-sdk)
- [Python `ast.literal_eval` documentation](https://docs.python.org/3/library/ast.html#ast.literal_eval)

## Best Practices

- Keep clipboard payloads small and short-lived.
- Avoid storing secrets or sensitive tokens in clipboard-backed state.
- Install `xclip` explicitly on Linux hosts and CI runners.
- Prefer a durable state backend for concurrent, remote, or production flows.

## License

This project is licensed under the Apache-2.0 License.
