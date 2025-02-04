![Swarmauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<div align="center">

![PyPI - Downloads](https://img.shields.io/pypi/dm/swarmauri_state_clipboard)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/swarmauri_state_clipboard)
![PyPI - License](https://img.shields.io/pypi/l/swarmauri_state_clipboard)
![PyPI - Version](https://img.shields.io/pypi/v/swarmauri_state_clipboard?label=swarmauri_state_clipboard&color=green)

</div>

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
