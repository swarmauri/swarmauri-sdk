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

Evaluator that detects and penalizes usage of the `typing.Any` type in Python source files.

## Features

- Recursively scans every `.py` file under `program.path`, falling back to the current
  working directory when that attribute is missing.
- Uses the Python AST to capture imports and annotations plus a regex pass to
  backfill edge cases (e.g., syntax errors).
- Deducts `penalty_per_occurrence` (default `0.1`) for each finding and caps the
  deduction at `max_penalty` (default `1.0`), yielding a normalized score between `0.0`
  and `1.0` where higher is better.
- Returns rich metadata that lists the number of files analyzed, the total `Any`
  occurrences, and per-file line numbers and snippets to accelerate remediation.

## Installation

Choose the tool that best fits your workflow:

```bash
# pip
pip install swarmauri_evaluator_anyusage

# Poetry
poetry add swarmauri_evaluator_anyusage

# uv
uv add swarmauri_evaluator_anyusage
```

## Usage

```python
from pathlib import Path

from swarmauri_base.programs.ProgramBase import ProgramBase
from swarmauri_evaluator_anyusage import AnyTypeUsageEvaluator


workspace = Path("path/to/project")

program = ProgramBase()
program.name = workspace.name
program.path = str(workspace)  # AnyTypeUsageEvaluator walks this directory on disk

evaluator = AnyTypeUsageEvaluator(penalty_per_occurrence=0.1, max_penalty=1.0)
score, metadata = evaluator.evaluate(program)

print(f"Score: {score:.2f}")
print("Files analyzed:", metadata["files_analyzed"])
print("Any usages:", metadata["total_any_occurrences"])

for report in metadata["detailed_occurrences"]:
    print("-", report["file"])
    for occurrence in report["occurrences"]:
        print(f"  line {occurrence['line']}: {occurrence['context']}")

# If you already depend on `swarmauri_standard`, import
# `from swarmauri_standard.programs.Program import Program` and replace the
# ProgramBase construction above with `Program.from_workspace(workspace)`
# before setting `program.path` to keep the on-disk directory in sync with
# your Program content.
```

### Metadata reference

The evaluation metadata contains:

- `files_analyzed`: Number of Python files inspected.
- `total_any_occurrences`: Count of detected `Any` usages across all files.
- `penalty_applied`: The aggregate deduction applied to the score.
- `detailed_occurrences`: A list with one entry per file containing the absolute path
  and the line/context pairs for each finding. Multiple entries can share a line number
  when both the parameter and return annotations use `Any`; the `context` value explains
  the exact usage (import, parameter annotation, return annotation, etc.).
- `execution_time`: Added by `EvaluatorBase` to show how long the evaluation took.

Use these fields to build dashboards, enforce quality gates, or guide manual reviews.

## Want to help?

If you want to contribute to swarmauri-sdk, read up on our
[guidelines for contributing](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md)
that will help you get started.
