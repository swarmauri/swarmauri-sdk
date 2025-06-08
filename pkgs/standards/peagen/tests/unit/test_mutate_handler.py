import pytest
from pathlib import Path

from peagen.handlers import mutate_handler as handler


@pytest.mark.unit
@pytest.mark.asyncio
async def test_mutate_handler_invokes_core(monkeypatch):
    captured = {}

    def fake_mutate_workspace(**kwargs):
        captured.update(kwargs)
        return {"winner": "w.py", "score": "1"}

    monkeypatch.setattr(handler, "mutate_workspace", fake_mutate_workspace)

    args = {
        "workspace_uri": "ws",
        "target_file": "t.py",
        "import_path": "mod",
        "entry_fn": "f",
        "gens": 3,
        "profile_mod": None,
        "config": None,
    }

    result = await handler.mutate_handler({"payload": {"args": args}})

    assert result == {"winner": "w.py", "score": "1"}
    assert captured["workspace_uri"] == "ws"
    assert captured["target_file"] == "t.py"
    assert captured["import_path"] == "mod"
    assert captured["entry_fn"] == "f"
    assert captured["gens"] == 3
