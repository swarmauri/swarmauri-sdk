from __future__ import annotations

import re
from pathlib import Path

import pytest


@pytest.mark.example
def test_usage_example_from_readme():
    """Execute the README usage example to ensure it stays valid."""

    readme_path = Path(__file__).resolve().parent.parent / "README.md"
    readme_text = readme_path.read_text(encoding="utf-8")

    # Pull the first Python code block from the README (the usage example).
    match = re.search(r"```python\n(.*?)```", readme_text, re.DOTALL)
    assert match, "Expected to find a Python code block in the README."

    code_block = match.group(1)

    namespace: dict[str, object] = {}
    exec(code_block, namespace)  # noqa: S102 - executing trusted documentation example

    documents = namespace.get("documents")
    assert documents is not None, (
        "The README example should define a 'documents' variable."
    )

    # Validate that the parser extracted <p> elements with accompanying metadata.
    contents = [doc.content for doc in documents]
    metadata = [doc.metadata for doc in documents]

    assert contents == ["<p>First paragraph</p>", "<p>Second paragraph</p>"]
    assert metadata == [
        {"element": "p", "index": 0},
        {"element": "p", "index": 1},
    ]
