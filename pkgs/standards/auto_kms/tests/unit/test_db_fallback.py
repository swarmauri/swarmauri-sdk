import asyncio
import importlib
from autoapi.v3.engine import resolver as _resolver


def test_startup_falls_back_to_sqlite(monkeypatch):
    monkeypatch.setenv("KMS_DATABASE_URL", "postgresql+asyncpg://localhost:1/testdb")
    app_mod = importlib.reload(importlib.import_module("auto_kms.app"))
    asyncio.run(app_mod.startup_event())
    prov = _resolver.resolve_provider()
    assert str(prov.ensure()[0].url).startswith("sqlite")
