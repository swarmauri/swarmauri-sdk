import pytest

from peagen.handlers import eval_handler as handler


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize("strict", [False, True])
async def test_eval_handler(monkeypatch, strict):
    def fake_evaluate_workspace(**kwargs):
        return {"results": [{"score": 0}, {"score": 1}]}

    monkeypatch.setattr(handler, "evaluate_workspace", fake_evaluate_workspace)

    args = {"workspace_uri": "ws", "strict": strict}
    result = await handler.eval_handler({"payload": {"args": args}})

    assert result["manifest"]["results"][0]["score"] == 0
    assert result["strict_failed"] == (strict and True)
