
<picture>
  <source media="(prefers-color-scheme: dark)"  srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_light_mg8cmd.png">
  <source media="(prefers-color-scheme: light)" srcset="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
  <!-- Fallback below (see #2) -->
  <img alt="Swarmauri Logo" src="https://res.cloudinary.com/dryedzrlo/image/upload/v1757724629/swarmauri_brand_frag_dark_tzjuja.png">
</picture>

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

A concrete implementation of StateBase that uses the system clipboard to store and retrieve state data.

## Installation

```bash
pip install swarmauri_state_clipboard
```

## Usage
Basic usage examples with code snippets
```python
from swarmauri.states.ClipboardState import ClipboardState

# Create an instance of ClipboardState
clipboard_state = ClipboardState()

# Write data to the clipboard
clipboard_state.write({"key1": "value1", "key2": 42})

# Read data from the clipboard
data = clipboard_state.read()
print(data)  # Output: {'key1': 'value1', 'key2': 42}

# Update data on the clipboard
clipboard_state.update({"key3": "value3"})

# Read updated data from the clipboard
updated_data = clipboard_state.read()
print(updated_data)  # Output: {'key1': 'value1', 'key2': 42, 'key3': 'value3'}

# Reset the clipboard state
clipboard_state.reset()

# Verify the clipboard is reset
reset_data = clipboard_state.read()
print(reset_data)  # Output: {}
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.
