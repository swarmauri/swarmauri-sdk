![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_evaluator_anyusage/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_evaluator_anyusage" alt="PyPI - Downloads"/>
    </a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_evaluator_anyusage/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_evaluator_anyusage.svg"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_evaluator_anyusage/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_evaluator_anyusage" alt="PyPI - Python Version"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_evaluator_anyusage/">
        <img src="https://img.shields.io/pypi/l/swarmauri_evaluator_anyusage" alt="PyPI - License"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_evaluator_anyusage/">
        <img src="https://img.shields.io/pypi/v/swarmauri_evaluator_anyusage?label=swarmauri_evaluator_anyusage&color=green" alt="PyPI - swarmauri_evaluator_anyusage"/>
    </a>
</p>

---

# Swarmauri Evaluator AnyUsage

Evaluator that detects and penalizes use of the `Any` type in Python code.

## Features

- Flags `typing.Any` occurrences across your codebase.
- Produces a penalty score proportional to the number of findings.
- Reports file names and line numbers for quick remediation.

## Installation

```bash
pip install swarmauri_evaluator_anyusage
```

## Usage

```python
from swarmauri_evaluator_anyusage import AnyTypeUsageEvaluator

# 'program' is any swarmauri_core Program pointing to your source files.
evaluator = AnyTypeUsageEvaluator()
score, metadata = evaluator.evaluate(program)
print(score, metadata)
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md)
that will help you get started.
