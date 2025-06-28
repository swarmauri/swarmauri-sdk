import pytest

from peagen.handlers import eval_handler as handler
from peagen.schemas import TaskRead
from peagen.orm.status import Status
import uuid
from datetime import datetime, timezone


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize("strict", [False, True])
async def test_eval_handler(monkeypatch, strict):
    def fake_evaluate_workspace(**kwargs):
        return {"results": [{"score": 0}, {"score": 1}]}

    monkeypatch.setattr(handler, "evaluate_workspace", fake_evaluate_workspace)

    args = {"workspace_uri": "ws", "strict": strict}
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
    result = await handler.eval_handler(task)

    assert result["report"]["results"][0]["score"] == 0
    assert result["strict_failed"] == (strict and True)
