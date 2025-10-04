import pytest
from pathlib import Path

from peagen.handlers import fetch_handler as handler
from peagen.cli.task_helpers import build_task


@pytest.mark.unit
@pytest.mark.asyncio
async def test_fetch_handler_passes_args(monkeypatch):
    captured = {}

    def fake_fetch_many(repos, *, ref="HEAD", out_dir=None):
        captured["repos"] = repos
        captured["ref"] = ref
        captured["out_dir"] = out_dir
        return {"count": len(repos)}

    monkeypatch.setattr(handler, "fetch_many", fake_fetch_many)

    args = {
        "repos": ["git+repo1", "git+repo2"],
        "out_dir": "~/out",
        "ref": "master",
    }

    task = build_task(
        action="fetch",
        args=args,
        pool_id="p",
        repo="repo",
        ref="master",
    )
    result = await handler.fetch_handler(task)

    assert result == {"count": 2}
    assert captured["repos"] == ["git+repo1", "git+repo2"]
    assert captured["ref"] == "master"
    assert captured["out_dir"] == Path("~/out").expanduser()
