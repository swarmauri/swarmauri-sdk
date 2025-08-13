import pytest

from peagen.handlers import eval_handler as handler
from peagen.cli.task_helpers import build_task


@pytest.mark.unit
@pytest.mark.asyncio
async def test_eval_handler(monkeypatch):
    def fake_evaluate_workspace(**kwargs):
        assert kwargs["repo"] == "repo"
        assert kwargs["ref"] == "HEAD"
        return {"results": [{"score": 0}, {"score": 1}]}

    monkeypatch.setattr(handler, "evaluate_workspace", fake_evaluate_workspace)

    args = {"repo": "repo", "ref": "HEAD"}
    params = build_task(
        action="eval",
        args=args,
        pool_id="p",
        repo="repo",
        ref="HEAD",
    )
    result = await handler.eval_handler(params)

    assert result["report"]["results"][0]["score"] == 0
    assert result["strict_failed"] is False
