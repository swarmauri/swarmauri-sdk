import importlib

import pytest

from peagen.orm import Base
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

    await gw.secrets_add(name="foo", cipher="bar")
    res = await gw.secrets_get(name="foo")
    assert res["secret"] == "bar"
    await gw.secrets_delete(name="foo")
    with pytest.raises(gw.RPCException):
        await gw.secrets_get(name="foo")
