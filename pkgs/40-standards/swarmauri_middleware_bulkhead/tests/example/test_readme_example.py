import runpy
from pathlib import Path

import pytest

EXAMPLE_PATH = (
    Path(__file__).resolve().parents[2] / "docs/readme/quick_start.py"
)


@pytest.mark.example
def test_readme_quickstart_example(capsys: pytest.CaptureFixture[str]) -> None:
    runpy.run_path(str(EXAMPLE_PATH), run_name="__main__")

    output = capsys.readouterr().out
    assert "Peak concurrent requests:" in output
    assert "Responses:" in output
