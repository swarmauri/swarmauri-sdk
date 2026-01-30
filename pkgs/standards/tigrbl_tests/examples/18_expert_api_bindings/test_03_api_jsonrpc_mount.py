"""Lesson 18: JSON-RPC mounting on APIs.

This lesson shows how the API exposes a JSON-RPC router that can be mounted on
an application. Keeping the router attached to the API instance is the
preferred pattern because it preserves routing metadata alongside model
configuration.
"""

from tigrbl import Base, TigrblApi
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


def test_api_binding_mounts_jsonrpc_router():
    """mount_jsonrpc returns a router ready to be attached to an app."""

    class LessonApiJsonrpc(Base, GUIDPk):
        __tablename__ = "lessonapijsonrpcs"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    Widget = LessonApiJsonrpc
    api = TigrblApi(engine=mem(async_=False))
    api.include_model(Widget)

    router = api.mount_jsonrpc()

    assert router is not None


def test_jsonrpc_mount_uses_configured_prefix():
    """The JSON-RPC prefix on the API should be configurable."""

    class LessonApiJsonrpcPrefix(Base, GUIDPk):
        __tablename__ = "lessonapijsonrpcprefixs"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    Widget = LessonApiJsonrpcPrefix
    api = TigrblApi(engine=mem(async_=False), jsonrpc_prefix="/rpc-demo")
    api.include_model(Widget)

    router = api.mount_jsonrpc()

    assert router is not None
