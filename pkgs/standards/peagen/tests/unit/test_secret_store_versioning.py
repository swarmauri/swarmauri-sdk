import importlib

import pytest

from peagen.models import Base
import peagen.gateway as gw
import peagen.gateway.db as db


@pytest.mark.asyncio
async def test_secret_roundtrip(tmp_path, monkeypatch):
    """Validate storing, retrieving and deleting secrets."""
    monkeypatch.chdir(tmp_path)
    importlib.reload(gw)
    importlib.reload(db)
    async with db.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await gw.secrets_add(name="ns/test", secret="a")
    val = await gw.secrets_get(name="ns/test")
    assert val == {"secret": "a"}

    await gw.secrets_add(name="ns/test", secret="b")
    val = await gw.secrets_get(name="ns/test")
    assert val == {"secret": "b"}

    await gw.secrets_delete(name="ns/test")
    with pytest.raises(gw.RPCException):
        await gw.secrets_get(name="ns/test")
