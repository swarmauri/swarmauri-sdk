from __future__ import annotations

from types import SimpleNamespace

import pytest


@pytest.mark.asyncio
async def test_canonical_and_custom_resolution_targets():
    from tigrbl.op.types import OpSpec
    from tigrbl.transport.dispatcher import resolve_operation

    class DemoModel:
        pass

    read_spec = OpSpec(alias="read", target="read")
    custom_spec = OpSpec(alias="sync_profile", target="custom")
    DemoModel.ops = SimpleNamespace(
        by_alias={
            "read": (read_spec,),
            "sync_profile": (custom_spec,),
        }
    )

    api = SimpleNamespace(models={"DemoModel": DemoModel})

    read = resolve_operation(api=api, model_or_name="DemoModel", alias="read")
    custom = resolve_operation(
        api=api,
        model_or_name="DemoModel",
        alias="sync_profile",
    )

    assert read.target == "read"
    assert custom.target == "custom"


@pytest.mark.asyncio
async def test_rest_and_rpc_paths_execute_same_handler_once():
    from tigrbl.bindings.rpc import register_and_attach
    from tigrbl.op.types import OpSpec
    from tigrbl.transport.dispatcher import dispatch_operation

    events: list[str] = []

    async def read_handler(ctx):
        events.append(f"{ctx.target}:{ctx.op}")
        return {"path": "handler", "alias": ctx.op, "target": ctx.target}

    setattr(read_handler, "__tigrbl_label", "handler:read")

    class DemoModel:
        pass

    read_spec = OpSpec(alias="read", target="read")
    DemoModel.ops = SimpleNamespace(by_alias={"read": (read_spec,)})
    DemoModel.hooks = SimpleNamespace(
        read=SimpleNamespace(
            START_TX=[],
            PRE_TX_BEGIN=[],
            PRE_HANDLER=[],
            HANDLER=[read_handler],
            POST_HANDLER=[],
            PRE_COMMIT=[],
            END_TX=[],
            POST_RESPONSE=[],
            ON_ERROR=[],
            ON_SUCCESS=[],
        )
    )
    DemoModel.schemas = SimpleNamespace()

    register_and_attach(DemoModel, (read_spec,))

    api = SimpleNamespace(models={"DemoModel": DemoModel})

    class DummyDB:
        def commit(self):
            return None

        def flush(self):
            return None

        def rollback(self):
            return None

    db = DummyDB()

    rest_result = await dispatch_operation(
        api=api,
        model_or_name=DemoModel,
        alias="read",
        payload={"id": 1},
        db=db,
        request=None,
        ctx={},
        rpc_mode=False,
    )

    rpc_result = await DemoModel.rpc.read(
        {"id": 1},
        db=db,
        request=None,
        ctx={},
    )

    assert rest_result["path"] == "handler"
    assert rpc_result["path"] == "handler"
    assert events == ["read:read", "read:read"]


def test_rest_and_jsonrpc_resolution_map_to_same_model_alias_pairs():
    from tigrbl import TigrblApp
    from tigrbl.engine.shortcuts import mem
    from tigrbl.orm.tables import Base
    from tigrbl.orm.mixins import GUIDPk
    from sqlalchemy import Column, String

    class DemoItem(Base, GUIDPk):
        __tablename__ = "resolution_parity_demo_item"
        name = Column(String, nullable=False)

    app = TigrblApp(engine=mem(async_=False))
    app.include_model(DemoItem)
    app.initialize()
    app.mount_jsonrpc()

    rest_pairs = {
        (route.name.split(".", 1)[0], route.name.split(".", 1)[1]): route.path_template
        for route in app.routers["DemoItem"].routes
        if route.name.startswith("DemoItem.")
    }
    rpc_pairs = {
        ("DemoItem", method["name"].split(".", 1)[1])
        for method in app.openrpc()["methods"]
        if method["name"].startswith("DemoItem.")
    }

    assert rest_pairs, "expected REST routes for DemoItem"
    assert rpc_pairs, "expected RPC methods for DemoItem"
    # Every RPC op should resolve to a model+alias pair that REST also registers.
    assert rpc_pairs.issubset(set(rest_pairs))
