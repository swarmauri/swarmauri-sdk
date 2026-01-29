![Tigrbl Logo](https://github.com/swarmauri/swarmauri-sdk/blob/a170683ecda8ca1c4f912c966d4499649ffb8224/assets/tigrbl.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/tigrbl-tests/">
        <img src="https://img.shields.io/pypi/dm/tigrbl-tests" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/tigrbl_tests/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/tigrbl_tests.svg"/></a>
    <a href="https://pypi.org/project/tigrbl-tests/">
        <img src="https://img.shields.io/pypi/pyversions/tigrbl-tests" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/tigrbl-tests/">
        <img src="https://img.shields.io/pypi/l/tigrbl-tests" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/tigrbl-tests/">
        <img src="https://img.shields.io/pypi/v/tigrbl-tests?label=tigrbl-tests&color=green" alt="PyPI - tigrbl-tests"/></a>
</p>

---

# Tigrbl Tests 🧪

Test suite distribution for the Tigrbl framework. Install this package to get
Tigrbl's curated test fixtures and test-only dependencies without bloating the
base `tigrbl` install.

## Features ✨

- ✅ Bundled unit, integration, and performance test suites for Tigrbl.
- 🧰 Test dependencies prewired for pytest + async tooling.
- 🧭 Pairs cleanly with `tigrbl[tests]` for a one-command setup.

## Installation 📦

**uv**

```bash
uv add "tigrbl[tests]"
```

**pip**

```bash
pip install "tigrbl[tests]"
```

You can also install the test package directly if you only want the suite:

```bash
uv add tigrbl-tests
```

```bash
pip install tigrbl-tests
```

## Usage 🧭

Run the tests from the `pkgs` directory to mirror the monorepo workflow:

```bash
cd /workspace/swarmauri-sdk/pkgs
uv run --package tigrbl --directory standards/tigrbl pytest
```

Use pytest selectors to focus on specific suites:

```bash
pytest standards/tigrbl_tests/tests/unit
```

## Examples Curriculum 📚

The `examples/` directory contains downstream-facing pytest lessons that
demonstrate how to implement Tigrbl in real applications. These lessons are
organized as a multi-module curriculum with uvicorn-backed usage examples and
system diagnostics validation. See the full curriculum plan for the learning
sequence and module descriptions.[^tigrbl-examples]
Run the examples from the `pkgs` directory:

```bash
uv run --package tigrbl-tests --directory standards/tigrbl_tests pytest examples
```

[^tigrbl-examples]: examples/README.md
