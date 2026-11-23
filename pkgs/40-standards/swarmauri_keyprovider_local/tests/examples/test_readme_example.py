import asyncio
import runpy
from pathlib import Path

import pytest

EXAMPLE_PATH = (
    Path(__file__).resolve().parents[2] / "docs/readme/quick_start.py"
)


@pytest.mark.example
def test_readme_quickstart_example_runs() -> None:
    run_example = runpy.run_path(str(EXAMPLE_PATH))["run_example"]

    result = asyncio.run(run_example())
    assert isinstance(result, str)
    assert result
