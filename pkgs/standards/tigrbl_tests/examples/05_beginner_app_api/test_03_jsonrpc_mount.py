from tigrbl import Base, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


def test_jsonrpc_mount_adds_rpc_prefix():
    """Ensure JSON-RPC endpoints are mounted at the requested prefix.

    Purpose: demonstrate how RPC endpoints are exposed alongside REST routes.

    Best practice: keep RPC prefixes explicit to avoid collisions with REST
    paths and to make integrations predictable.
    """

    # Setup: define a widget model and API instance.
    class Widget(Base, GUIDPk):
        __tablename__ = "lessonrpc"
        __allow_unmapped__ = True
        name = Column(String, nullable=False)

    router = TigrblApp(engine=mem(async_=False))
    # Deployment: include the model and initialize before mounting JSON-RPC.
    router.include_model(Widget)
    router.initialize()
    router.mount_jsonrpc(prefix="/rpc")
    # Exercise: collect route paths after mounting RPC routes.
    route_paths = {route.path for route in router.router.routes}
    # Assertion: the RPC prefix is registered.
    assert "/rpc" in route_paths


def test_jsonrpc_mount_preserves_existing_routes():
    """Show that adding JSON-RPC does not remove existing routes.

    Purpose: verify that the router grows instead of replacing existing model
    endpoints when JSON-RPC is enabled.

    Best practice: measure route count before and after mutation to detect
    unexpected side effects.
    """

    # Setup: define a new widget model and API instance.
    class Widget(Base, GUIDPk):
        __tablename__ = "lessonrpcexisting"
        __allow_unmapped__ = True
        name = Column(String, nullable=False)

    router = TigrblApp(engine=mem(async_=False))
    # Deployment: include the model and initialize routes.
    router.include_model(Widget)
    router.initialize()
    # Exercise: capture routes before enabling JSON-RPC.
    initial_routes = {route.path for route in router.router.routes}
    router.mount_jsonrpc(prefix="/rpc")
    # Exercise: capture the expanded route set after mounting.
    updated_routes = {route.path for route in router.router.routes}

    # Assertion: existing routes remain available after adding JSON-RPC.
    assert initial_routes.issubset(updated_routes)
