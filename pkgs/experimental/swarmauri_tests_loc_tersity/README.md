![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tests_loc_tersity/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tests_loc_tersity" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/swarmauri_tests_loc_tersity/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/swarmauri_tests_loc_tersity.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tests_loc_tersity/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tests_loc_tersity" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tests_loc_tersity/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tests_loc_tersity" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tests_loc_tersity/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tests_loc_tersity?label=swarmauri_tests_loc_tersity&color=green" alt="PyPI - swarmauri_tests_loc_tersity"/></a>
</p>

---

## Overview

`swarmauri_tests_loc_tersity` is a [pytest](https://docs.pytest.org/) plugin that
keeps modules small and readable. It scans a package for Python files and
asserts that each file stays under a configurable line‑of‑code (LOC) limit
(docstrings included). The default limit is **400 lines**.

The plugin runs in *parameterized* mode by default, turning every file into an
individual test case. You can also switch to an *aggregate* mode that reports
all failures as a single test.

## Installation

```bash
pip install swarmauri_tests_loc_tersity
```

`pytest` automatically discovers the plugin once it is installed.

## Usage

### Parameterized (default)

Run `pytest` normally to create one LOC check per Python file:

```bash
pytest
```

Example failure:

```
E   AssertionError: pkg/example.py has 425 lines (>400)
```

### Aggregate

Use the `--loc-mode=aggregate` flag to consolidate checks into one test that
lists every file exceeding the threshold:

```bash
pytest --loc-mode=aggregate
```

Example output:

```
E   pkg/example.py has 425 lines (>400)
E   pkg/other.py has 410 lines (>400)
```

### Customizing

* `--loc-root PATH` – directory to scan (defaults to the package root)
* `--loc-max-lines N` – change the maximum line count

```bash
pytest --loc-root=src --loc-max-lines=200
```

## License

Licensed under the [Apache 2.0 License](LICENSE).

