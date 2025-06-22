import pytest
from peagen.gateway import secrets_add, secrets_get, secrets_delete, SECRET_STORE


@pytest.mark.asyncio
async def test_secret_versioning():
    SECRET_STORE.clear()

    res = await secrets_add("ns/test", "a", version=0)
    assert res == {"version": 1}

    val = await secrets_get("ns/test")
    assert val == {"secret": "a", "version": 1}

    with pytest.raises(TypeError):
        await secrets_add("ns/test", "b", version=0)

    res = await secrets_add("ns/test", "b", version=1)
    assert res == {"version": 2}

    await secrets_delete("ns/test", version=2)
    with pytest.raises(TypeError):
        await secrets_get("ns/test")
