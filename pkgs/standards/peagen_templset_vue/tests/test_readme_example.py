from __future__ import annotations

import io
import sys
from contextlib import redirect_stdout
from pathlib import Path
from typing import List

import pytest


def _extract_readme_python_example(readme_path: Path) -> str:
    blocks: List[str] = []
    current: List[str] = []
    capturing = False

    for line in readme_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("```python"):
            capturing = True
            current = []
            continue
        if capturing and stripped.startswith("```"):
            blocks.append("\n".join(current))
            capturing = False
            continue
        if capturing:
            current.append(line)

    for block in blocks:
        if "peagen_templset_vue.templates.peagen_templset_vue" in block:
            return block

    raise AssertionError(
        "Unable to find the README Python example for peagen_templset_vue"
    )


@pytest.mark.example
def test_readme_example_runs_and_outputs_expected(tmp_path) -> None:  # noqa: ANN001
    package_root = Path(__file__).resolve().parents[1]
    readme_path = package_root / "README.md"
    code = _extract_readme_python_example(readme_path)

    stdout = io.StringIO()
    namespace: dict[str, object] = {}

    sys_path_added = False
    if str(package_root) not in sys.path:
        sys.path.insert(0, str(package_root))
        sys_path_added = True

    try:
        with redirect_stdout(stdout):
            exec(code, namespace)  # noqa: S102
    finally:
        if sys_path_added:
            sys.path.remove(str(package_root))

    output_lines = stdout.getvalue().strip().splitlines()
    assert output_lines[0] == "Template root: peagen_templset_vue"
    assert output_lines[1] == "Top-level prompts: ['agent_default.j2', 'ptree.yaml.j2']"
    assert output_lines[2] == "Component template files:"
    assert output_lines[3:] == [
        "- index.ts.j2",
        "- {{ MOD.NAME }}.a11y.spec.ts.j2",
        "- {{ MOD.NAME }}.css.j2",
        "- {{ MOD.NAME }}.d.ts.j2",
        "- {{ MOD.NAME }}.spec.ts.j2",
        "- {{ MOD.NAME }}.stories.mdx.j2",
        "- {{ MOD.NAME }}.stories.ts.j2",
        "- {{ MOD.NAME }}.visual.spec.ts.j2",
        "- {{ MOD.NAME }}.vue.j2",
    ]
