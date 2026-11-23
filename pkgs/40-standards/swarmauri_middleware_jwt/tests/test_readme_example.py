"""Tests for the README example."""

from __future__ import annotations

import pathlib

import pytest


README_PATH = pathlib.Path(__file__).resolve().parents[1] / "README.md"


def _extract_first_python_block() -> str:
    contents = README_PATH.read_text(encoding="utf-8")
    lines: list[str] = []
    in_block = False
    for raw_line in contents.splitlines():
        stripped = raw_line.strip()
        if not in_block and stripped.startswith("```python"):
            in_block = True
            continue
        if in_block and stripped.startswith("```"):
            break
        if in_block:
            lines.append(raw_line)
    if not lines:
        raise AssertionError("README is missing a Python example block")
    return "\n".join(lines)


@pytest.mark.example
def test_readme_example_runs() -> None:
    namespace: dict[str, object] = {"__name__": "__test__"}
    code = _extract_first_python_block()

    exec(compile(code, str(README_PATH), "exec"), namespace)  # noqa: S102

    assert isinstance(namespace["token"], str)
    middleware = namespace["jwt_middleware"]
    assert middleware.verify_token(namespace["token"])["sub"] == "demo-user"
