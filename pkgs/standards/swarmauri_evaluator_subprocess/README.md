![Swamauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_evaluator_subprocess/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_evaluator_subprocess" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_evaluator_subprocess/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/standards/swarmauri_evaluator_subprocess.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_evaluator_subprocess/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_evaluator_subprocess" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_evaluator_subprocess/">
        <img src="https://img.shields.io/pypi/l/swarmauri_evaluator_subprocess" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_evaluator_subprocess/">
        <img src="https://img.shields.io/pypi/v/swarmauri_evaluator_subprocess?label=swarmauri_evaluator_subprocess&color=green" alt="PyPI - swarmauri_evaluator_subprocess"/></a>
</p>

---

# Swarmauri Evaluator Subprocess

A subprocess-based evaluator for executing and measuring program performance in isolated subprocesses.

## Installation

```bash
pip install swarmauri_evaluator_subprocess
```

## Usage

```python
from swarmauri_evaluator_subprocess import SubprocessEvaluator

# `program` should implement `get_path()` and `is_executable()` and point to a script on disk.
evaluator = SubprocessEvaluator()
score, metadata = evaluator.evaluate(
    program,
    expected_output="hello\n",
)

print("Score:", score)
print("Stdout:", metadata["stdout"])
```

