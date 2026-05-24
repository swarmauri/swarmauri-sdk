![Swarmauri Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/swarmauri_sdk_brand.png)

<p align="center">
    <a href="https://pepy.tech/project/swarmauri_tests_griffe/">
        <img src="https://static.pepy.tech/badge/swarmauri_tests_griffe/month" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tests_griffe/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tests_griffe.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_tests_griffe/">
        <img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_tests_griffe/">
        <img src="https://img.shields.io/pypi/l/swarmauri_tests_griffe" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_tests_griffe/">
        <img src="https://img.shields.io/pypi/v/swarmauri_tests_griffe?label=swarmauri_tests_griffe&color=green" alt="PyPI - swarmauri_tests_griffe"/></a>
    <a href="https://discord.gg/N4UpBuQv8T">
        <img src="https://img.shields.io/badge/Discord-Join%20Chat-5865F2?logo=discord&logoColor=white" alt="Discord"/></a></p>

# swarmauri_tests_griffe

`swarmauri_tests_griffe` is a [pytest](https://pytest.org) plugin that loads your
package metadata with [Griffe](https://github.com/mkdocstrings/griffe). The
plugin converts any warnings generated during inspection into failing tests so
that documentation, annotations, and runtime signatures stay in sync across the
Swarmauri ecosystem.

## Features

- **Python 3.10â€“3.12 coverage** â€“ verified across the supported Swarmauri
  runtime range so you can keep consistent quality gates on every maintained
  interpreter.
- **Warning-to-test enforcement** â€“ automatically escalates Griffe warnings to
  failing pytest checks to stop documentation drift before it ships.
- **Zero-config discovery** â€“ the plugin registers as a pytest entry point and
  loads without additional setup once installed.
- **Flexible targeting** â€“ tune the inspection scope with command-line flags or
  persistent `pyproject.toml` settings.

## Installation

Choose the installer that best fits your workflow:

### Using `uv`

```bash
uv add swarmauri-tests-griffe
```

### Using `pip`

```bash
pip install swarmauri-tests-griffe
```

Both commands add the plugin as a dependency of your project. Because the plugin
uses pytest entry points, it is automatically discovered the next time your test
suite runsâ€”no manual configuration required.

> **Supported Python versions:** The plugin is tested and published for Python
> 3.10, 3.11, and 3.12 across the Swarmauri platform.

## Usage

After installation, execute your test suite as normal and a dynamic Griffe check
is injected for each configured package. By default, the package defined in
`pyproject.toml` is inspected. You can target additional packages or limit the
scope with command-line options:

```bash
pytest --griffe-package your_package --griffe-package another_package
```

Each `--griffe-package` argument adds a module to the inspection list. If
Griffe produces warnings while processing any module, the corresponding dynamic
test fails and the collected warnings are rendered in the pytest output, making
it easy to pinpoint the files that need attention.

### Configuring defaults

For larger projects, keep the configuration in `pyproject.toml` to avoid
repeating command-line flags:

```toml
[tool.pytest.ini_options]
addopts = "--griffe-package swarmauri_core --griffe-package swarmauri_tests_griffe"
```

With the options saved, every pytest run enforces the same quality gates across
your codebase without extra setup.


