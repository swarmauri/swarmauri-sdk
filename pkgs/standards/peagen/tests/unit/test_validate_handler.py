import pytest
from pathlib import Path

from peagen.handlers import validate_handler as handler
from peagen.models import Task


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize("as_dict", [True, False])
async def test_validate_handler(monkeypatch, as_dict):
    captured = {}

    def fake_validate_artifact(kind, path):
        captured["kind"] = kind
        captured["path"] = path
        return {"ok": True}

    monkeypatch.setattr(handler, "validate_artifact", fake_validate_artifact)

    args = {"kind": "schema", "path": "~/p"}
    task = {"payload": {"args": args}}
    if not as_dict:
        task = Task(pool="p", payload=task["payload"])

    result = await handler.validate_handler(task)

    assert result == {"ok": True}
    assert captured["kind"] == "schema"
    assert captured["path"] == Path("~/p").expanduser()
