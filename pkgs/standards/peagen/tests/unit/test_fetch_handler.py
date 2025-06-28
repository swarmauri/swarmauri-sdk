import pytest
from pathlib import Path

from peagen.handlers import fetch_handler as handler
from peagen.schemas import TaskRead
from peagen.orm.status import Status
import uuid
from datetime import datetime, timezone


@pytest.mark.unit
@pytest.mark.asyncio
async def test_fetch_handler_passes_args(monkeypatch):
    captured = {}

    def fake_fetch_many(**kwargs):
        captured.update(kwargs)
        return {"count": len(kwargs.get("workspace_uris", []))}

    monkeypatch.setattr(handler, "fetch_many", fake_fetch_many)

    args = {
        "workspaces": ["w1", "w2"],
        "out_dir": "~/out",
        "no_source": True,
        "install_template_sets": False,
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
    result = await handler.fetch_handler(task)

    assert result == {"count": 2}
    assert captured["workspace_uris"] == ["w1", "w2"]
    assert captured["out_dir"] == Path("~/out").expanduser()
    assert captured["no_source"] is True
    assert captured["install_template_sets_flag"] is False
