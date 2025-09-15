![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tests_pylicense/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tests_pylicense" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/swarmauri_tests_pylicense/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/swarmauri_tests_pylicense.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tests_pylicense/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tests_pylicense" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tests_pylicense/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tests_pylicense" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tests_pylicense/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tests_pylicense?label=swarmauri_tests_pylicense&color=green" alt="PyPI - swarmauri_tests_pylicense"/></a>
</p>

---

## Overview

`swarmauri_tests_pylicense` is a [pytest](https://docs.pytest.org/) plugin that
scans a package's full dependency tree and ensures each dependency declares a
license. The plugin resolves dependencies recursively, checking every
transitive requirement. It inspects both the `License` metadata field and
any `Classifier` entries that declare a license.

By default, the plugin runs in *parameterized* mode which creates one test per
dependency. An *aggregate* mode is also available that reports all missing
licenses in a single test.

## Installation

```bash
pip install swarmauri_tests_pylicense
```

`pytest` automatically discovers the plugin once it is installed.

## Usage

### Parameterized (default)

Run `pytest` with the package name to scan its dependency licenses:

```bash
pytest --pylicense-package=<your-package>
```

### Aggregate

Use the `--pylicense-mode=aggregate` flag to consolidate checks into one test:

```bash
pytest --pylicense-package=<your-package> --pylicense-mode=aggregate
```

### Allow and Disallow Lists

To restrict acceptable licenses, provide a comma-separated allow list or
disallow list. These can be passed via command-line options or environment
variables.

Command-line:

```bash
pytest --pylicense-package=<your-package> --pylicense-allow-list=MIT,Apache-2.0
pytest --pylicense-package=<your-package> --pylicense-disallow-list=GPL
```

Environment variables:

```bash
export PYLICENSE_ALLOW_LIST="MIT,Apache-2.0"
export PYLICENSE_DISALLOW_LIST="GPL"
pytest --pylicense-package=<your-package>
```

If both are provided, any license not in the allow list or explicitly present
in the disallow list will cause a test failure. By default, all licenses are
allowed and none are disallowed.

## License

Licensed under the [Apache 2.0 License](LICENSE).
