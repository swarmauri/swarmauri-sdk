![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

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

`ExternalImportsEvaluator` gauges dependency hygiene by walking the Python
sources referenced by a [`swarmauri_core.programs.IProgram`](https://github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/core/swarmauri_core)
and flagging modules that are not part of the Python standard library.

## What it does

1. Recursively walks every `.py` file beneath `program.path`.
2. Parses each file's abstract syntax tree to collect `import` and
   `from ... import ...` statements.
3. Compares imported modules against the Python standard library (including
   built-ins and a curated set of commonly used packages).
4. Returns both a score and metadata describing any external dependencies that
   were found.

### How scoring works

- The evaluator starts at a perfect score of **1.0**.
- Each unique external module subtracts **0.1** from the score.
- The score never drops below **0.0** regardless of how many modules are
  flagged.

### Metadata provided

`evaluate` returns the score alongside a dictionary with:

- `total_imports`: Count of all import statements encountered.
- `external_imports_count`: Number of non-standard imports detected.
- `unique_external_modules`: How many distinct external modules were used.
- `external_modules`: A list of the external module names.
- `external_imports_details`: Rich per-import entries containing the module,
  alias, line number, import type, and whether the module was considered
  standard.
- `files_analyzed` and `python_files`: Insights into the scan coverage.
- `execution_time`: Added by `EvaluatorBase` to show runtime of the analysis.

## Installation

Pick the workflow that matches your toolchain:

```bash
# pip
pip install swarmauri_evaluator_externalimports

# Poetry
poetry add swarmauri_evaluator_externalimports

# uv (install the tool if you have not already)
curl -Ls https://astral.sh/uv/install.sh | sh
uv add swarmauri_evaluator_externalimports
```

## Example

The snippet below creates a temporary project, evaluates it, and prints the
results. You can drop it into a file such as `example.py` and run
`python example.py`.

```python
from pathlib import Path
import tempfile
from typing import Any

from swarmauri_core.programs.IProgram import IProgram
from swarmauri_evaluator_externalimports import ExternalImportsEvaluator


class DirectoryProgram(IProgram):
    """Minimal IProgram implementation backed by a filesystem path."""

    def __init__(self, path: str):
        self.path = path

    def diff(self, other: "IProgram"):
        raise NotImplementedError("Diffing is outside the scope of this example")

    def apply_diff(self, diff: Any) -> "IProgram":
        raise NotImplementedError("Diffing is outside the scope of this example")

    def validate(self) -> bool:
        return True

    def clone(self) -> "IProgram":
        return DirectoryProgram(self.path)


def evaluate_example() -> tuple[float, dict[str, Any]]:
    evaluator = ExternalImportsEvaluator()

    with tempfile.TemporaryDirectory() as workdir:
        project = Path(workdir)
        project.joinpath("app.py").write_text(
            """import os\nimport numpy\n\nprint(os.name, numpy.__version__)\n""",
            encoding="utf-8",
        )

        program = DirectoryProgram(workdir)
        score, details = evaluator.evaluate(program)

        print("Score:", score)
        print("External modules:", sorted(details["external_modules"]))
        return score, details


if __name__ == "__main__":
    evaluate_example()
```

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our [guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/CONTRIBUTING.md).
