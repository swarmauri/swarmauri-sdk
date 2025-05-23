import os
import re
from pathlib import Path

import pytest
from typer.testing import CliRunner

from peagen.cli import app


@pytest.mark.i9n
def test_peagen_process_creates_manifest(tmp_path):
    payload = (
        Path(__file__).resolve().parents[1]
        / "examples"
        / "projects_payloads"
        / "projects_payload_example1.yaml"
    )
    runner = CliRunner()
    env = {"OPENAI_API_KEY": "dummy", **os.environ}
    result = runner.invoke(
        app,
        [
            "process",
            str(payload),
            "--provider",
            "openai",
            "--model-name",
            "dummy",
            "--artifacts",
            f"dir://{tmp_path}",
        ],
        env=env,
    )
    assert result.exit_code == 0, result.output
    match = re.search(r"run-id: (\S+)", result.output)
    assert match, "run-id not found in output"
    run_id = match.group(1)
    manifest = (
        tmp_path
        / "projects"
        / "exampleparserproject"
        / "runs"
        / run_id
        / ".peagen"
        / "ExampleParserProject_manifest.json"
    )
    assert manifest.exists()
