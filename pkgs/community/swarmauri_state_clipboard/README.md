![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_state_clipboard/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_state_clipboard" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_state_clipboard/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_state_clipboard.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_state_clipboard/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_state_clipboard" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_state_clipboard/">
        <img src="https://img.shields.io/pypi/l/swarmauri_state_clipboard" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_state_clipboard/">
        <img src="https://img.shields.io/pypi/v/swarmauri_state_clipboard?label=swarmauri_state_clipboard&color=green" alt="PyPI - swarmauri_state_clipboard"/></a>
</p>

---

# Swarmauri State Clipboard

`ClipboardState` implements Swarmauri's `StateBase` interface using the system clipboard as storage. Useful for quick demos or sharing state between desktop tools without running an external datastore.

## Features

- Reads/writes clipboard contents via platform commands (`clip`, `pbcopy`/`pbpaste`, `xclip`).
- Stores JSON-like dictionaries as string representations; uses `ast.literal_eval` when reading.
- Provides `write`, `read`, `update`, `reset`, and `deep_copy` helpers.

## Prerequisites

- Python 3.10 or newer.
- OS clipboard utilities available:
  - Windows: `clip` (built-in) and PowerShell `Get-Clipboard`.
  - macOS: `pbcopy`/`pbpaste` (built-in).
  - Linux: `xclip` installed (`apt install xclip` or equivalent).

## Installation

```bash
# pip
pip install swarmauri_state_clipboard

# poetry
poetry add swarmauri_state_clipboard

# uv (pyproject-based projects)
uv add swarmauri_state_clipboard
```

## Quickstart

```python
from swarmauri_state_clipboard import ClipboardState

state = ClipboardState()
state.write({"key1": "value1", "counter": 42})
print(state.read())

state.update({"counter": 43})
print(state.read())

state.reset()
print(state.read())  # {}
```

## Deep Copy

```python
state = ClipboardState()
state.write({"session": "abc123"})
clone = state.deep_copy()
clone.update({"session": "xyz789"})

print(state.read())   # {'session': 'abc123'}
print(clone.read())    # {'session': 'xyz789'}
```

## Tips

- Clipboard overwrites are global; avoid using this state provider in multi-user or production environments where clipboard privacy matters.
- Contents are stored as Python literal strings—avoid writing untrusted data to the clipboard to prevent evaluation issues (though `ast.literal_eval` mitigates code execution risks).
- Ensure required system commands exist before running in CI or containers (install `xclip` for Linux builds).

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
