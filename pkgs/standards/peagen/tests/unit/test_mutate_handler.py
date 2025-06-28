import pytest

from peagen.handlers import mutate_handler as handler
from peagen.schemas import TaskRead
from peagen.orm.status import Status
import uuid
from datetime import datetime, timezone


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

    task = TaskRead.model_construct(
        id=str(uuid.uuid4()),
        tenant_id=uuid.uuid4(),
        git_reference_id=None,
        pool="default",
        payload={"args": args},
        status=Status.queued,
        note=None,
        spec_hash="",
        date_created=datetime.now(timezone.utc),
        last_modified=datetime.now(timezone.utc),
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
