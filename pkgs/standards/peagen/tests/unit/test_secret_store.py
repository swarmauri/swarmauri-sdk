import importlib

import pytest

from peagen.models import Base
from peagen.gateway.db import engine
import peagen.gateway as gw


@pytest.mark.unit
@pytest.mark.asyncio
async def test_secret_roundtrip(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    importlib.reload(gw)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await gw.secrets_add(name="foo", secret="bar")
    res = await gw.secrets_get(name="foo")
    assert res["secret"] == "bar"
    await gw.secrets_delete(name="foo")
    with pytest.raises(TypeError):
        await gw.secrets_get(name="foo")
