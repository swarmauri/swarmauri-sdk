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

`tigrbl-tests` packages the test suite, fixtures, and examples used to validate
and teach the Tigrbl framework.

## Features ✨

- ✅ Includes tests used to validate framework behavior and API contracts.
- 📚 Includes example-first lesson tests for implementers.
- 🧰 Installs test dependencies for async API testing workflows.

## Installation 📦

**uv**

```bash
uv add "tigrbl[tests]"
```

**pip**

```bash
pip install "tigrbl[tests]"
```

Install `tigrbl-tests` directly when you only need the test package:

```bash
uv add tigrbl-tests
```

```bash
pip install tigrbl-tests
```

## Usage 🧭

### Maintainer-facing tests (framework validation)

These tests verify behavior for Tigrbl maintainers: model internals, routing,
hooks, diagnostics, and contract stability.

```bash
cd /workspace/swarmauri-sdk/pkgs
uv run --package tigrbl-tests --directory standards/tigrbl_tests pytest tests
```

### Implementer-facing tests (learning examples)

These tests are structured as lessons for implementers building Tigrbl apps.
They emphasize explicit model definitions, API setup, and client calls.

```bash
cd /workspace/swarmauri-sdk/pkgs
uv run --package tigrbl-tests --directory standards/tigrbl_tests pytest examples
```

## Tests at a glance

- `tests/`: maintainers' validation suite for the framework itself.
- `examples/`: implementers' learning lessons and pedagogical walkthroughs.

See `examples/README.md` for module-by-module lesson descriptions.
