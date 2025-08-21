import asyncio


def _run(service):
    async def _go():
        t_pub = await service.mint({"msg": "hi"}, alg="v4.public", kid="ed1")
        c_pub = await service.verify(t_pub)
        t_loc = await service.mint({"msg": "hi"}, alg="v4.local", kid="sym1")
        c_loc = await service.verify(t_loc)
        return c_pub["msg"] == "hi" and c_loc["msg"] == "hi"

    return asyncio.run(_go())


def test_mint_and_verify_unit(token_service):
    assert _run(token_service)
