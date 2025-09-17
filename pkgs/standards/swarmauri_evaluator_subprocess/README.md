![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

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

`SubprocessEvaluator` executes programs inside sandboxed subprocesses while
enforcing CPU, memory, and file size quotas. It captures stdout/stderr, tracks
exit codes, and returns a normalized score plus structured metadata describing
each run.

## Highlights

- Apply CPU timeouts, memory ceilings, file size limits, and process count caps
  before user code starts (`resource.setrlimit`).
- Automatically choose the appropriate command: launch executables directly or
  wrap Python and shell scripts with the correct interpreter.
- Compare stdout against an `expected_output` string and annotate mismatches in
  the result metadata.
- Record execution context (`command`, `args`, `working_dir`) alongside
  collected streams for easy debugging.
- Aggregate multiple runs with reason counts, timeout rates, and success rates
  via `aggregate_scores`.

## Installation

Pick the tool that matches your workflow:

```bash
# pip
pip install swarmauri_evaluator_subprocess

# Poetry
poetry add swarmauri_evaluator_subprocess

# uv
uv add swarmauri_evaluator_subprocess
```

## Quickstart

The example below writes a temporary Python script to disk, wraps it in a small
`IProgram` implementation, and evaluates it inside a subprocess. The evaluator
returns `1.0` when the exit code is in `success_exit_codes` and, when provided,
stdout matches `expected_output`.

```python
from pathlib import Path
import tempfile

from swarmauri_evaluator_subprocess import SubprocessEvaluator
from swarmauri_core.programs.IProgram import DiffType, IProgram


class ScriptProgram(IProgram):
    """Minimal IProgram wrapper for a script stored on disk."""

    def __init__(self, path: Path):
        self._path = Path(path)

    # Required IProgram interface methods -------------------------------
    def diff(self, other: IProgram) -> DiffType:  # pragma: no cover - example
        return {}

    def apply_diff(self, diff: DiffType) -> "ScriptProgram":  # pragma: no cover
        return ScriptProgram(self._path)

    def validate(self) -> bool:  # pragma: no cover
        return self._path.exists()

    def clone(self) -> "ScriptProgram":  # pragma: no cover
        return ScriptProgram(self._path)

    # Methods consumed by SubprocessEvaluator ---------------------------
    def get_path(self) -> str:
        return str(self._path)

    def is_executable(self) -> bool:
        return False


def run_example(expected_output: str = "hello from subprocess\n"):
    evaluator = SubprocessEvaluator(timeout=5)

    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = Path(tmpdir) / "echo.py"
        script_path.write_text("print('hello from subprocess')\n", encoding="utf-8")

        program = ScriptProgram(script_path)

        score, metadata = evaluator.evaluate(
            program,
            expected_output=expected_output,
        )

    return score, metadata


def main():
    score, metadata = run_example()
    print("Score:", score)
    print("Stdout:", metadata["stdout"].strip())
    print("Reason:", metadata["reason"])


if __name__ == "__main__":
    main()
```

### Evaluation options

`SubprocessEvaluator.evaluate(program, **kwargs)` accepts runtime controls in
addition to the evaluator's model fields:

| Argument         | Description |
| ---------------- | ----------- |
| `args`           | List of command-line arguments appended to the prepared command. |
| `input_data`     | String provided on stdin; useful for feeding sample input. |
| `expected_output`| Optional stdout string; mismatches lower the score to `0.7`. |
| `timeout`        | Overrides the evaluator's `timeout` for a single run. |

### Returned metadata

Each evaluation returns `(score, metadata)` where `metadata` always contains:

- `stdout`, `stderr`, and `exit_code` from the subprocess.
- `timed_out` flag plus a human-readable `reason` such as `success`,
  `timeout`, or `exit_code_<value>`.
- `command`, `args`, and `working_dir` to show how the program was launched.
- `execution_time` (seconds) measured by the evaluator wrapper.

When aggregating multiple runs, `aggregate_scores` adds `reason_counts`,
`timeout_rate`, `success_rate`, and `total_executions` to the combined
metadata so callers can evaluate fleet-wide behavior.

