"""Execute the README quickstart example to ensure it stays runnable."""

from __future__ import annotations

from pathlib import Path

import pytest


README_PATH = Path(__file__).resolve().parents[2] / "README.md"


def _extract_quickstart_code() -> str:
    text = README_PATH.read_text(encoding="utf-8")
    lines = text.splitlines()

    in_quickstart = False
    in_code = False
    code_lines: list[str] = []

    for line in lines:
        if line.strip().lower() == "## quickstart":
            in_quickstart = True
            continue

        if in_quickstart:
            if line.startswith("```python"):
                in_code = True
                continue
            if line.startswith("```") and in_code:
                break
            if in_code:
                code_lines.append(line)
                continue
            if line.startswith("## "):
                break

    if not code_lines:
        raise AssertionError("Quickstart python example not found in README.md")

    return "\n".join(code_lines)


@pytest.mark.example
def test_readme_quickstart_example_runs() -> None:
    code = _extract_quickstart_code()
    namespace: dict[str, object] = {}
    exec(compile(code, str(README_PATH), "exec"), namespace)

    certificate = namespace.get("certificate_pem")
    assert isinstance(certificate, bytes)
    assert certificate.startswith(b"-----BEGIN CERTIFICATE-----")
