![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_evaluator_abstractmethods/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_evaluator_abstractmethods" alt="PyPI - Downloads"/></a>
    <a href="https://pypi.org/project/swarmauri_evaluator_abstractmethods/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_evaluator_abstractmethods" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_evaluator_abstractmethods/">
        <img src="https://img.shields.io/pypi/l/swarmauri_evaluator_abstractmethods" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_evaluator_abstractmethods/">
        <img src="https://img.shields.io/pypi/v/swarmauri_evaluator_abstractmethods?label=swarmauri_evaluator_abstractmethods&color=green" alt="PyPI - swarmauri_evaluator_abstractmethods"/></a>
</p>

---

# Swarmauri Evaluator Abstractmethods

`AbstractMethodsEvaluator` inspects Python source files to verify that abstract
base classes decorate their contract methods with `@abstractmethod`. The
evaluator is designed for automated program analysis within the Swarmauri
ecosystem and reports the exact lines that need attention together with summary
metrics.

## Features

- Parses Python modules into an AST to discover classes inheriting from
  `ABC` or any custom bases supplied through `abc_base_classes`.
- Flags methods on abstract classes that are missing the
  `@abstractmethod` decorator and records fully compliant methods for context.
- Ignores private (`_method`) and dunder (`__method__`) members by default to
  focus on the public interface; these rules can be toggled with
  `ignore_private` and `ignore_dunder`.
- Returns a detailed metadata payload containing compliance counts,
  per-method diagnostics, and an overall percentage score.
- Provides `aggregate_scores` to average multiple evaluation runs while
  combining their metadata such as total issues and compliance percentages.

## Installation

Install the evaluator with your preferred packaging tool:

```bash
pip install swarmauri_evaluator_abstractmethods
```

```bash
poetry add swarmauri_evaluator_abstractmethods
```

```bash
uv pip install swarmauri_evaluator_abstractmethods
```

## Configuration

Instantiate the evaluator with optional keyword arguments:

| Option | Default | Description |
| --- | --- | --- |
| `ignore_private` | `True` | Skip methods whose names begin with a single underscore. |
| `ignore_dunder` | `True` | Skip dunder methods such as `__init__`. |
| `abc_base_classes` | `["ABC", "abc.ABC"]` | Additional base class names that should be treated as abstract. |

## Evaluation Output

Calling `evaluate` returns `(score, metadata)` where `score` is the ratio of
properly decorated methods to the total number of methods that should be
abstract. `metadata` contains:

- `issues`: A list of dictionaries with file, line, class name, method name,
  whether the decorator is present, and a descriptive message. Fully compliant
  methods are included for context.
- `total_abstract_classes`, `total_methods`, `total_abstract_methods`, and
  `total_missing_decorators`: Counters summarizing the analysis.
- `percentage_compliant`: Convenience metric equal to `score * 100`.

## Usage Example

```python
import textwrap
from typing import Dict

from swarmauri_core.programs.IProgram import DiffType, IProgram
from swarmauri_evaluator_abstractmethods import AbstractMethodsEvaluator


class InMemoryProgram(IProgram):
    def __init__(self, files: Dict[str, str]):
        self._files = files

    def diff(self, other: IProgram) -> DiffType:
        return {}

    def apply_diff(self, diff: DiffType) -> IProgram:
        return self

    def validate(self) -> bool:
        return True

    def clone(self) -> IProgram:
        return InMemoryProgram(dict(self._files))

    def get_source_files(self) -> Dict[str, str]:
        return self._files


def main() -> None:
    program = InMemoryProgram(
        {
            "shapes.py": textwrap.dedent(
                """
                from abc import ABC, abstractmethod

                class Shape(ABC):
                    @abstractmethod
                    def area(self):
                        ...
                """
            ).strip(),
            "incomplete.py": textwrap.dedent(
                """
                from abc import ABC

                class InvalidShape(ABC):
                    def area(self):
                        ...
                """
            ).strip(),
        }
    )

    evaluator = AbstractMethodsEvaluator()
    score, metadata = evaluator.evaluate(program)

    print(f"Score: {score:.2f}")
    for issue in metadata["issues"]:
        if not issue["has_abstractmethod"]:
            print(f"{issue['file']}:{issue['line']} -> {issue['message']}")


if __name__ == "__main__":
    main()
```

**Output**

```
Score: 0.50
incomplete.py:4 -> Method 'area' in abstract class 'InvalidShape' should be decorated with @abstractmethod
```

The evaluator reports both compliant and non-compliant methods in
`metadata["issues"]`, allowing you to surface violations while still retaining
context about classes that already satisfy the contract.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md)
that will help you get started.