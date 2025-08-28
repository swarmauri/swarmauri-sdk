import pytest
from typer.testing import CliRunner

from peagen.cli.commands.extras import local_extras_app


@pytest.mark.unit
def test_extras_cli_generates_schemas(monkeypatch, tmp_path):
    called = {}

    def fake_build_task(action, args, pool):
        called["action"] = action
        called["args"] = args
        called["pool"] = pool
        return "TASK"

    async def fake_handler(task):
        called["task"] = task
        return {"generated": [str(tmp_path / "a.json")]}

    monkeypatch.setattr("peagen.cli.commands.extras.build_task", fake_build_task)
    monkeypatch.setattr("peagen.cli.commands.extras.extras_handler", fake_handler)

    runner = CliRunner()
    templates = tmp_path / "templates"
    schemas = tmp_path / "schemas"
    result = runner.invoke(
        local_extras_app,
        [
            "--repo",
            "repo",
            "--ref",
            "main",
            "--templates-root",
            str(templates),
            "--schemas-dir",
            str(schemas),
        ],
        obj={"pool": "default"},
    )

    assert result.exit_code == 0
    assert called["action"] == "extras"
    assert called["args"]["templates_root"] == str(templates)
    assert called["args"]["schemas_dir"] == str(schemas)
    assert called["args"]["repo"] == "repo"
    assert called["args"]["ref"] == "main"
    assert called["pool"] == "default"
    assert called["task"] == "TASK"
    assert "\u2705 Wrote" in result.stdout
    assert str(tmp_path / "a.json") in result.stdout


@pytest.mark.unit
def test_extras_cli_handles_error(monkeypatch):
    def fake_build_task(action, args, pool):
        return "TASK"

    async def fake_handler(task):
        raise RuntimeError("boom")

    monkeypatch.setattr("peagen.cli.commands.extras.build_task", fake_build_task)
    monkeypatch.setattr("peagen.cli.commands.extras.extras_handler", fake_handler)

    runner = CliRunner()
    result = runner.invoke(
        local_extras_app,
        ["--repo", "repo"],
        obj={"pool": "default"},
    )

    assert result.exit_code == 1
    assert "[ERROR] Exception inside extras_handler: boom" in result.stdout
