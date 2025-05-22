import os
from pathlib import Path
from typer.testing import CliRunner
import pytest

from peagen.cli import app


@pytest.mark.i9n
def test_peagen_revise_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    payload = Path(__file__).resolve().parents[2] / "examples" / "projects_payloads" / "projects_payload_example1.yaml"
    notes_file = tmp_path / "revision_notes.txt"
    notes_file.write_text("minor update")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("OPENAI_API_KEY", "dummy-key")

    from peagen import _external
    monkeypatch.setattr(_external, "call_external_agent", lambda prompt, agent_env, logger=None: "generated")

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "revise",
            str(payload),
            "--project-name",
            "ExampleParserProject",
            "--revision-notes-file",
            str(notes_file),
            "--provider",
            "openai",
            "--model-name",
            "dummy",
            "--no-include-swarmauri",
            "--artifacts",
            f"dir://{tmp_path}",
        ],
    )
    assert result.exit_code == 0, result.output
    manifest_path = tmp_path / ".peagen" / "ExampleParserProject_manifest.json"
    assert manifest_path.is_file()
