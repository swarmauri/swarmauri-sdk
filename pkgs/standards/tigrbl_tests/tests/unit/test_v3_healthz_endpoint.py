import pytest
from types import SimpleNamespace
from tigrbl.types import App
from httpx import AsyncClient, ASGITransport

from tigrbl.system.diagnostics import mount_diagnostics


class DummyDB:
    def __init__(self):
        self.calls = []

    def execute(self, stmt):
        text = str(stmt)
        self.calls.append(text)
        if text == "SELECT 1":
            raise RuntimeError("uppercase not supported")
        return 1


@pytest.mark.asyncio
async def test_healthz_endpoint_select_case_fallback():
    db = DummyDB()

    def get_db():
        return db

    api = SimpleNamespace(models={})
    app = App()
    app.include_router(mount_diagnostics(api, get_db=get_db), prefix="/system")

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        res = await client.get("/system/healthz")

    assert res.status_code == 200
    assert res.json() == {"ok": True}
    assert db.calls == ["SELECT 1", "select 1"]
