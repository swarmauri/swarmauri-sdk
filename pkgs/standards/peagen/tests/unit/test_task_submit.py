import httpx
import pytest

from peagen.tui.task_submit import build_task, submit_task


@pytest.mark.unit
def test_build_task_creates_task():
    task = build_task("demo", {"x": 1})
    assert task.payload["action"] == "demo"
    assert task.payload["args"] == {"x": 1}


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
                return {"jsonrpc": "2.0", "id": "1", "result": {"ok": True}}

        return Resp()

    monkeypatch.setattr(httpx, "post", fake_post)
    task = build_task("demo", {})
    reply = submit_task("http://gw/rpc", task)
    assert captured["json"]["params"]["id"] == task.id
    assert reply.get("result") == {"ok": True}
