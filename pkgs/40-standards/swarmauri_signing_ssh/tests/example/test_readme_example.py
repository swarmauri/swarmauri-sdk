import runpy
from pathlib import Path

import pytest

EXAMPLE_PATH = (
    Path(__file__).resolve().parents[2] / "docs/readme/quick_start.py"
)


@pytest.mark.asyncio
@pytest.mark.example
async def test_readme_example_executes() -> None:
    main = runpy.run_path(str(EXAMPLE_PATH))["main"]
    assert await main() is True
