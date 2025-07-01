import json
from pathlib import Path

import pytest
import typer

from peagen.cli.commands import fetch
from peagen.orm.status import Status
from peagen.cli.task_helpers import build_task


@pytest.mark.unit
def test_build_task_embeds_action_and_args():
    args = {"workspaces": ["w"]}
    task = build_task("fetch", args)
    assert task.payload == {"action": "fetch", "args": args}
    assert task.pool == "default"
    assert task.status == Status.waiting
    assert isinstance(task.id, str)


@pytest.mark.unit
def test_collect_args_with_repo(monkeypatch):
    monkeypatch.setattr(Path, "cwd", lambda: Path("/tmp/w"))
    result = fetch._collect_args([], False, True, repo="r", ref="main")
    assert result == {
        "workspaces": ["git+r@main"],
        "out_dir": "/tmp/w",
        "no_source": False,
        "install_template_sets": True,
    }


@pytest.mark.unit
def test_collect_args_without_repo(monkeypatch):
    monkeypatch.setattr(Path, "cwd", lambda: Path("/tmp/w"))
    result = fetch._collect_args(["w1"], True, False)
    assert result == {
        "workspaces": ["w1"],
        "out_dir": "/tmp/w",
        "no_source": True,
        "install_template_sets": False,
    }


@pytest.mark.unit
def test_run_invokes_fetch_handler(monkeypatch):
    captured = {}

    async def fake_fetch(task):
        captured["payload"] = task.payload
        return {"ok": True}

    monkeypatch.setattr(fetch, "fetch_handler", fake_fetch)
    monkeypatch.setattr(Path, "cwd", lambda: Path("/tmp/w"))
    outputs = []
    monkeypatch.setattr(typer, "echo", lambda msg: outputs.append(msg))

    fetch.run(None, ["w"], False, True)

    assert captured["payload"]["action"] == "fetch"
    assert json.loads(outputs[0]) == {"ok": True}


@pytest.mark.unit
def test_fetch_repo_ref_argument(monkeypatch):
    captured = {}

    async def fake_fetch(task):
        captured["payload"] = task.payload
        return {"done": True}

    monkeypatch.setattr(fetch, "fetch_handler", fake_fetch)
    monkeypatch.setattr(Path, "cwd", lambda: Path("/tmp/w"))
    outputs = []
    monkeypatch.setattr(typer, "echo", lambda msg: outputs.append(msg))

    fetch.run(None, [], False, True, repo="repo", ref="main")

    assert captured["payload"]["args"]["workspaces"] == ["git+repo@main"]
    assert json.loads(outputs[0]) == {"done": True}
