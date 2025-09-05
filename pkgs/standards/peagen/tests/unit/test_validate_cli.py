import pytest
from typer.testing import CliRunner

from peagen.cli.commands.validate import local_validate_app, remote_validate_app
from peagen.cli.task_helpers import build_task
from peagen.orm import Action


@pytest.mark.unit
def test_build_validate_task_payload():
    task = build_task(
        action="validate",
        args={"kind": "config", "path": "foo.toml"},
        pool_id="p",
        repo="repo",
        ref="HEAD",
    )
    assert task.action == Action.VALIDATE
    assert task.args == {"kind": "config", "path": "foo.toml"}


@pytest.mark.unit
def test_local_validate_cli_invokes_handler(monkeypatch, tmp_path):
    runner = CliRunner()
    captured = {}

    async def fake_handler(task):
        captured.update(task.args)
        return {"ok": True, "errors": []}

    monkeypatch.setattr(
        "peagen.handlers.validate_handler.validate_handler", fake_handler
    )

    result = runner.invoke(
        local_validate_app,
        [
            "validate",
            "config",
            "--path",
            str(tmp_path / "foo.toml"),
            "--repo",
            "repo",
            "--ref",
            "main",
        ],
    )
    assert result.exit_code == 0
    assert "Config is valid" in result.stdout
    assert captured["kind"] == "config"


@pytest.mark.unit
def test_remote_validate_cli_submits_task(monkeypatch):
    runner = CliRunner()
    captured = {}

    def fake_submit_task(rpc, task_model):
        captured["action"] = task_model.action
        return {"result": {"taskId": "t1"}}

    monkeypatch.setattr("peagen.cli.commands.validate.submit_task", fake_submit_task)

    result = runner.invoke(
        remote_validate_app,
        [
            "validate",
            "config",
            "--repo",
            "repo",
            "--ref",
            "main",
        ],
        obj={"rpc": object(), "pool": "default"},
    )
    assert result.exit_code == 0
    assert "Submitted validation → taskId=t1" in result.stdout
    assert captured["action"] == Action.VALIDATE
