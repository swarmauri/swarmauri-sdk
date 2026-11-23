import runpy
from pathlib import Path

import pytest

EXAMPLE_PATH = (
    Path(__file__).resolve().parents[1] / "docs/readme/quick_start.py"
)


@pytest.mark.example
def test_readme_example_executes(capsys: pytest.CaptureFixture[str]) -> None:
    runpy.run_path(str(EXAMPLE_PATH), run_name="__main__")

    output = capsys.readouterr().out
    assert "Score: 0.50" in output
    assert "should be decorated with @abstractmethod" in output
