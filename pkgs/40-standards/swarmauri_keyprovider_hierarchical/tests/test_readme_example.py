import runpy
from pathlib import Path

import pytest

EXAMPLE_PATH = (
    Path(__file__).resolve().parents[1] / "docs/readme/quick_start.py"
)


@pytest.mark.example
def test_readme_quickstart_example(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    runpy.run_path(str(EXAMPLE_PATH), run_name="__main__")

    output = capsys.readouterr().out
    assert "Symmetric key kid:" in output
    assert "Asymmetric key kid:" in output
    assert "Random token length:" in output
    assert "JWKS entries:" in output
