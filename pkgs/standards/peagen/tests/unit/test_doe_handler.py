import pytest
from pathlib import Path

from peagen.handlers import doe_handler as handler
from peagen.schemas import TaskRead
from peagen.orm.status import Status
import uuid
from datetime import datetime, timezone


@pytest.mark.unit
@pytest.mark.asyncio
async def test_doe_handler_calls_generate_payload(monkeypatch):
    captured = {}

    def fake_generate_payload(**kwargs):
        captured.update(kwargs)
        return {"done": True}

    monkeypatch.setattr(handler, "generate_payload", fake_generate_payload)

    args = {
        "spec": "spec.yml",
        "template": "templ.j2",
        "output": "out.json",
        "config": "cfg.toml",
        "notify": "http://x",
        "dry_run": True,
        "force": True,
        "skip_validate": True,
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
    result = await handler.doe_handler(task)

    assert result == {"done": True}
    assert captured["spec_path"] == Path("spec.yml")
    assert captured["dry_run"] is True
