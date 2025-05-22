import yaml
from pathlib import Path
from typer.testing import CliRunner
import pytest

from peagen.cli import app


@pytest.mark.i9n
def test_doe_gen_creates_project_payload(tmp_path):
    """Ensure DOE generation produces expected number of projects."""
    runner = CliRunner()
    spec_path = Path("tests/examples/doe_specs/doe_spec.yaml")
    template_path = Path("docs/examples/base_example_project.yaml")
    out_file = tmp_path / "payload.yaml"

    result = runner.invoke(
        app,
        [
            "doe",
            "gen",
            str(spec_path),
            str(template_path),
            "--output",
            str(out_file),
            "--skip-validate",
        ],
    )
    assert result.exit_code == 0, result.output
    assert out_file.exists()
    data = yaml.safe_load(out_file.read_text())
    assert len(data.get("PROJECTS", [])) == 8
