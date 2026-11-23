import runpy
from pathlib import Path

import pytest

EXAMPLE_PATH = Path(__file__).resolve().parents[1] / "docs/readme/usage.py"


@pytest.mark.example
def test_readme_example_executes() -> None:
    namespace = runpy.run_path(str(EXAMPLE_PATH), run_name="__main__")
    assert namespace["verified"] is True
