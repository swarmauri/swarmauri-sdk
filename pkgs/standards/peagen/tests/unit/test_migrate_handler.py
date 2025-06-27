import asyncio
import pytest
from pathlib import Path

from peagen.handlers import migrate_handler as handler
from peagen.orm import Task


@pytest.mark.unit
@pytest.mark.parametrize("as_dict", [True, False])
def test_migrate_handler_dispatch(monkeypatch, as_dict):
    captured = {}

    def fake_upgrade(cfg):
        captured["op"] = "upgrade"
        captured["cfg"] = cfg
        return {"ok": True}

    monkeypatch.setattr(handler, "alembic_upgrade", fake_upgrade)

    args = {"op": "upgrade", "alembic_ini": "~/a.ini"}
    task = {"payload": {"args": args}}
    if not as_dict:
        task = Task(pool="p", payload=task["payload"])

    result = asyncio.run(handler.migrate_handler(task))

    assert result == {"ok": True}
    assert captured["cfg"] == Path("~/a.ini").expanduser()
