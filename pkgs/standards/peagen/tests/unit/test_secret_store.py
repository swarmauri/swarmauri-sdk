import importlib

import pytest

from peagen.models import Base
import peagen.gateway as gw
import peagen.gateway.db as db


@pytest.mark.unit
@pytest.mark.asyncio
async def test_secret_roundtrip(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    importlib.reload(gw)
    importlib.reload(db)
    async with db.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await gw.secrets_add(name="foo", secret="bar")
    res = await gw.secrets_get(name="foo")
    assert res["secret"] == "bar"
    await gw.secrets_delete(name="foo")
    with pytest.raises(TypeError):
        await gw.secrets_get(name="foo")
