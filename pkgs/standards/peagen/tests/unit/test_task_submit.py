import pytest

from peagen.cli.task_helpers import build_task, submit_task


@pytest.mark.unit
def test_build_task_creates_task():
    task = build_task(
        action="demo",
        args={"x": 1},
        pool_id="p",
        repo="repo",
        ref="HEAD",
    )
    assert task.action == "demo"
    assert task.args == {"x": 1}


@pytest.mark.unit
def test_submit_task_sends_request(monkeypatch):
    captured = {}

    def fake_call(self, method, *, params=None, out_schema=None):
        captured["json"] = {
            "params": params if isinstance(params, dict) else params.model_dump()
        }

        class Res:
            def model_dump(self):
                return {"ok": True}

        return Res()

    from tigrbl_client import TigrblClient

    monkeypatch.setattr(TigrblClient, "call", fake_call)
    task = build_task(
        action="demo",
        args={},
        pool_id="p",
        repo="repo",
        ref="HEAD",
    )
    reply = submit_task("http://gw/rpc", task)
    assert captured["json"]["params"]["id"] == task.id
    assert reply == {"ok": True}
