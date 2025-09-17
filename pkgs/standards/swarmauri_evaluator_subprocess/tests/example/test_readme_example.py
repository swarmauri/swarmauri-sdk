"""Execute the Quickstart snippet from the README to ensure it stays up-to-date."""

from __future__ import annotations

import re
import textwrap
from pathlib import Path

import pytest


README_PATH = Path(__file__).resolve().parents[2] / "README.md"


def _extract_first_python_block() -> str:
    readme_text = README_PATH.read_text(encoding="utf-8")
    matches = re.findall(r"```python\n(.*?)```", readme_text, flags=re.DOTALL)
    if not matches:
        raise AssertionError("README does not contain a Python example block")
    return textwrap.dedent(matches[0])


@pytest.mark.example
def test_readme_quickstart_example_runs(capsys):
    code = _extract_first_python_block()

    namespace: dict[str, object] = {"__name__": "__README__"}
    exec(code, namespace)  # noqa: S102 - intentional execution of documentation example

    run_example = namespace.get("run_example")
    assert callable(run_example), "README example must define run_example()"

    score, metadata = run_example()

    assert score == 1.0
    assert metadata["reason"] == "success"
    assert metadata["stdout"] == "hello from subprocess\n"

    main = namespace.get("main")
    assert callable(main), "README example must define main()"

    main()
    captured = capsys.readouterr()
    assert "Score:" in captured.out
    assert "Stdout:" in captured.out
    assert "Reason:" in captured.out
