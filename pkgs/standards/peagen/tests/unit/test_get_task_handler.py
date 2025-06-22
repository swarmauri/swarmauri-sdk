import pytest

from peagen.handlers import get_task_handler as handler


@pytest.mark.unit
@pytest.mark.asyncio
async def test_task_get_handler(monkeypatch):
    async def fake_get_task_result(task_id, tenant_id="default"):
        return {"id": task_id, "tenant": tenant_id}

    # task_get_handler lazily imports get_task_result from peagen.core.task_core
    # Insert a stub module into sys.modules so that import resolves without
    # loading the real module (which has heavy deps and circular imports).
    import sys
    import types
    stub = types.ModuleType("peagen.core.task_core")
    stub.get_task_result = fake_get_task_result
    monkeypatch.setitem(sys.modules, "peagen.core.task_core", stub)

    result = await handler.task_get_handler({"taskId": "123", "tenantId": "t1"})

    assert result == {"id": "123", "tenant": "t1"}
