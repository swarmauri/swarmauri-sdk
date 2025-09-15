![Swamauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_evaluatorpool_accessibility/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_evaluatorpool_accessibility" alt="PyPI - Downloads"/>
    </a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_evaluatorpool_accessibility/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_evaluatorpool_accessibility.svg"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_evaluatorpool_accessibility/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_evaluatorpool_accessibility" alt="PyPI - Python Version"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_evaluatorpool_accessibility/">
        <img src="https://img.shields.io/pypi/l/swarmauri_evaluatorpool_accessibility" alt="PyPI - License"/>
    </a>
    <a href="https://pypi.org/project/swarmauri_evaluatorpool_accessibility/">
        <img src="https://img.shields.io/pypi/v/swarmauri_evaluatorpool_accessibility?label=swarmauri_evaluatorpool_accessibility&color=green" alt="PyPI - swarmauri_evaluatorpool_accessibility"/>
    </a>
</p>

---

# Swarmauri Evaluatorpool Accessibility

A package providing accessibility and readability evaluators for Swarmauri, aggregating classic readability metrics into a single pool.

## Installation

```bash
pip install swarmauri_evaluatorpool_accessibility
```

## Usage

```python
from swarmauri_evaluatorpool_accessibility.AccessibilityEvaluatorPool import AccessibilityEvaluatorPool
from swarmauri_standard.programs.Program import Program

program = Program(content={"example.txt": "This is a simple sentence. Here is another one."})
pool = AccessibilityEvaluatorPool()
result = pool.evaluate(program)

print(result.score)       # aggregated accessibility score
print(result.metadata)    # details from individual evaluators
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md) that will help you get started.

