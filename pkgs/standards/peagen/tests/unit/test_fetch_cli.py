import json
from pathlib import Path

import pytest
import typer

from peagen.cli.commands import fetch
from peagen.models import Status


@pytest.mark.unit
def test_build_task_embeds_action_and_args():
    args = {"workspaces": ["w"]}
    task = fetch._build_task(args)
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
def test_submit_posts_request(monkeypatch):
    captured = {}

    class DummyResp:
        def raise_for_status(self):
            pass

        def json(self):
            return {"result": {"done": True}}

    class DummyClient:
        def __init__(self, timeout=None):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            pass

        def post(self, url, json):
            captured["url"] = url
            captured["json"] = json
            return DummyResp()

    monkeypatch.setattr(fetch.httpx, "Client", DummyClient)
    secho_out = []
    monkeypatch.setattr(
        typer, "secho", lambda msg, fg=None, err=False: secho_out.append(msg)
    )
    monkeypatch.setattr(typer, "echo", lambda msg: secho_out.append(msg))

    class DummyCtx:
        obj = {"gateway_url": "http://gw"}

    fetch.submit(DummyCtx(), ["w"], False, True)

    assert captured["url"] == "http://gw"
    assert captured["json"]["method"] == "Task.submit"
    assert any("Submitted task" in m for m in secho_out)
