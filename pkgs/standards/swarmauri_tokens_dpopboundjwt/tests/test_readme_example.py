from __future__ import annotations

import re
from pathlib import Path

import pytest

EXAMPLE_MARKER = "# README example: mint and verify a DPoP-bound JWT"


@pytest.mark.example
def test_readme_example_executes(monkeypatch: pytest.MonkeyPatch) -> None:
    """Execute the README example to ensure it stays up-to-date."""

    tests_dir = Path(__file__).resolve().parent
    package_dir = tests_dir.parent
    repo_root = package_dir.parent.parent.parent

    # Ensure local workspace packages are importable when running inside the mono-repo.
    for candidate in (
        package_dir,
        repo_root / "pkgs" / "core",
        repo_root / "pkgs" / "base",
    ):
        monkeypatch.syspath_prepend(str(candidate))

    readme = package_dir / "README.md"
    readme_text = readme.read_text(encoding="utf-8")

    code_blocks = re.findall(r"```python\n(.*?)```", readme_text, flags=re.DOTALL)
    example_block = next(
        (block for block in code_blocks if EXAMPLE_MARKER in block),
        None,
    )
    assert example_block is not None, "README example block not found"

    exec(compile(example_block, str(readme), "exec"), {"__name__": "__main__"})
