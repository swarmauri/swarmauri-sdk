from __future__ import annotations

import json
from typing import Any

import pytest
from pydantic import BaseModel
from typer.testing import CliRunner

from peagen.cli.commands import task as task_cmd
from peagen.orm import Status


class DummyTaskUpdate(BaseModel):
    id: str | None = None
    status: Status | None = None
    notes: str | None = None


class DummyTaskRead(BaseModel):
    id: str
    status: Status | None = None
    notes: str | None = None


class FakeRPC:
    def __init__(self) -> None:
        self.calls: list[tuple[str, Any]] = []

    def call(self, method: str, *, params: Any = None, out_schema: Any = None):  # type: ignore[override]
        if hasattr(params, "model_dump"):
            data = params.model_dump()
        else:
            data = params
        self.calls.append((method, data))
        return out_schema(**data)


@pytest.fixture(autouse=True)
def patch_schema(monkeypatch):
    def fake_schema(tag: str):
        if tag == "update":
            return DummyTaskUpdate
        if tag == "read":
            return DummyTaskRead
        raise AssertionError(f"unexpected tag {tag}")

    monkeypatch.setattr(task_cmd, "_schema", fake_schema)


@pytest.mark.unit
def test_patch_command_updates_task() -> None:
    runner = CliRunner()
    rpc = FakeRPC()
    changes = json.dumps({"status": "paused"})

    result = runner.invoke(
        task_cmd.remote_task_app, ["patch", "t1", changes], obj={"rpc": rpc}
    )
    assert result.exit_code == 0
    assert rpc.calls[0][0] == "Tasks.update"
    assert rpc.calls[0][1]["status"] == Status.paused


@pytest.mark.parametrize(
    ("cmd", "expected"),
    [
        ("pause", Status.paused),
        ("resume", Status.running),
        ("cancel", Status.cancelled),
        ("retry", Status.retry),
    ],
)
@pytest.mark.unit
def test_simple_status_commands(cmd: str, expected: Status) -> None:
    runner = CliRunner()
    rpc = FakeRPC()
    result = runner.invoke(task_cmd.remote_task_app, [cmd, "t1"], obj={"rpc": rpc})
    assert result.exit_code == 0
    assert rpc.calls[0][1]["status"] == expected


@pytest.mark.unit
def test_retry_from_clones_task(monkeypatch) -> None:
    runner = CliRunner()
    captured: dict[str, Any] = {}

    def fake_get_task(rpc: Any, task_id: str):
        return {
            "action": "demo",
            "args": {"x": 1},
            "pool_id": "p",
            "labels": ["a"],
            "repo": "r",
            "ref": "HEAD",
        }

    def fake_build_task(action, args, pool_id, labels, repo, ref):
        captured["built"] = (action, args, pool_id, labels, repo, ref)
        return "new-task"

    def fake_submit_task(rpc: Any, task: Any):
        captured["submitted"] = task
        return {"id": "t2"}

    monkeypatch.setattr(task_cmd, "get_task", fake_get_task)
    monkeypatch.setattr(task_cmd, "build_task", fake_build_task)
    monkeypatch.setattr(task_cmd, "submit_task", fake_submit_task)

    rpc = object()
    result = runner.invoke(
        task_cmd.remote_task_app, ["retry-from", "t1"], obj={"rpc": rpc}
    )
    assert result.exit_code == 0
    assert captured["built"][0] == "demo"
    assert captured["submitted"] == "new-task"
    assert '"id": "t2"' in result.stdout
