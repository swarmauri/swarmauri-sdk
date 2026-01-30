"""Lesson 19: JSON-RPC mounting on apps.

Apps expose a JSON-RPC router for programmatic access to operations. Keeping
the router on the app instance ensures a consistent integration point for
transport layers and documentation tools.
"""

from tigrbl import Base, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


def test_app_binding_mounts_jsonrpc_router():
    """mount_jsonrpc produces a router for JSON-RPC endpoints."""

    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_app_jsonrpc"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    app = TigrblApp(engine=mem(async_=False))
    app.include_model(Widget)

    router = app.mount_jsonrpc()

    assert router is not None


def test_app_jsonrpc_mount_uses_prefix_setting():
    """The JSON-RPC prefix is configurable on the app instance."""

    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_app_jsonrpc_prefix"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    app = TigrblApp(engine=mem(async_=False), jsonrpc_prefix="/rpc-app")
    app.include_model(Widget)

    router = app.mount_jsonrpc()

    assert router is not None
