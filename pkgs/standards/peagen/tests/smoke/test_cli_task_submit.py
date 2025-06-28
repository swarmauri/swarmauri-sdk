import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from peagen.cli import app
from peagen.cli.commands import process as process_mod


@pytest.mark.smoke
def test_cli_task_submit_local(monkeypatch, tmp_path: Path) -> None:
    def fake_post(url: str, json: dict, timeout: float):
        assert json["method"] == "Task.submit"
        data = {"result": {"taskId": "123"}}

        class Resp:
            def raise_for_status(self):
                pass

            def json(self):
                return data

        return Resp()

    class DummyClient:
        def __init__(self, *a, **k):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            pass

        def post(self, url: str, json: dict):
            return fake_post(url, json, 30.0)

    import httpx

    monkeypatch.setattr(httpx, "post", fake_post)
    monkeypatch.setattr(httpx, "Client", DummyClient)

    from pydantic import BaseModel

    class DummyTask(BaseModel):
        id: str = "abc"
        pool: str
        payload: dict

    monkeypatch.setattr(
        process_mod,
        "_build_task",
        lambda args, pool: DummyTask(
            pool=pool, payload={"action": "process", "args": args}
        ),
    )

    payload = tmp_path / "payload.yaml"
    payload.write_text("PROJECTS: []", encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(
        app,
        ["remote", "-q", "--gateway-url", "http://gw/rpc", "process", str(payload)],
    )

    assert result.exit_code == 0
    output = result.stdout.strip().splitlines()
    assert any("Submitted task" in line for line in output)
    last = json.loads("\n".join(output[-3:]))
    assert "taskId" in last
