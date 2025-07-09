import pytest
from pathlib import Path

from peagen.handlers import doe_handler as handler
from peagen.cli.task_helpers import build_task
from peagen.orm import Action
from uuid import uuid4


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

    task = build_task(
        action=Action.VALIDATE,
        args=args,
        tenant_id=str(uuid4()),
        pool_id=str(uuid4()),
        repo="repo",
        ref="HEAD",
    )
    result = await handler.doe_handler(task)

    assert result == {"done": True}
    assert captured["spec_path"] == Path("spec.yml")
    assert captured["dry_run"] is True
