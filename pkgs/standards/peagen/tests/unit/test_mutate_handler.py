import pytest

from peagen.handlers import mutate_handler as handler
from peagen.cli.task_helpers import build_task
from peagen.orm import Action
from uuid import uuid4


@pytest.mark.unit
@pytest.mark.asyncio
async def test_mutate_handler_invokes_core(monkeypatch):
    captured = {}

    def fake_mutate_workspace(**kwargs):
        captured.update(kwargs)
        return {"winner": "w.py", "score": "1", "meta": {"ok": True}}

    monkeypatch.setattr(handler, "mutate_workspace", fake_mutate_workspace)

    args = {
        "workspace_uri": "ws",
        "target_file": "t.py",
        "import_path": "mod",
        "entry_fn": "f",
        "gens": 3,
        "profile_mod": None,
        "config": None,
        "mutations": [{"kind": "echo_mutator", "probability": 1}],
        "evaluator_ref": "ev",
    }

    task = build_task(
        action=Action.MUTATE,
        args=args,
        tenant_id=str(uuid4()),
        pool_id=str(uuid4()),
        repo="repo",
        ref="HEAD",
    )

    result = await handler.mutate_handler(task)

    assert result == {"winner": "w.py", "score": "1", "meta": {"ok": True}}
    assert captured["workspace_uri"] == "ws"
    assert captured["target_file"] == "t.py"
    assert captured["import_path"] == "mod"
    assert captured["entry_fn"] == "f"
    assert captured["gens"] == 3
    assert captured["mutations"] == [{"kind": "echo_mutator", "probability": 1}]
    assert captured["evaluator_ref"] == "ev"
