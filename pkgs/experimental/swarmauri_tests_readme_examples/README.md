![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_tests_readme_examples/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_tests_readme_examples" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/swarmauri_tests_readme_examples/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/swarmauri_tests_readme_examples.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tests_readme_examples/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_tests_readme_examples" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tests_readme_examples/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tests_readme_examples" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tests_readme_examples/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tests_readme_examples?label=swarmauri_tests_readme_examples&color=green" alt="PyPI - Version"/></a>
</p>

---

## Overview

`swarmauri_tests_readme_examples` is a [pytest](https://docs.pytest.org/) plugin that
turns Markdown code blocks into executable tests. It scans README (or other
documentation) files for Python examples and verifies that every runnable block
still executes successfully. This keeps documentation trustworthy without
hand-maintained `test_readme_example.py` scaffolding.

The plugin works out of the box for Python code blocks (` ```python `, ` ```py `,
` ```pycon `) and exposes command-line flags and `pyproject.toml` settings so you can
fine-tune which files and languages are exercised.

## Installation

```bash
pip install swarmauri_tests_readme_examples
```

`pytest` discovers the plugin automatically after installation.

## Quick Start

Run `pytest` as usual to execute every Python code block in `README.md`:

```bash
pytest
```

Sample failure output:

```
E   README.md::block-3 raised ValueError('boom')
```

## Configuration

You can control the scan through CLI options or `pyproject.toml`:

* `--readme-files` – comma/newline separated Markdown files (default: `README.md`)
* `--readme-languages` – languages to execute (default: `python`, `py`, `pycon`)
* `--readme-mode` – `parameterized` (default) or `aggregate`
* `--readme-skip-markers` – comment markers that skip a block when they appear on the first non-empty line

`pyproject.toml` example (under `[tool.pytest.ini_options]`):

```toml
[tool.pytest.ini_options]
readme_files = """
    README.md
    docs/guide.md
"""
readme_languages = """
    python
    py
"""
readme_mode = "aggregate"
readme_skip_markers = """
    # pytest: skip-example
    # docs: skip
"""
```

## Skipping Blocks

Place one of the configured skip markers on the first non-empty line to leave a
code block out of execution:

````markdown
```python
# pytest: skip-example
print("shown in docs, ignored in tests")
```
````

## Aggregate Mode

Switch to `--readme-mode=aggregate` (or set `readme_mode = "aggregate"`) to
collapse all README checks into a single pytest item that aggregates every
failure message. This is handy when you want a brief summary rather than many
individual tests.

## License

Licensed under the [Apache 2.0 License](LICENSE).
