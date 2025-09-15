![Swamauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_evaluator_externalimports/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_evaluator_externalimports" alt="PyPI - Downloads"/>
    </a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_evaluator_externalimports/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_evaluator_externalimports.svg"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_evaluator_externalimports/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_evaluator_externalimports" alt="PyPI - Python Version"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_evaluator_externalimports/">
        <img src="https://img.shields.io/pypi/l/swarmauri_evaluator_externalimports" alt="PyPI - License"/>
    </a>
    <br />
    <a href="https://pypi.org/project/swarmauri_evaluator_externalimports/">
        <img src="https://img.shields.io/pypi/v/swarmauri_evaluator_externalimports?label=swarmauri_evaluator_externalimports&color=green" alt="PyPI - swarmauri_evaluator_externalimports"/>
    </a>
</p>

---

# Swarmauri Evaluator External Imports

Evaluator that detects and penalizes non–standard-library imports in Python source files.

## Purpose

This evaluator helps gauge dependency hygiene by examining import statements and flagging modules that are not part of the Python standard library.

## Installation

```bash
pip install swarmauri_evaluator_externalimports
```

## Usage

```python
from swarmauri_evaluator_externalimports import ExternalImportsEvaluator

evaluator = ExternalImportsEvaluator()
score, details = evaluator.evaluate(program)  # `program` is an instance of swarmauri_core.programs.IProgram
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md).
