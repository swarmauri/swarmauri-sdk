![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

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

`FileFilter` combines the `FileStorageAdapter` storage backend with the
`GitFilterBase` helpers from `swarmauri_base`. The filter stores git-cleaned
objects beneath a local directory, deduplicating each payload by its SHA-256
digest and retrieving the bytes on smudge.

## Installation

Install the package with your preferred Python packaging tool:

```bash
pip install swarmauri_gitfilter_file
```

```bash
poetry add swarmauri_gitfilter_file
```

```bash
uv pip install swarmauri_gitfilter_file
```

## Usage

`FileFilter.from_uri` accepts `file://` URIs and resolves them to the directory
where objects will be stored. You can also instantiate `FileFilter` directly by
passing an `output_dir`.

```python
import tempfile
from pathlib import Path

from swarmauri_gitfilter_file import FileFilter

with tempfile.TemporaryDirectory() as tmpdir:
    uri = Path(tmpdir).as_uri()
    filt = FileFilter.from_uri(uri)
    oid = filt.clean(b"hello")
    assert oid.startswith("sha256:")
    assert filt.smudge(oid) == b"hello"
```

The returned object identifier includes the `sha256:` prefix, matching the
digest used to deduplicate objects on disk.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.