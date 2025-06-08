import pytest

from peagen.handlers import get_task_handler as handler


@pytest.mark.unit
@pytest.mark.asyncio
async def test_task_get_handler(monkeypatch):
    async def fake_get_task_result(task_id):
        return {"id": task_id}

    monkeypatch.setattr(handler, "get_task_result", fake_get_task_result)

    result = await handler.task_get_handler({"taskId": "123"})

    assert result == {"id": "123"}
