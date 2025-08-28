# Swarmauri File Git Filter

Filesystem-based git filter for Peagen that stores artifacts on the local disk.

## Installation

```bash
# pip install swarmauri_gitfilter_file (when published)
```

## Usage

```python
from swarmauri_gitfilter_file import FileFilter

filt = FileFilter.from_uri("file:///tmp/peagen")
oid = filt.clean(b"hello")
print(filt.smudge(oid))
```
