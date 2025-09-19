from __future__ import annotations

import pathlib
import re
import textwrap

import pytest


def _readme_path() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[2] / "README.md"


def _extract_readme_example() -> str:
    readme_text = _readme_path().read_text(encoding="utf-8")
    match = re.search(r"```python\n(?P<code>.*?)\n```", readme_text, re.DOTALL)
    if not match:  # pragma: no cover - defensive guard
        raise AssertionError("README is missing the expected python example block.")
    return textwrap.dedent(match.group("code")).strip()


@pytest.mark.example
def test_readme_example_executes(capsys):
    namespace: dict[str, object] = {"__name__": "__main__"}
    exec(compile(_extract_readme_example(), str(_readme_path()), "exec"), namespace)
    captured = capsys.readouterr()
    assert "Signature valid? True" in captured.out
