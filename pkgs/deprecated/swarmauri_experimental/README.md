![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_experimental/">
        <img src="https://static.pepy.tech/badge/swarmauri_experimental/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/deprecated/swarmauri_experimental/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/deprecated/swarmauri_experimental.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_experimental/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14%20%7C%203.15-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_experimental/">
        <img src="https://img.shields.io/pypi/l/swarmauri_experimental" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_experimental/">
        <img src="https://img.shields.io/pypi/v/swarmauri_experimental?label=swarmauri_experimental&color=green" alt="PyPI - swarmauri_experimental"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# Swarmauri Experimental

> **Deprecated package — no further maintenance or compatibility work planned.**
>
> Experimental components are now released as standalone distributions. Migrate
> away from the `swarmauri_experimental` umbrella. Importing it emits a
> `DeprecationWarning`. Existing installations remain available for migration.

## Features

- Legacy experimental components retained for existing applications.
- No new features or guarantees for optional backend compatibility.

## Migration

Find the maintained standalone distribution for each component in
[`pkgs/experimental`](../../experimental) or
[`pkgs/standards`](../../standards). Follow that package's installation and usage
instructions, replace umbrella imports, and validate your application before
removing `swarmauri_experimental`. Components without a maintained replacement
should be retired or maintained separately.

## Legacy installation

For applications that still require the deprecated package:

```console
uv pip install swarmauri_experimental
pip install swarmauri_experimental
```

Python 3.10–3.15 metadata describes the default package. Optional `vision` and
`manifold` extras depend on separately supported backends. TensorFlow currently
prevents the vision extra from installing on Python 3.14 and 3.15; those optional
workflows are not certified by the default unit tests.



