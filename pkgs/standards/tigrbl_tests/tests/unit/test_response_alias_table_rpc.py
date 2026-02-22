from __future__ import annotations
import pytest
from tigrbl import alias_ctx
from tigrbl.responses import response_ctx
from tigrbl.engine.shortcuts import engine as build_engine, mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.orm.tables import Base
from tigrbl.specs import IO, S, F, acol as spec_acol
from tigrbl.types import String
from tigrbl.router import TigrblRouter


@pytest.mark.asyncio
async def test_response_ctx_alias_table_rpc():
    @alias_ctx(read="fetch")
    @response_ctx(headers={"X-Table": "alias"})
    class Widget(Base, GUIDPk):
        __tablename__ = "widgets_alias"
        __allow_unmapped__ = True

        name = spec_acol(
            storage=S(type_=String(50), nullable=False),
            field=F(py_type=str),
            io=IO(in_verbs=("create",), out_verbs=("read",)),
        )

    eng = build_engine(mem(async_=False))
    router = TigrblRouter(engine=eng)
    router.include_model(Widget, mount_router=False)
    router.initialize()
    raw_eng, _ = eng.raw()
    try:
        with eng.session() as session:
            created = await router.rpc_call(Widget, "create", {"name": "a"}, db=session)
            fetched = await router.rpc_call(
                Widget, "fetch", {"id": created["id"]}, db=session
            )
            assert fetched["id"] == created["id"]
    finally:
        raw_eng.dispose()
