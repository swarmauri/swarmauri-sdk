![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri-tests-griffe/">
        <img src="https://img.shields.io/pypi/dm/swarmauri-tests-griffe" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tests_griffe/">
        <img src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/community/swarmauri_tests_griffe.svg" alt="Repository Hits"/></a>
    <a href="https://pypi.org/project/swarmauri-tests-griffe/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri-tests-griffe" alt="PyPI - Supported Python Versions"/></a>
    <a href="https://pypi.org/project/swarmauri-tests-griffe/">
        <img src="https://img.shields.io/pypi/l/swarmauri-tests-griffe" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri-tests-griffe/">
        <img src="https://img.shields.io/pypi/v/swarmauri-tests-griffe?label=swarmauri_tests_griffe&color=green" alt="PyPI - Latest Release"/></a>
</p>

---

# swarmauri_tests_griffe

`swarmauri_tests_griffe` is a [pytest](https://pytest.org) plugin that loads your
package metadata with [Griffe](https://github.com/mkdocstrings/griffe). The
plugin converts any warnings generated during inspection into failing tests so
that documentation, annotations, and runtime signatures stay in sync across the
Swarmauri ecosystem.

## Features

- **Python 3.10–3.12 coverage** – verified across the supported Swarmauri
  runtime range so you can keep consistent quality gates on every maintained
  interpreter.
- **Warning-to-test enforcement** – automatically escalates Griffe warnings to
  failing pytest checks to stop documentation drift before it ships.
- **Zero-config discovery** – the plugin registers as a pytest entry point and
  loads without additional setup once installed.
- **Flexible targeting** – tune the inspection scope with command-line flags or
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
suite runs—no manual configuration required.

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
