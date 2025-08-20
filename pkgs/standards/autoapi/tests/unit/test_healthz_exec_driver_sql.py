import pytest
from types import SimpleNamespace
from sqlalchemy import create_engine

from autoapi.v3.system.diagnostics import _build_healthz_endpoint


@pytest.mark.asyncio
async def test_healthz_exec_driver_sql():
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )
    with engine.connect() as conn:
        request = SimpleNamespace(state=SimpleNamespace(db=conn))
        healthz = _build_healthz_endpoint(None)
        resp = await healthz(request)
    assert resp == {"ok": True}
