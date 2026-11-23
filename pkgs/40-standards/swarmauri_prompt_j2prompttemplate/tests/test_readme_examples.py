import runpy
from pathlib import Path

import pytest

EXAMPLES = Path(__file__).resolve().parents[1] / "docs/readme"


@pytest.mark.example
def test_readme_examples(tmp_path, monkeypatch):
    inline_example = runpy.run_path(str(EXAMPLES / "quick_start.py"))
    assert inline_example["result"] == "Hello, World!"

    monkeypatch.chdir(tmp_path)
    filesystem_example = runpy.run_path(str(EXAMPLES / "usage.py"))
    prompt = filesystem_example["prompt"]
    assert prompt({"animal": "fox"}) == "Hello, foxes!"
