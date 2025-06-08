import pytest
from pathlib import Path

from peagen.handlers import doe_handler as handler


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

    result = await handler.doe_handler({"payload": {"args": args}})

    assert result == {"done": True}
    assert captured["spec_path"] == Path("spec.yml")
    assert captured["dry_run"] is True
