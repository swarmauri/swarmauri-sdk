import pytest
from pathlib import Path

from peagen.handlers import fetch_handler as handler
from peagen.cli.task_helpers import build_task


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

    task = build_task(
        action="fetch",
        args=args,
        tenant_id="t",
        pool_id="p",
        repo="repo",
        ref="HEAD",
    )
    result = await handler.fetch_handler(task)

    assert result == {"count": 2}
    assert captured["workspace_uris"] == ["w1", "w2"]
    assert captured["out_dir"] == Path("~/out").expanduser()
    assert captured["no_source"] is True
    assert captured["install_template_sets_flag"] is False
