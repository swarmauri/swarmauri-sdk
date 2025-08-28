![Swamauri Logo](https://res.cloudinary.com/dbjmpekvl/image/upload/v1730099724/Swarmauri-logo-lockup-2048x757_hww01w.png)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_gitfilter_file/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_gitfilter_file" alt="PyPI - Downloads"/>
    </a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_gitfilter_file/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_gitfilter_file.svg"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_gitfilter_file/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_gitfilter_file" alt="PyPI - Python Version"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_gitfilter_file/">
        <img src="https://img.shields.io/pypi/l/swarmauri_gitfilter_file" alt="PyPI - License"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_gitfilter_file/">
        <img src="https://img.shields.io/pypi/v/swarmauri_gitfilter_file?label=swarmauri_gitfilter_file&color=green" alt="PyPI - swarmauri_gitfilter_file"/>
    </a>
</p>

---

# Swarmauri Git Filter File

Filesystem backed git filter for Peagen.

## Installation

```bash
pip install swarmauri_gitfilter_file
```

## Usage

```python
from swarmauri_gitfilter_file import FileFilter

filt = FileFilter.from_uri("file:///tmp/store")
oid = filt.clean(b"hello")
assert filt.smudge(oid) == b"hello"
```
