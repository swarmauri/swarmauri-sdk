import os
from pathlib import Path

import pytest
from click.testing import CliRunner

from peagen.cli import app


@pytest.mark.i9n
def test_sort_lists_files(tmp_path):
    """Integration test for `peagen sort` command."""
    runner = CliRunner()
    payload = (
        Path(__file__).resolve().parent.parent
        / "examples"
        / "projects_payloads"
        / "projects_payload_example1.yaml"
    )

    env = {"OPENAI_API_KEY": "dummy", **os.environ}
    result = runner.invoke(
        app,
        [
            "sort",
            str(payload),
            "--project-name",
            "ExampleParserProject",
            "--provider",
            "openai",
            "--model-name",
            "dummy",
            "--transitive",
            "--show-deps",
        ],
        env=env,
    )

    assert result.exit_code == 0
    assert any(line.strip().startswith("0)") for line in result.output.splitlines())
