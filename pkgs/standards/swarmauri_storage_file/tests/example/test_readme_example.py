"""Execute the README usage example to ensure it stays accurate."""

from __future__ import annotations

import sys
import textwrap
from pathlib import Path

import pytest


PACKAGE_DIR = Path(__file__).resolve().parents[2]
if str(PACKAGE_DIR) not in sys.path:  # pragma: no cover - import guard
    sys.path.insert(0, str(PACKAGE_DIR))


def _extract_usage_code(readme: Path) -> str:
    """Return the first Python code block under the ``Usage`` heading."""

    lines = readme.read_text(encoding="utf-8").splitlines()
    in_usage = False
    in_code = False
    code_lines: list[str] = []

    for line in lines:
        if not in_usage:
            if line.strip() == "## Usage":
                in_usage = True
            continue

        if not in_code:
            if line.startswith("## "):
                break
            if line.strip().startswith("```python"):
                in_code = True
            continue

        if line.strip().startswith("```"):
            break

        code_lines.append(line)

    if not code_lines:
        raise AssertionError("Usage example code block not found in README.md")

    return textwrap.dedent("\n".join(code_lines)).strip()


@pytest.mark.example
def test_readme_usage_example(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Run the README example and assert it produces the expected artifacts."""

    readme = PACKAGE_DIR / "README.md"
    code = _extract_usage_code(readme)

    monkeypatch.chdir(tmp_path)

    namespace: dict[str, object] = {}
    exec(code, namespace)

    workspace = namespace["workspace"]
    assert isinstance(workspace, Path)
    assert workspace.exists()
    assert workspace.is_dir()
    assert workspace.is_relative_to(tmp_path.resolve())

    artifact = workspace / "example.txt"
    assert artifact.exists()
    assert artifact.read_text(encoding="utf-8") == "hello world"

    assert namespace["downloaded"] == "hello world"
    assert namespace["keys"] == ["example.txt"]

    uri = namespace["uri"]
    root_uri = namespace["root_uri"]
    assert isinstance(uri, str)
    assert isinstance(root_uri, str)
    assert uri.endswith("example.txt")
    assert root_uri.startswith("file://")
