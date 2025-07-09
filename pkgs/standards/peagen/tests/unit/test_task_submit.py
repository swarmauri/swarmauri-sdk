import httpx
import pytest

from peagen.cli.task_helpers import build_task, submit_task
from peagen.orm import Action
from uuid import uuid4


@pytest.mark.unit
def test_build_task_creates_task():
    task = build_task(
        action=Action.SORT,
        args={"x": 1},
        tenant_id=str(uuid4()),
        pool_id=str(uuid4()),
        repo="repo",
        ref="HEAD",
    )
    assert task.action == "demo"
    assert task.args == {"x": 1}


@pytest.mark.unit
def test_submit_task_sends_request(monkeypatch):
    captured = {}

    def fake_post(url, json, timeout):
        captured["url"] = url
        captured["json"] = json

        class Resp:
            def raise_for_status(self):
                pass

            def json(self):
                return {"ok": True}

        return Resp()

    monkeypatch.setattr(
        httpx,
        "Client",
        lambda timeout: type(
            "C", (), {"post": fake_post, "close": lambda self: None}
        )(),
    )
    task = build_task(
        action=Action.SORT,
        args={},
        tenant_id=str(uuid4()),
        pool_id=str(uuid4()),
        repo="repo",
        ref="HEAD",
    )
    reply = submit_task("http://gw/rpc", task)
    assert captured["json"]["params"]["id"] == str(task.id)
    assert reply == {"ok": True}
