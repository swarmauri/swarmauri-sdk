from __future__ import annotations
import pytest
from autoapi.v3 import alias_ctx
from autoapi.v3.response import response_ctx
from autoapi.v3.orm.mixins import GUIDPk
from autoapi.v3.orm.tables import Base
from autoapi.v3.specs import IO, S, F, acol as spec_acol
from autoapi.v3.types import Session, String
from autoapi.v3.autoapi import AutoAPI
from autoapi.v3.engine.shortcuts import mem


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

    api = AutoAPI(engine=mem(async_=False))
    api.include_model(Widget, mount_router=False)
    api.initialize_sync()

    _, SessionLocal = api.engine.raw()
    session: Session = SessionLocal()
    try:
        created = await api.rpc_call(Widget, "create", {"name": "a"}, db=session)
        fetched = await api.rpc_call(Widget, "fetch", {"id": created["id"]}, db=session)
        assert fetched["id"] == created["id"]
    finally:
        session.close()
